# Example : Use existing Terraform IBM Modules (TIM) to create Watson Discovery instance

"""
In order to use a Terraform module in Pulumi, first add it to your project using the `pulumi package add` command. Refer [here](https://www.pulumi.com/docs/iac/guides/building-extending/using-existing-tools/use-terraform-module/) for more information.
  pulumi package add terraform-module <module-source> [<version>] <pulumi-package-name>

This will generate a local SDK which can be imported in the Pulumi program. So, the Watson discovery and resource group packages can be added as:
  pulumi package add terraform-module terraform-ibm-modules/watsonx-discovery/ibm 1.11.1 wx_discovery
  pulumi package add terraform-module terraform-ibm-modules/resource-group/ibm 1.4.6 ibm_rg_module
"""

import pulumi_ibm_rg_module as rgmod
import pulumi_wx_discovery as wxd_mod

import pulumi

config = pulumi.Config()

# Create Resource group or use existing RG if exists

# Set this to an existing resource group name to use it, or None to create a new one
EXISTING_RESOURCE_GROUP = "Default"

# Resource Group
if EXISTING_RESOURCE_GROUP:
    rg = rgmod.Module(
        "resource_group", existing_resource_group_name=EXISTING_RESOURCE_GROUP
    )
    resource_group_id = None  # Will be looked up by name in watsonx module
else:
    rg = rgmod.Module("resource_group", resource_group_name=f"{PREFIX}-resource-group")
    resource_group_id = rg.resource_group_id

wxd = wxd_mod.Module(
    "my-wxd-resource",
    resource_group_id=rg.resource_group_id,  # config.get("resource-group"),
    watson_discovery_name="my-wxd",
)

# Show outputs
pulumi.export("account_id", wxd.account_id)
pulumi.export("wxd_id", wxd.id)
pulumi.export("crn", wxd.crn)
pulumi.export("plan_id", wxd.plan_id)
pulumi.export("dashboard_url", wxd.dashboard_url)
