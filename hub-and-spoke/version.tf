terraform {
  required_version = ">= 1.9.0"
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.80.4"
    }

    tls = {
      source  = "hashicorp/tls"
      version = "4.2.1"
    }

    local = {
      source  = "hashicorp/local"
      version = ">= 2.5.0"
    }
  }
}
