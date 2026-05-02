##############################################################################
# Main Infrastructure Configuration
# This file orchestrates all infrastructure components for the AI application.
##############################################################################

##############################################################################
# Resource Group
# Creates a logical container for organizing all IBM Cloud resources.
##############################################################################

module "resource_group" {
  source              = "terraform-ibm-modules/resource-group/ibm"
  version             = "1.6.0"
  resource_group_name = "${var.prefix}-resource-group"
}

##############################################################################
# Code Engine Project
# Creates a serverless container platform to host the AI application.
##############################################################################

module "code_engine_project" {
  source            = "terraform-ibm-modules/code-engine/ibm//modules/project"
  version           = "4.9.1"
  name              = "${var.prefix}-ce-project"
  resource_group_id = module.resource_group.resource_group_id
}

##############################################################################
# Code Engine Secret
# Creates credentials for Code Engine to push/pull images from IBM Container Registry.
##############################################################################

module "code_engine_secret" {
  source     = "terraform-ibm-modules/code-engine/ibm//modules/secret"
  version    = "4.9.1"
  name       = "${var.prefix}-registry-access-secret"
  project_id = module.code_engine_project.id
  format     = "registry"
  data = {
    "server"   = "private.us.icr.io",
    "username" = "iamapikey",
    "password" = var.ibmcloud_api_key,
  }
}

##############################################################################
# Container Registry Namespace
# Creates a namespace in IBM Container Registry to store container images.
##############################################################################

module "namespace" {
  source            = "terraform-ibm-modules/container-registry/ibm"
  version           = "2.7.1"
  namespace_name    = "${var.prefix}-crn"
  resource_group_id = module.resource_group.resource_group_id
}

##############################################################################
# Local Variables for Container Image Path
##############################################################################

locals {
  # Path where the built container image will be stored
  output_image = "private.us.icr.io/${module.namespace.namespace_name}/ai-agent-for-loan-risk"
}

##############################################################################
# Code Engine Build
# Builds a container image from the AI application source code on GitHub.
# The build uses the Dockerfile in the repository and pushes the image to Container Registry.
##############################################################################

module "code_engine_build" {
  source                     = "terraform-ibm-modules/code-engine/ibm//modules/build"
  version                    = "4.9.1"
  name                       = "${var.prefix}-ce-build"
  ibmcloud_api_key           = var.ibmcloud_api_key
  project_id                 = module.code_engine_project.id
  existing_resource_group_id = module.resource_group.resource_group_id
  source_url                 = "https://github.com/terraform-ibm-modules/sample-iac-solutions/tree/main/secure-infra-ai-app/ai-app-for-loan-risk" # AI application source code
  strategy_type              = "dockerfile"                                                                                                       # Build using Dockerfile
  output_secret              = module.code_engine_secret.name                                                                                     # Registry credentials
  output_image               = local.output_image                                                                                                 # Where to push the image
}

##############################################################################
# Local Variables for Encryption Keys
##############################################################################

locals {
  key_ring_name = "${var.prefix}-cos-key-ring" # Key ring for organizing encryption keys
  key_name      = "${var.prefix}-cos-key"      # Customer-managed encryption key
}

##############################################################################
# Key Protect and Customer-Managed Encryption Keys
# Creates IBM Key Protect service with key ring and customer-managed encryption keys.
##############################################################################

module "key_protect_all_inclusive" {
  source                    = "terraform-ibm-modules/kms-all-inclusive/ibm"
  version                   = "5.6.3"
  key_protect_instance_name = "${var.prefix}-kp"
  resource_group_id         = module.resource_group.resource_group_id
  enable_metrics            = false
  region                    = var.region
  keys = [
    {
      key_ring_name = (local.key_ring_name)
      keys = [
        {
          key_name = (local.key_name) # Root key for encrypting COS and watsonx.ai
        }
      ]
    }
  ]
  resource_tags = ["tutorial-tag"]
}

##############################################################################
# Cloud Object Storage with Key Protect Encryption
# Creates COS instance and bucket with customer-managed encryption.
##############################################################################

module "cos" {
  source                     = "terraform-ibm-modules/cos/ibm"
  version                    = "10.16.0"
  resource_group_id          = module.resource_group.resource_group_id
  region                     = var.region
  cos_instance_name          = "${var.prefix}-my-cos"
  cos_plan                   = "standard"
  bucket_name                = "${var.prefix}-bucket"
  kms_encryption_enabled     = true                                                                                  # Enable encryption
  existing_kms_instance_guid = module.key_protect_all_inclusive.kms_guid                                             # Key Protect instance
  kms_key_crn                = module.key_protect_all_inclusive.keys["${local.key_ring_name}.${local.key_name}"].crn # Encryption key
}

##############################################################################
# IAM Authentication Token for REST API Provider
# Required by watsonx.ai module for API calls
##############################################################################

data "ibm_iam_auth_token" "restapi" {
}

##############################################################################
# watsonx.ai Project
# Creates a watsonx.ai project with encrypted storage for AI workloads.
##############################################################################

module "watsonx_ai" {
  source                        = "terraform-ibm-modules/watsonx-ai/ibm"
  version                       = "2.17.1"
  region                        = var.region
  resource_group_id             = module.resource_group.resource_group_id
  watsonx_ai_studio_plan        = "professional-v1"
  watsonx_ai_runtime_plan       = "v2-professional"
  project_name                  = "${var.prefix}-wxai-project"
  enable_cos_kms_encryption     = true # Enable encryption for project data
  cos_instance_crn              = module.cos.cos_instance_crn
  cos_kms_key_crn               = module.key_protect_all_inclusive.keys["${local.key_ring_name}.${local.key_name}"].crn
  skip_iam_authorization_policy = true
}

##############################################################################
# Code Engine Application
# Deploys the containerized AI application as a serverless workload.
##############################################################################

module "code_engine_app" {
  depends_on      = [module.code_engine_build] # Wait for image to be built
  source          = "terraform-ibm-modules/code-engine/ibm//modules/app"
  version         = "4.9.1"
  project_id      = module.code_engine_project.id
  name            = "${var.prefix}-ai-agent-for-loan-risk"
  image_reference = module.code_engine_build.output_image # Use the built container image
  image_secret    = module.code_engine_secret.name        # Registry credentials

  # Environment variables for the application
  run_env_variables = [{
    type = "literal"
    name = "WATSONX_AI_APIKEY"
    # Use dedicated watsonx API key if provided, otherwise use IBM Cloud API key
    value = var.watsonx_ai_api_key != null ? var.watsonx_ai_api_key : var.ibmcloud_api_key
    },
    {
      type  = "literal"
      name  = "WATSONX_PROJECT_ID"
      value = module.watsonx_ai.watsonx_ai_project_id # Connect app to watsonx.ai project
    }
  ]
}
