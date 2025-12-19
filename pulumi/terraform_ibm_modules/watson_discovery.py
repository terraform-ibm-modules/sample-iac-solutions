# ----------------------------------------------------------------------------------------------------
# Required Pulumi packages:
#   - IBM Cloud Watson Discovery module:
#       pulumi package add terraform-module terraform-ibm-modules/watsonx-discovery/ibm 1.12.0 wx_discovery
# ----------------------------------------------------------------------------------------------------

import pulumi_wx_discovery as wxd_mod
from config import PREFIX
from constants import WATSON_DISCOVERY_NAME


def create_watson_discovery(rg):
    """Provision a Watson Discovery instance."""
    return wxd_mod.Module(
        WATSON_DISCOVERY_NAME,
        resource_group_id=rg.resource_group_id,
        watson_discovery_name=f"{PREFIX}-{WATSON_DISCOVERY_NAME}",
    )
