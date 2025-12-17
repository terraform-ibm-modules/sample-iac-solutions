# Deploying a single zone Red Hat Openshift Cluster in a Virtual Private Cloud using Terragrunt

This solution provides an opinionated, Terragrunt-based framework for deploying IBM Cloud infrastructure using Terraform IBM Cloud modules. The configuration automates the provisioning of the foundational cloud components required to run Red Hat OpenShift on IBM Cloud VPC, ensuring consistency, repeatability, and modular infrastructure design.

Terragrunt is used to orchestrate module dependencies, manage shared provider settings, enforce variable inheritance, and structure the deployment into logical layers. This repository includes three deployable units:

- **Resource Group** – Logical grouping used to organize, manage, and apply access policies to IBM Cloud resources
- **VPC** – Virtual Private Cloud with subnets, ACLs, and public gateway configuration  
- **OCP** – Red Hat OpenShift cluster deployed within the VPC

---

## Purpose

The purpose of this solution is to provide:

1. **A repeatable, automated deployment model** for IBM Cloud environments using Terragrunt.  
2. **A modular infrastructure structure** separating the Resource Group, VPC, and OpenShift layers into clear Terragrunt modules.  
3. **A reference implementation** that demonstrates how to:  
   - Integrate multiple Terraform IBM modules through Terragrunt  
   - Manage dependencies between modules (e.g., VPC depends on Resource Group, OCP depends on VPC)  
   - Promote best practices for multi-layer cloud deployments  

This solution can be used as a baseline for production deployments or adapted for learning and testing environments.

---

## Architecture & Use Case

The following diagram represents the conceptual architecture for this deployment. It illustrates the relationships between the Resource Group, VPC, subnets, and the OpenShift cluster.

![Architecture Overview](https://raw.githubusercontent.com/terraform-ibm-modules/sample-iac-solutions/refs/heads/main/reference-architectures/deployable-architecture-ocp-tg.svg)

The architecture includes:

- A **Resource Group** to isolate cloud resources  
- A **VPC** with subnet, ACLs, and a public gateway
- An **OpenShift cluster**

### Use Cases
This architecture is suitable for:
- **Rapid Prototyping**: Quickly spinning up an OpenShift cluster to test applications.
- **Development & Testing**: Creating isolated environments for development teams.
- **Learning & Experimentation**: Understanding Terraform modules and Terragrunt workflows on IBM Cloud.

This configuration by default is designed for a single-zone deployment:
- Provisions **one subnet in zone-1**.  
- Deploys OpenShift with **a single worker pool** and **fixed machine type** (`bx2.8x32`).  
- Uses default versioning for OpenShift (no specific version pinned).

(See [Network & Zone Configuration](#network--zone-configuration) for customization details)

---

## Pre-requisites

- You have an **IBM Cloud account** with required permissions to create VPC, Subnets, ACLs, and OpenShift clusters.  
- An **IBM Cloud API key** is available and exported as an environment variable.  
- The account has quota available for:
  - VPC creation  
  - Public gateways  
  - Subnets  
  - Worker nodes for OpenShift  

### Tools & Runtime

- Terraform **v1.9 or higher**  
- Terragrunt **v0.94 or higher**  

Set TERRAGRUNT_TFPATH to the location of your Terraform binary to confirm which executable Terragrunt should use for all operations. This can be different on your machine so ensure to set it to the correct path.

```bash
# Mac/Linux
export TERRAGRUNT_TFPATH=/usr/local/bin/terraform

# Windows
set TERRAGRUNT_TFPATH="C:\Program Files\Terraform\terraform.exe"
```

### Network & Zone Configuration

The current configuration deploys the cluster in a single subnet within a single zone.

To add more subnets in the same zone or create subnets in a different zone, you can modify the `subnets` value in the `inputs` block of [vpc/terragrunt.hcl](vpc/terragrunt.hcl).

To create multiple worker pools or change worker pool configuration, you can modify the `worker_pools` value in the `inputs` block of [ocp/terragrunt.hcl](ocp/terragrunt.hcl).



### Module Dependencies

- Resource Group must exist before VPC creation.  
- VPC must exist before OCP cluster deployment.  
- `terragrunt run --all` commands will handle dependency ordering automatically.  

---

## Solution Scope

- This solution does **not** include:
  - VPN, Transit Gateway, or Direct Link connectivity  
  - Load balancers external to the OCP cluster  
  - Security groups (only ACLs are used)  
  - LogDNA, Monitoring, Key Protect, or Secrets Manager integrations  

- Running Terragrunt **inside individual module folders** may produce dependency errors; all commands should be executed from the root folder.

### Configuration & Deployment

You can customize the deployment by modifying the `prefix` and `region` values in locals block in `variables-terragrunt.hcl` to select the target region and ensure unique resource naming.

To deploy the solution, run the following commands from the root directory:

```bash
terragrunt run --all plan
terragrunt run --all apply
```
