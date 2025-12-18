# ----------------------------------------------------------------------------------------------------
# Pulumi Program: Provision IBM Cloud Object Storage (COS) instance & buckets
#                 and Watson Discovery instance using terraform-ibm-modules.
#
# Required Pulumi packages:
#   - IBM provider package
#       pulumi package add terraform-provider ibm-cloud/ibm
#
#   - IBM Cloud KMS All Inclusive module:
#       pulumi package add terraform-module terraform-ibm-modules/kms-all-inclusive/ibm 5.5.5 ibm_kms_module
#
#   - IBM Cloud Object Storage module:
#       pulumi package add terraform-module terraform-ibm-modules/cos/ibm 10.7.2 ibm_cos_module
#
#   - IBM Cloud Resource Group module:
#       pulumi package add terraform-module terraform-ibm-modules/resource-group/ibm 1.4.6 ibm_rg_module
#
#   - IBM Cloud Watson Discovery module:
#       pulumi package add terraform-module terraform-ibm-modules/watsonx-discovery/ibm 1.12.0 wx_discovery
# ----------------------------------------------------------------------------------------------------


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
    cos, bucket_name = create_cos_instance(rg, kms_instance)
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
        cos.bucket_crn.apply(
            lambda crn: f"https://{bucket_name}.s3.us-south.cloud-object-storage.appdomain.cloud"
        ),
    )
    pulumi.export("watson_discovery_id", watson_discovery.id)
    pulumi.export("watson_discovery_dashboard", watson_discovery.dashboard_url)


if __name__ == "__main__":
    main()
