include "ibm_provider" {
  path = find_in_parent_folders("ibm-provider.hcl")
}

include "variables" {
  path   = find_in_parent_folders("variables-terragrunt.hcl")
  expose = true
}

terraform {
  source = "git::https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vpc.git?ref=v8.9.2"
}

dependency "resource_group" {
  config_path = "../resource_group"

  # Allow planning before resource group is applied by supplying placeholder outputs.
  mock_outputs = {
    resource_group_id = "00000000-0000-0000-0000-000000000000"
  }
  # Use shallow merge so real state wins where present; mocks fill gaps pre-apply.
  mock_outputs_merge_strategy_with_state = "shallow"
}

locals {
  prefix = include.variables.locals.prefix
  region = include.variables.locals.region
}

inputs = {
  name              = "vpc"
  prefix            = local.prefix
  region            = local.region
  resource_group_id = dependency.resource_group.outputs.resource_group_id

  subnets = {
    "zone-1" = [
      {
        name           = "${local.prefix}subnet"
        cidr           = "10.10.10.0/24"
        public_gateway = true
        acl_name       = "${local.prefix}acl"
      }
    ]
  }

  use_public_gateways = {
    "zone-1" = true
    "zone-2" = false
    "zone-3" = false
  }

  network_acls = [
    {
      name                         = "${local.prefix}acl"
      add_ibm_cloud_internal_rules = true
      add_vpc_connectivity_rules   = true
      prepend_ibm_rules            = true
      rules = [
        {
          name        = "${local.prefix}inbound"
          action      = "allow"
          source      = "0.0.0.0/0"
          destination = "0.0.0.0/0"
          direction   = "inbound"
        },
        {
          name        = "${local.prefix}outbound"
          action      = "allow"
          source      = "0.0.0.0/0"
          destination = "0.0.0.0/0"
          direction   = "outbound"
        }
      ]
    }
  ]
}
