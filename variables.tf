variable "ibmcloud_api_key" {
  type        = string
  description = "The IBM Cloud API key."
  sensitive   = true
}

variable "prefix" {
  type        = string
  description = "The prefix to be added to all resources name created by this solution."
}

variable "region" {
  type        = string
  description = "IBM Cloud region where resources will be deployed"
  default     = "us-south"
}