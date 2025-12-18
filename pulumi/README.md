# Description

This repository serves as the central collection of Pulumi examples that demonstrate how to provision Terraform IBM Modules.

##  Pulumi IBM Cloud Examples

This project demonstrates how to provision **IBM Cloud Object Storage (COS)** and **Watson Discovery** instances using Pulumi with the official `terraform-ibm-modules`.

## Setup

1. Install dependencies
   Add the required Pulumi Terraform modules:

   ```sh
    pulumi package add terraform-module terraform-ibm-modules/cos/ibm 10.7.2 ibm_cos_module
    pulumi package add terraform-module terraform-ibm-modules/kms-all-inclusive/ibm 5.5.5 ibm_kms_module
    pulumi package add terraform-module terraform-ibm-modules/resource-group/ibm 1.4.6 ibm_rg_module
    pulumi package add terraform-module terraform-ibm-modules/watsonx-discovery/ibm 1.11.1 wx_discovery
   ```

2. Configure IBM Cloud credentials
    Export your API key:

    ```sh
    export IBMCLOUD_API_KEY=<your_ibmcloud_api_key> # pragma: allowlist secret
    ```

3. Set Pulumi stack config
    Define region, prefix, resource group and access group:

    ```sh
    pulumi config set region us-south # Provide region
    pulumi config set prefix pulumi2 # Provide the prefix
    pulumi config set resource-group Default # Replace with Resource Group of your choice.
    pulumi config set access_group "Public Access" # Replace with Access group of your choice.
    ```

4. Preview the changes

    ```sh
    pulumi preview
    ```

5. Apply the changes

    ```sh
    pulumi up
    ```

6. Destroy the resources

    ```sh
    pulumi down
    ```

## Validation

You can log in to IBM Cloud and verify :

- The COS instance and bucket in the IBM Cloud console under Object Storage.
- Watson Discovery instance in the IBM Cloud dashboard.
- Resource Group and Key Protect instance.
