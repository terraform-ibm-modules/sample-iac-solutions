variable "ibmcloud_api_key" {
  description = "IBM Cloud API key for authentication and resource provisioning"
  type        = string
  sensitive   = true
}

variable "prefix" {
  description = "Unique prefix for resource naming (e.g., 'vb-lab' or 'ra-dev'). Maximum prefix length is 6 characters."
  type        = string
}