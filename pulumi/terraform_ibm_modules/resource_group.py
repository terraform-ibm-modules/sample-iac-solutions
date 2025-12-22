# ----------------------------------------------------------------------------------------------------
# Required Pulumi packages:
#   - IBM Cloud Resource Group module:
#       pulumi package add terraform-module terraform-ibm-modules/resource-group/ibm 1.4.6 ibm_rg_module
# ----------------------------------------------------------------------------------------------------

import pulumi_ibm_rg_module as rgmod
from config import PREFIX
from constants import EXISTING_RESOURCE_GROUP, NEW_RG_NAME


def create_resource_group():
    """
    Create or reference an IBM Cloud resource group.
    The default value of Existing Resource Group is Default. If want to create a new resource group, set the EXISTING_RESOURCE_GROUP to None.
    The NEW_RG_NAME will be then used to create the new resource group.
    """
    if EXISTING_RESOURCE_GROUP:
        return rgmod.Module(
            "resource_group", existing_resource_group_name=EXISTING_RESOURCE_GROUP
        )
    else:
        return rgmod.Module(
            "resource_group", resource_group_name=f"{PREFIX}-{NEW_RG_NAME}"
        )
