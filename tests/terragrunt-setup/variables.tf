variable "ibmcloud_api_key" {
  type        = string
  description = "The IBM Cloud API Key."
  sensitive   = true
}

variable "region" {
  type        = string
  description = "Region to provision all resources created by this example."
  default     = "us-south"
}


variable "install_terragrunt" {
  type        = bool
  description = "Set to true to automatically install terragrunt. Set to false if terragrunt is already available in the environment."
  default     = true
}
