# Example: Create Object Storage instance and buckets using terraform-ibm-modules/cos

# Import local SDKs as shown : 
# pulumi package add terraform-module terraform-ibm-modules/cos/ibm 10.1.14 ibm_cos_module
# pulumi package add terraform-module terraform-ibm-modules/resource-group/ibm 1.2.1 ibm_rg_module

import pulumi
import pulumi_ibm_rg_module as rgmod
import pulumi_ibm_cos_module as cosmod
import pulumi_ibm as ibm
import os
import random
import string
import glob
from pulumi_ibm import IamAccessGroupPolicy
from pulumi_ibm import CosBucketWebsiteConfiguration

REGION = "us-south"
PREFIX = "pulumi2"
API_KEY = os.getenv("IBMCLOUD_API_KEY")

# Set this to an existing resource group name to use it, or None to create a new one
EXISTING_RESOURCE_GROUP = "Default"  # or e.g. "Default"

# Resource Group
if EXISTING_RESOURCE_GROUP:
    rg = rgmod.Module(
        "resource_group",
        existing_resource_group_name=EXISTING_RESOURCE_GROUP
    )
    resource_group_id = None  # Will be looked up by name in COS module
else:
    rg = rgmod.Module(
        "resource_group",
        resource_group_name=f"{PREFIX}-resource-group"
    )
    resource_group_id = rg.resource_group_id

# Random 4-character suffix for bucket name
BUCKET_SUFFIX = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
BUCKET_NAME = f"{PREFIX}-web-bucket"
COS_INSTANCE_NAME = f"{PREFIX}-cos"

# COS Instance and Bucket
cos = cosmod.Module(
    "cos_instance_bucket",
    resource_group_id=rg.resource_group_id,
    region=REGION,
    cos_instance_name=COS_INSTANCE_NAME,
    bucket_name=BUCKET_NAME,
    create_cos_instance=True,
    create_cos_bucket=True,
    bucket_storage_class="standard",
    kms_encryption_enabled=False,
    retention_enabled=False,
    object_versioning_enabled=False,
    archive_days=None,
    expire_days=None,
    add_bucket_name_suffix=False  # We already add our own
)

# Upload files from static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    files = [os.path.basename(f) for f in glob.glob(os.path.join(STATIC_DIR, "*")) if os.path.isfile(f)]
    for fname in files:
        ibm.cos_bucket_object.CosBucketObject(
            f"file-{fname}",
            bucket_crn=cos.bucket_crn.apply(lambda crns: crns[0] if isinstance(crns, list) else crns),
            bucket_location=REGION,
            content_file=os.path.join(STATIC_DIR, fname),
            key=fname
        )
else:
    pulumi.log.warn(f"Static directory not found: {STATIC_DIR}")

# Lookup the 'Public Access' IAM access group
public_access_group = ibm.get_iam_access_group(
    access_group_name="Public Access"
)

# Grant public read access to the bucket
ibm.IamAccessGroupPolicy(
    "cos-public-access-policy",
    access_group_id=public_access_group.groups[0].id,
    roles=["Object Reader"],
    resources={
        "service": "cloud-object-storage",
        "resource_type": "bucket",
        "resource_instance_id": cos.cos_instance_guid.apply(lambda x: x[0] if isinstance(x, list) else x),
        "resource": cos.bucket_name.apply(lambda x: x[0] if isinstance(x, list) else x),
    }
)

# Configure the COS bucket for static web hosting
ibm.CosBucketWebsiteConfiguration(
    "website-config",
    bucket_crn=cos.bucket_crn.apply(lambda x: x[0] if isinstance(x, list) else x),
    bucket_location=REGION,
    website_configuration={
        "index_document": {"suffix": "index.html"},
        "error_document": {"key": "error.html"},
    }
)

# Export outputs
pulumi.export("bucket_name", cos.bucket_name)
pulumi.export("cos_instance_name", cos.cos_instance_name)
pulumi.export("website_endpoint", cos.bucket_crn.apply(lambda crn: f"https://{BUCKET_NAME}.s3.{REGION}.cloud-object-storage.appdomain.cloud"))
