# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT INCLUDE BLOCKS FOR IBM PROVIDER
# This is a root level terragrunt file that contains common blocks for configuring the IBM terraform
# provider.
# ---------------------------------------------------------------------------------------------------------------------

locals {
  vars   = read_terragrunt_config(find_in_parent_folders("variables-terragrunt.hcl"))
  region = local.vars.locals.region
}

generate "provider" {
  path      = "provider-ibm.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key  #pragma: allowlist secret
  region           = "${local.region}"
}
EOF
}
