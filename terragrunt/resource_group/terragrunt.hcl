include "ibm_provider" {
  path = find_in_parent_folders("ibm-provider.hcl")
}

include "variables" {
  path   = find_in_parent_folders("variables-terragrunt.hcl")
  expose = true
}

terraform {
  source = "git::https://github.com/terraform-ibm-modules/terraform-ibm-resource-group.git?ref=v1.4.0"
}

locals {
  prefix              = include.variables.locals.prefix
  resource_group_name = "${local.prefix}-rg"
}

inputs = {
  resource_group_name = local.resource_group_name
}
