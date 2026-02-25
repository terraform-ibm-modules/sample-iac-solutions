terraform {
  required_version = ">= 1.9.0"
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.80.4"
    }
    restapi = {
      source  = "Mastercard/restapi"
      version = ">= 1.19.1"
    }
  }
}