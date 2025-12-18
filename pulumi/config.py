import pulumi

config = pulumi.Config()
REGION = config.get("region") or "us-south"
PREFIX = config.get("prefix") or "pulumi2"
ACCESS_GROUP = config.get("access_group")
EXISTING_RESOURCE_GROUP = config.get("resource_group")  # None if new


KMS_KEY_CONFIGURATION = {
    "key_name": "pulumi-key-for-cos",
    "standard_key": True,
    "rotation_interval_month": 4,
    "dual_auth_delete_enabled": True,
    "force_delete": True,
}

KMS_KEYS = {
    "key_ring_name": "pulumi-key-ring",
    "existing_key_ring": False,
    "keys": [KMS_KEY_CONFIGURATION],
}
