##############################################################################
# Input Variables
# These variables allow you to customize the deployment without modifying
# the main configuration. Set values in terraform.tfvars file.
##############################################################################

##############################################################################
# Required Variables (must be provided in terraform.tfvars)
##############################################################################

variable "ibmcloud_api_key" {
  type        = string
  description = "The IBM Cloud API key."
  sensitive   = true # Prevents value from appearing in logs
}

variable "prefix" {
  type        = string
  description = "The prefix to be added to all resources name created by this solution."
  # Example: prefix "myapp" will create resources like "myapp-resource-group", "myapp-ce-project", etc.
}

##############################################################################
# Optional Variables (have default values)
##############################################################################

variable "watsonx_ai_api_key" {
  type        = string
  description = "The API key for IBM watsonx in the target account. If this key is not provided, the IBM Cloud API key will be used instead."
  sensitive   = true
  default     = null # If null, ibmcloud_api_key will be used for watsonx.ai
}

variable "region" {
  type        = string
  description = "The IBM Cloud region to deploy resources in."
  default     = "us-south" # Change to your preferred region (e.g., "eu-de", "jp-tok")
}

variable "cr_retention_images_per_repo" {
  type        = number
  description = "(Optional, Integer) Determines how many images are retained in each repository when the retention policy is processed. The value -1 denotes Unlimited (all images are retained). The value 0 denotes no retention policy will be created (default). For more details, refer [here](https://registry.terraform.io/providers/IBM-Cloud/ibm/latest/docs/resources/cr_retention_policy)."
  default     = 1
}
