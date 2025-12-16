# ---------------------------------------------------------------------------------------------------------------------
# TERRAGRUNT SCAFFOLD VARIABLES
# This terragrunt file contains some base-level variables to be included to all modules, including any variables
# needed for provider configuration that would not exist in the root modules themselves.
# ---------------------------------------------------------------------------------------------------------------------


locals {
  prefix = "ocp-tg"
  region = "eu-de"
}

generate "variables" {
  path      = "variables-terragrunt.tf"
  if_exists = "overwrite"
  contents  = <<EOF
variable "ibmcloud_api_key" {
  description = "The IBM Cloud api token."
  type        = string
  sensitive   = true
}
EOF
}
