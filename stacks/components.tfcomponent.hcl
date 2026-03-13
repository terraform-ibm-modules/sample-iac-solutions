component "resource_group" {
  source  = "terraform-ibm-modules/resource-group/ibm"
  version = "1.4.8"
  inputs = {
    resource_group_name = "${var.prefix}-rg"
  }

  providers = {
    ibm = provider.ibm.this
  }
}

component "postgres" {
  source  = "terraform-ibm-modules/icd-postgresql/ibm"
  version = "4.10.10"

  inputs = {
    resource_group_id = component.resource_group.resource_group_id
    region            = var.region
    name              = "${var.prefix}-postgres"
    tags              = var.resource_tags
  }

  providers = {
    ibm      = provider.ibm.this
    time     = provider.time.this
    external = provider.external.this
  }
}
