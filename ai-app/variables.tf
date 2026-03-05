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
  sensitive   = true  # Prevents value from appearing in logs
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
  default     = null  # If null, ibmcloud_api_key will be used for watsonx.ai
}

variable "region" {
  type        = string
  description = "The IBM Cloud region to deploy resources in."
  default     = "us-south"  # Change to your preferred region (e.g., "eu-de", "jp-tok")
}
