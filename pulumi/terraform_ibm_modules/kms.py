# ----------------------------------------------------------------------------------------------------
# Required Pulumi packages:
#   - IBM Cloud KMS All Inclusive module:
#       pulumi package add terraform-module terraform-ibm-modules/kms-all-inclusive/ibm 5.5.5 ibm_kms_module
# ----------------------------------------------------------------------------------------------------

import pulumi_ibm_kms_module as ibm_kms_module
from config import KMS_KEYS, PREFIX, REGION
from constants import KP_NAME


def create_kms_instance(rg):
    """Create Key Protect Instance which can be used for Encrypting COS buckets."""
    return ibm_kms_module.Module(
        "pulumi-key-protect",
        resource_group_id=rg.resource_group_id,
        key_protect_instance_name=f"{PREFIX}-{KP_NAME}",
        region=REGION,
        keys=[KMS_KEYS],
    )
