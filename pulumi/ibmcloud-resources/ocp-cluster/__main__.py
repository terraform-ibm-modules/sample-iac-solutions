# Example : Red Hat OpenShift Cluster with a default worker pool with one worker node.

import pulumi_ibm as ibm

import pulumi

config = pulumi.Config()

# Create a VPC

vpc = ibm.IsVpc(
    "my-vpc",
    name="gen2-vpc",
    resource_group=config.get("resource-group"),
    tags=["environment:dev"],
)

# Create an address prefix
vpc_address_prefix = ibm.IsVpcAddressPrefix(
    "my-address-prefix", cidr="10.0.1.0/24", vpc=vpc.is_vpc_id, zone="us-south-1"
)

# Create a subnet
vpc_subnet = ibm.IsSubnet(
    "my-subnet",
    ipv4_cidr_block="10.0.1.0/24",
    vpc=vpc.is_vpc_id,
    zone="us-south-1",
    opts=pulumi.ResourceOptions(depends_on=[vpc_address_prefix]),
)

# Create a COS instance
cos_instance = ibm.ResourceInstance(
    "cosInstance", service="cloud-object-storage", plan="standard", location="global"
)

# Create an OCP Cluster
cluster = ibm.ContainerVpcCluster(
    "my-ocp-cluster",
    vpc_id=vpc.is_vpc_id,
    kube_version="4.18.24_openshift",
    flavor="bx2.16x64",
    worker_count=2,
    entitlement="cloud_pak",
    cos_instance_crn=cos_instance.resource_instance_id,
    resource_group_id=config.get("resource-group"),
    zones=[
        {
            "subnet_id": vpc_subnet.id,
            "name": "us-south-1",
        }
    ],
)

# Outputs
pulumi.export("vpc_id", vpc.id)
pulumi.export("vpc_name", vpc.name)
pulumi.export("subnet_id", vpc_subnet.id)
pulumi.export("ocp_cluster_id", cluster.id)
