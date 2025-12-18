# Example : VPC with Subnets and Security Groups

import pulumi_ibm as ibm

import pulumi

config = pulumi.Config()

# Create a VPC
vpc = ibm.IsVpc(
    "my-vpc",
    name="my-development-vpc",
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

# Create a security group
security_group = ibm.IsSecurityGroup(
    "my-security-group",
    vpc=vpc.is_vpc_id,
)

# Create Security Group Rules

sg_rule_1 = ibm.IsSecurityGroupRule(
    "my-sg-rule1",
    group=security_group.is_security_group_id,
    direction="inbound",
    remote="127.0.0.1",
    icmp={
        "code": 20,
        "type": 30,
    },
)

sg_rule_2 = ibm.IsSecurityGroupRule(
    "my-sg-rule2",
    group=security_group.is_security_group_id,
    direction="inbound",
    remote="127.0.0.1",
    udp={
        "port_min": 805,
        "port_max": 807,
    },
)

sg_rule_3 = ibm.IsSecurityGroupRule(
    "my-sg-rule3",
    group=security_group.is_security_group_id,
    direction="outbound",
    remote="127.0.0.1",
    tcp={
        "port_min": 8080,
        "port_max": 8080,
    },
)

# Output VPC details
pulumi.export("vpc_id", vpc.id)
pulumi.export("vpc_name", vpc.name)
pulumi.export("address_prefix", vpc_address_prefix.id)
pulumi.export("subnet_id", vpc_subnet.id)
pulumi.export("security_group_id", security_group.id)
