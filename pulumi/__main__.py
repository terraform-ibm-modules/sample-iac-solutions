# ----------------------------------------------------------------------------------------------------
# Pulumi Program: Provision IBM Cloud Object Storage (COS) instance & buckets
#                 and Watson Discovery instance using terraform-ibm-modules.
#
# Required Pulumi packages:
#   - IBM provider package
#       pulumi package add terraform-provider ibm-cloud/ibm
# ----------------------------------------------------------------------------------------------------


from constants import COS_ENDPOINT
from terraform_ibm_modules.kms import create_kms_instance
from terraform_ibm_modules.object_storage import (
    configure_bucket_website,
    configure_public_access,
    create_cos_instance,
    upload_static_files,
)
from terraform_ibm_modules.resource_group import create_resource_group
from terraform_ibm_modules.watson_discovery import create_watson_discovery

import pulumi


def main():
    """Main method to provision resources."""

    rg = create_resource_group()
    kms_instance = create_kms_instance(rg)
    cos = create_cos_instance(rg, kms_instance)
    configure_public_access(cos)
    upload_static_files(cos)
    configure_bucket_website(cos)
    watson_discovery = create_watson_discovery(rg)

    # Export outputs
    pulumi.export("kms_instance_crn", kms_instance.key_protect_crn)
    pulumi.export("bucket_name", cos.bucket_name)
    pulumi.export("cos_instance_name", cos.cos_instance_name)
    pulumi.export(
        "website_endpoint",
        cos.bucket_crn.apply(lambda crn: f"https://{cos.bucket_name}.{COS_ENDPOINT}"),
    )
    pulumi.export("watson_discovery_id", watson_discovery.id)
    pulumi.export("watson_discovery_dashboard", watson_discovery.dashboard_url)


if __name__ == "__main__":
    main()
