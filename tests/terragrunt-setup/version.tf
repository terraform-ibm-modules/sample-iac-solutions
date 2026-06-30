
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    ibm = {
      source  = "ibm-cloud/ibm"
      version = ">= 1.79.0"
    }
    external = {
      source  = "hashicorp/external"
      version = ">=2.2.3"
    }
  }
}
