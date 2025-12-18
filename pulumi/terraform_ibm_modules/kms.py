import pulumi_ibm_kms_module as ibm_kms_module
from config import KMS_KEYS, KP_NAME, PREFIX, REGION


def create_kms_instance(rg):
    """Create Key Protect Instance which can be used for Encrypting COS buckets."""
    return ibm_kms_module.Module(
        "pulumi-key-protect",
        resource_group_id=rg.resource_group_id,
        key_protect_instance_name=f"{PREFIX}-{KP_NAME}",
        region=REGION,
        keys=[KMS_KEYS],
    )
