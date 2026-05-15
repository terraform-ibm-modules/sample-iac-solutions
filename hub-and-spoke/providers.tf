provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.region
  # Increase default timeouts for VPC resources
  max_retries      = 10
  ibmcloud_timeout = 3600
