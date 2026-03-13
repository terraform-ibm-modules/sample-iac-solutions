

required_providers {
  ibm = {
    source  = "ibm-cloud/ibm"
    version = ">= 1.87.3"
  }
  time = {
    source  = "hashicorp/time"
    version = ">= 0.9.1, < 1.0.0"
  }
  external = {
    source  = "hashicorp/external"
    version = ">=2.3.5, <3.0.0"
  }
}

provider "ibm" "this" {
  config {
    ibmcloud_api_key = var.ibmcloud_api_key  # pragma: allowlist secret
    region           = var.region
  }
}

provider "time" "this" {
  config {
  }
}

provider "external" "this" {
  config {
  }
}
