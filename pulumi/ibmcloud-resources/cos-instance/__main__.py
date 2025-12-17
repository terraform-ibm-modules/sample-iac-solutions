# Example : Simple Cloud Object Storage Instance


import pulumi
import pulumi_ibm as ibm

config = pulumi.Config()
resource_group = config.get("resource-group") or "Default"

# Create a Cloud Object Storage instance
cos_instance = ibm.ResourceInstance(
    "my-cos-instance",
    name="my-dev-cos-instance",
    service="cloud-object-storage",
    plan="lite",
    location="global",
    resource_group_id=resource_group,
    tags=["environment:dev", "managed-by:pulumi"]
)

# Create a COS bucket
cos_bucket = ibm.CosBucket(
    "my-bucket",
    bucket_name="my-unique-bucket-name",
    resource_instance_id=cos_instance.id,
    region_location="us-south",
    storage_class="standard",
    endpoint_type="public"
)

# Output the details
pulumi.export("bucket_name", cos_bucket.bucket_name)
pulumi.export("cos_instance_id", cos_instance.id)