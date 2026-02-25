module "resource_group" {
  source              = "terraform-ibm-modules/resource-group/ibm"
  version             = "1.4.0"
  resource_group_name = "${var.prefix}-resource-group"
}

module "code_engine_project" {
  source            = "terraform-ibm-modules/code-engine/ibm//modules/project"
  version           = "4.5.1"
  name              = "${var.prefix}-ce-project"
  resource_group_id = module.resource_group.resource_group_id
}

module "code_engine_secret" {
  source     = "terraform-ibm-modules/code-engine/ibm//modules/secret"
  version    = "4.5.1"
  name       = "${var.prefix}-registry-access-secret"
  project_id = module.code_engine_project.id
  format     = "registry"
  data = {
    "server"   = "private.us.icr.io",
    "username" = "iamapikey",
    "password" = var.ibmcloud_api_key,
  }
}

module "namespace" {
  source            = "terraform-ibm-modules/container-registry/ibm"
  version           = "2.3.5"
  namespace_name    = "${var.prefix}-crn"
  resource_group_id = module.resource_group.resource_group_id
}

locals {
  output_image = "private.us.icr.io/${module.namespace.namespace_name}/ai-agent-for-loan-risk"
}

module "code_engine_build" {
  source                     = "terraform-ibm-modules/code-engine/ibm//modules/build"
  version                    = "4.5.1"
  name                       = "${var.prefix}-ce-build"
  ibmcloud_api_key           = var.ibmcloud_api_key
  project_id                 = module.code_engine_project.id
  existing_resource_group_id = module.resource_group.resource_group_id
  source_url                 = "https://github.com/IBM/ai-agent-for-loan-risk"
  strategy_type              = "dockerfile"
  output_secret              = module.code_engine_secret.name
  output_image               = local.output_image
}

locals {
  key_ring_name = "${var.prefix}-cos-key-ring"
  key_name      = "${var.prefix}-cos-key"
}

module "key_protect_all_inclusive" {
  source                    = "terraform-ibm-modules/kms-all-inclusive/ibm"
  version                   = "5.5.5"
  key_protect_instance_name = "${var.prefix}-kp"
  resource_group_id         = module.resource_group.resource_group_id
  enable_metrics            = false
  region                    = var.region
  keys = [
    {
      key_ring_name = (local.key_ring_name)
      keys = [
        {
          key_name = (local.key_name)
        }
      ]
    }
  ]
  resource_tags = ["tutorial-tag"]
}

module "cos" {
  source  = "terraform-ibm-modules/cos/ibm"
  version = "10.7.2"
  resource_group_id = module.resource_group.resource_group_id
  region            = var.region
  cos_instance_name = "${var.prefix}-my-cos"
  cos_plan          = "standard"
  bucket_name       = "${var.prefix}-bucket"
  kms_encryption_enabled = true
  existing_kms_instance_guid = module.key_protect_all_inclusive.kms_guid
  kms_key_crn = module.key_protect_all_inclusive.keys["${local.key_ring_name}.${local.key_name}"].crn
}

data "ibm_iam_auth_token" "restapi" {
}

module "watsonx_ai" {
  source                    = "terraform-ibm-modules/watsonx-ai/ibm"
  version                   = "2.12.0"
  region                    = var.region
  resource_group_id         = module.resource_group.resource_group_id
  watsonx_ai_studio_plan    = "professional-v1"
  watsonx_ai_runtime_plan   = "v2-professional"
  project_name              = "${var.prefix}-wxai-project"
  enable_cos_kms_encryption = true
  cos_instance_crn          = module.cos.cos_instance_crn
  cos_kms_key_crn           = module.key_protect_all_inclusive.keys["${local.key_ring_name}.${local.key_name}"].crn
  skip_iam_authorization_policy = true
}

module "code_engine_app" {
  depends_on      = [ module.code_engine_build ]
  source          = "terraform-ibm-modules/code-engine/ibm//modules/app"
  version         = "4.5.1"
  project_id      = module.code_engine_project.id
  name            = "${var.prefix}-ai-agent-for-loan-risk"
  image_reference = module.code_engine_build.output_image
  image_secret    = module.code_engine_secret.name
  run_env_variables = [{
    type  = "literal"
    name  = "WATSONX_AI_APIKEY"
    value = var.watsonx_ai_api_key != null ? var.watsonx_ai_api_key : var.ibmcloud_api_key  # Uses watsonx API key if provided, otherwise falls back to IBM Cloud API key for LLM inferencing
    },
    {
      type  = "literal"
      name  = "WATSONX_PROJECT_ID"
      value = module.watsonx_ai.watsonx_ai_project_id
    }
  ]
}