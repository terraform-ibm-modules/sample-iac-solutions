EXISTING_RESOURCE_GROUP = (
    "Default"  # Change to None if want to create a new Resource Group.
)
NEW_RG_NAME = "new-rg"  # If want to create a new Resource Group EXISTING_RESOURCE_GROUP should be changed to None

# KMS Configuration
KP_NAME = "key-protect"
KMS_KEY_NAME = "pulumi-key-for-cos"
KMS_KEY_RING_NAME = "pulumi-key-ring"

COS_SERVICE_NAME = "cloud-object-storage"
COS_INSTANCE_NAME = "pulumi-cos"

BUCKET_STORAGE_CLASS = "standard"
BUCKET_NAME = "pulumi-bucket"
BUCKET_TYPE = "bucket"
COS_ENDPOINT = "s3.us-south.cloud-object-storage.appdomain.cloud"

STATIC_DIR_NAME = "static"

WATSON_DISCOVERY_NAME = "watson-discovery"
