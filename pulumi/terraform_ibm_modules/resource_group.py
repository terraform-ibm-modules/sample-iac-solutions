import pulumi_ibm_rg_module as rgmod
from config import EXISTING_RESOURCE_GROUP, PREFIX

from .constants import RG_NAME


def create_resource_group():
    """Create or reference an IBM Cloud resource group."""
    if EXISTING_RESOURCE_GROUP:
        return rgmod.Module(
            "resource_group", existing_resource_group_name=EXISTING_RESOURCE_GROUP
        )
    return rgmod.Module("resource_group", resource_group_name=f"{PREFIX}-{RG_NAME}")
