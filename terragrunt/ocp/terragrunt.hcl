terraform {
  source = "git::https://github.com/terraform-ibm-modules/terraform-ibm-base-ocp-vpc.git?ref=v3.78.5"
}

include "ibm_provider" {
  path = find_in_parent_folders("ibm-provider.hcl")
}

include "variables" {
  path   = find_in_parent_folders("variables-terragrunt.hcl")
  expose = true
}

dependency "resource_group" {
  config_path = "../resource_group"

  # Permit planning before the resource group is created.
  mock_outputs = {
    resource_group_id = "00000000-0000-0000-0000-000000000000"
  }
  # Shallow merge: prefer real state where available, use mock only if missing.
  mock_outputs_merge_strategy_with_state = "shallow"
}

dependency "vpc" {
  config_path = "../vpc"

  # Permit planning before the VPC is created.
  mock_outputs = {
    vpc_id            = "00000000-0000-0000-0000-000000000000"
    subnet_detail_map = {
      "zone-1" = [
        {
          id         = "subnet-mock-0001"
          zone       = "us-south-1"
          cidr_block = "10.10.10.0/24"
          crn        = "crn:v1:bluemix:public:is:us-south:a/1234567890abcdef::subnet:subnet-mock-0001"
        }
      ]
    }
  }
  # Shallow merge: prefer real state where available, use mock only if missing.
  mock_outputs_merge_strategy_with_state = "shallow"
}

locals {
  prefix = include.variables.locals.prefix
  region = include.variables.locals.region
}

inputs = {
  cluster_name = local.prefix

  region            = local.region
  resource_group_id = dependency.resource_group.outputs.resource_group_id

  vpc_id      = dependency.vpc.outputs.vpc_id
  vpc_subnets = dependency.vpc.outputs.subnet_detail_map

  force_delete_storage = true

  worker_pools = [
    {
      subnet_prefix    = "zone-1"
      pool_name        = "default"
      machine_type     = "bx2.8x32"
      operating_system = "RHCOS"
      workers_per_zone = 2
    }
  ]
  enable_addons   = false
  ocp_version     = null
  ocp_entitlement = null
  resource_tags   = []
  access_tags     = []

  disable_outbound_traffic_protection = true
}
