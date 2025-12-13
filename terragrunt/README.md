# Deploying a single zone Red Hat Openshift Cluster in a Virtual Private Cloud using Terragrunt

This project provides an opinionated, Terragrunt-based framework for deploying IBM Cloud infrastructure using Terraform IBM Cloud modules. The configuration automates the provisioning of the foundational cloud components required to run Red Hat OpenShift on IBM Cloud VPC, ensuring consistency, repeatability, and modular infrastructure design.

Terragrunt is used to orchestrate module dependencies, manage shared provider settings, enforce variable inheritance, and structure the deployment into logical layers. This repository includes three deployable units:

- **Resource Group** – Logical grouping used to organize, manage, and apply access policies to IBM Cloud resources
- **VPC** – Virtual Private Cloud with subnets, ACLs, and public gateway configuration  
- **OCP** – Red Hat OpenShift cluster deployed within the VPC

---

## Purpose

The purpose of this project is to provide:

1. **A repeatable, automated deployment model** for IBM Cloud environments using Terragrunt.  
2. **A modular infrastructure structure** separating the Resource Group, VPC, and OpenShift layers into clear Terragrunt modules.  
3. **A reference implementation** that demonstrates how to:  
   - Integrate multiple Terraform IBM modules through Terragrunt  
   - Manage dependencies between modules (e.g., VPC depends on Resource Group, OCP depends on VPC)  
   - Promote best practices for multi-layer cloud deployments  

This project can be used as a baseline for production deployments or adapted for learning and testing environments.

---

## Architecture Diagram

The following diagram represents the conceptual architecture for this deployment. It illustrates the relationships between the Resource Group, VPC, subnets, and the OpenShift cluster.

![Architecture Overview](https://raw.githubusercontent.com/terraform-ibm-modules/sample-iac-solutions/main/reference-architectures/deployable-architecture-ocp-tg.svg)

The architecture includes:

- A **Resource Group** to isolate cloud resources  
- A **VPC** with subnet, ACLs, and a public gateway
- An **OpenShift cluster**

---

## Assumptions

- This documentation is meant to be used for illustrative and learning purposes primarily.
- This document expects the reader to have a basic level of understanding of network infrastructure, compute, Terraform and Terragrunt.
- You have an **IBM Cloud account** with required permissions to create VPC, Subnets, ACLs, and OpenShift clusters.  
- An **IBM Cloud API key** is available and exported as an environment variable.  
- The account has quota available for:
  - VPC creation  
  - Public gateways  
  - Subnets  
  - Worker nodes for OpenShift  

### Tools & Runtime

- Terraform **v1.5 or higher**  
- Terragrunt **v0.54 or higher**  
- IBM Cloud CLI installed and authenticated  
- Git access to fetch Terraform modules  

### Network & Region Assumptions

- The deployment region used is **us-south** (can be changed in the module).  
- Only **zone-1** is used for the example subnet in this configuration.  

### Module Dependencies

- Resource Group must exist before VPC creation.  
- VPC must exist before OCP cluster deployment.  
- `terragrunt run --all` commands will handle dependency ordering automatically.  

---

## Limitations

### Functional Limitations

- The provided VPC example only provisions **one subnet in zone-1**.  
  - Additional subnets must be manually added for multi-zone deployments.
- The OpenShift module is configured with **a single worker pool** and **fixed machine type** (`bx2.8x32`).  
- `ocp_version`, addons, and entitlement parameters are set to **null**, meaning default versioning behavior applies.

### Limitations

- This project does **not** include:
  - VPN, Transit Gateway, or Direct Link connectivity  
  - Load balancers external to the OCP cluster  
  - Security groups (only ACLs are used)  
  - LogDNA, Monitoring, Key Protect, or Secrets Manager integrations  

- Running Terragrunt **inside individual module folders** may produce dependency errors; all commands should be executed from the root folder using:  

  ```bash
  terragrunt run --all plan
  terragrunt run --all apply
