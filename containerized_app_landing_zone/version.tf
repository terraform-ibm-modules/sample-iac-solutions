terraform {
  required_version = ">=1.9.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "3.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.14.0"
    }
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "2.2.2"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.1.2"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "3.1.0"
    }
  }
}
