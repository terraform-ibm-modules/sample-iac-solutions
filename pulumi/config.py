from constants import KMS_KEY_NAME, KMS_KEY_RING_NAME

import pulumi

config = pulumi.Config()
REGION = config.get("region") or "us-south"
PREFIX = config.get("prefix") or "pul-eg"
ACCESS_GROUP = config.get("access_group") or "Public Access"
EXISTING_RESOURCE_GROUP = config.get("resource_group") or "Default" # None if new

KMS_KEY_CONFIGURATION = {
    "key_name": KMS_KEY_NAME,
    "standard_key": True,
    "rotation_interval_month": 4,
    "dual_auth_delete_enabled": True,
    "force_delete": True,
}

KMS_KEYS = {
    "key_ring_name": KMS_KEY_RING_NAME,
    "existing_key_ring": False,
    "keys": [KMS_KEY_CONFIGURATION],
}
