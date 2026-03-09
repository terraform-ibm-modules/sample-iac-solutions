##############################################################################
# IBM Cloud Provider Configuration
##############################################################################

provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key  # Your IBM Cloud API key
  region           = var.region             # Target region
}

##############################################################################
# REST API Provider Configuration
##############################################################################

provider "restapi" {
  uri                  = "https:"  # Base URI for REST API calls
  write_returns_object = true      # Return full response object on write operations
  debug                = true      # Enable debug logging for troubleshooting
  headers = {
    # Use IAM token for authentication with IBM Cloud APIs
    Authorization = data.ibm_iam_auth_token.restapi.iam_access_token
    Content-Type  = "application/json"
  }
}
