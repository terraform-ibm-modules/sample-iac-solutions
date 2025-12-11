# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT INCLUDE BLOCKS FOR IBM PROVIDER
# This is a root level terragrunt file that contains common blocks for configuring the IBM terraform
# provider.
# ---------------------------------------------------------------------------------------------------------------------

generate "provider" {
  path      = "provider-ibm.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key  #pragma: allowlist secret
  region           = "us-south"
}
EOF
}
