# ----------------------------------------------------------------------------------------------------
# Required Pulumi packages:
#   - IBM Cloud Object Storage module:
#       pulumi package add terraform-module terraform-ibm-modules/cos/ibm 10.7.2 ibm_cos_module
# ----------------------------------------------------------------------------------------------------

import glob
import os

import pulumi_ibm as ibm
import pulumi_ibm_cos_module as cosmod
from config import PREFIX, REGION
from constants import (
    BUCKET_NAME,
    BUCKET_STORAGE_CLASS,
    BUCKET_TYPE,
    COS_INSTANCE_NAME,
    COS_SERVICE_NAME,
    KMS_KEY_NAME,
    KMS_KEY_RING_NAME,
    STATIC_DIR_NAME,
)
from utils import first_or_self, generate_suffix

import pulumi

STATIC_DIR = os.path.join(os.path.dirname(__file__), STATIC_DIR_NAME)


def create_cos_instance(rg, kms_instance):
    """Provision COS instance and bucket."""
    cos = cosmod.Module(
        "cos_instance_bucket",
        resource_group_id=rg.resource_group_id,
        region=REGION,
        cos_instance_name=f"{PREFIX}-{COS_INSTANCE_NAME}",
        bucket_name=f"{PREFIX}-{BUCKET_NAME}-{generate_suffix()}",
        create_cos_instance=True,
        create_cos_bucket=True,
        bucket_storage_class=BUCKET_STORAGE_CLASS,
        existing_kms_instance_guid=kms_instance.kms_guid,
        kms_key_crn=kms_instance.keys.apply(
            lambda keys: keys[f"{KMS_KEY_RING_NAME}.{KMS_KEY_NAME}"]["crn"]
        ),
    )

    return cos


def upload_static_files(cos):
    """Upload files from the static directory to the COS bucket."""

    if not os.path.isdir(STATIC_DIR):
        pulumi.log.warn(f"Static directory not found: {STATIC_DIR}")
        return

    for fname in glob.glob(os.path.join(STATIC_DIR, "*")):
        if os.path.isfile(fname):
            ibm.cos_bucket_object.CosBucketObject(
                f"file-{os.path.basename(fname)}",
                bucket_crn=cos.bucket_crn.apply(first_or_self),
                bucket_location=REGION,
                content_file=fname,
                key=os.path.basename(fname),
            )


def configure_bucket_website(cos):
    """Enable static website hosting on the COS bucket."""
    ibm.CosBucketWebsiteConfiguration(
        "website-config",
        bucket_crn=cos.bucket_crn.apply(first_or_self),
        bucket_location=REGION,
        website_configuration={
            "index_document": {"suffix": "index.html"},
            "error_document": {"key": "error.html"},
        },
    )


def configure_public_access(cos):
    """Grant public read access to the COS bucket."""

    # NOTE: If you want to use a different IAM access group, either change in pulumi config or override here.
    ACCESS_GROUP = "geretain-public-access"

    # Lookup the default 'Public Access' IAM access group
    public_access_group = ibm.get_iam_access_group(access_group_name=ACCESS_GROUP)

    # Grant public read access to the bucket
    ibm.IamAccessGroupPolicy(
        "cos-public-access-policy",
        access_group_id=public_access_group.groups[0].id,
        roles=["Object Reader"],
        resources={
            "service": COS_SERVICE_NAME,
            "resource_type": BUCKET_TYPE,
            "resource_instance_id": cos.cos_instance_guid.apply(first_or_self),
            "resource": cos.bucket_name.apply(first_or_self),
        },
    )
