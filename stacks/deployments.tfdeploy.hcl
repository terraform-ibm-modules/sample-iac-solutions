
store "varset" "ibm_credentials" {
  id       = "varset-7X1yJ4nwvovXU9MD"
  category = "terraform"
}

deployment "us-east" {
  inputs = {
    prefix           = "prefix1"
    region           = "us-east"
    resource_tags    = ["us-east"]
    ibmcloud_api_key = store.varset.ibm_credentials.ibmcloud_api_key
  }
}

deployment "ca-tor" {
  inputs = {
    prefix           = "prefix2"
    region           = "ca-tor"
    resource_tags    = ["ca-tor"]
    ibmcloud_api_key = store.varset.ibm_credentials.ibmcloud_api_key
  }
}
