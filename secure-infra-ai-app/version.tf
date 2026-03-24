##############################################################################
# Terraform Version Constraints
##############################################################################

terraform {
  required_version = ">= 1.9.0" # Minimum Terraform version required

  required_providers {
    # IBM Cloud provider for managing IBM Cloud resources
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.80.4"
    }

    # REST API provider for making API calls to IBM Cloud services
    restapi = {
      source  = "Mastercard/restapi"
      version = ">= 1.19.1"
    }
  }
}
