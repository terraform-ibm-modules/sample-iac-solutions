terraform {
  required_version = ">=1.9.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "3.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.13.1"
    }
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "1.89.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.1.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "3.0.1"
    }
  }
}
