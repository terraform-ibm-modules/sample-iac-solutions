include "ibm_provider" {
  path = find_in_parent_folders("ibm-provider.hcl")
}

include "variables" {
  path = find_in_parent_folders("variables-terragrunt.hcl")
}

terraform {
  source = "git::https://github.com/terraform-ibm-modules/terraform-ibm-resource-group.git?ref=v1.4.0"
}

locals {
  resource_group_name = "tg-rg"
}

inputs = {
  resource_group_name = local.resource_group_name
}
