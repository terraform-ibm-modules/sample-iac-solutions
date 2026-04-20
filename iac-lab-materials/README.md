# IaC Lab Materials

This directory contains the Infrastructure as Code (IaC) lab materials for the TechXChange tutorial on building and publishing Deployable Architectures on IBM Cloud.

## Overview

This lab demonstrates how to create a secure hub-and-spoke network architecture on IBM Cloud using Terraform modules. The architecture includes:

- Management VPC with jumpbox server
- Workload VPC with application servers
- Transit Gateway for VPC connectivity
- Load balancers for traffic distribution
- Virtual Private Endpoints (VPE) for secure cloud service access
- Cloud Object Storage integration

## Documentation

For detailed instructions and the complete tutorial, visit:
- [IBM Cloud Terraform Provider Documentation](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-package-and-publish-da)
- [TechXChange Lab Guide](https://ibm-cloud.github.io/techxchange-labs/pfeng-1818/#/)

## Repository

This code is maintained in the [terraform-ibm-modules/sample-iac-solutions](https://github.com/terraform-ibm-modules/sample-iac-solutions) repository under the `iac-lab-materials` directory.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
