terraform {
  required_version = ">=1.9.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = ">= 3.0.0, < 4.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.14.1"
    }
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "2.5.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "3.2.1"
    }
  }
}
