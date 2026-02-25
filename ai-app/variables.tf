variable "ibmcloud_api_key" {
  type        = string
  description = "The IBM Cloud API key."
  sensitive   = true
}

variable "watsonx_ai_api_key" {
  type        = string
  description = "The API key for IBM watsonx in the target account. If this key is not provided, the IBM Cloud API key will be used instead."
  sensitive   = true
  default     = null
}

variable "prefix" {
  type        = string
  description = "The prefix to be added to all resources name created by this solution."
}

variable "region" {
  type        = string
  description = "The IBM Cloud region to deploy resources in."
  default     = "us-south"
}