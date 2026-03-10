# Build Secure IBM Cloud Infrastructure with Terraform Modules for AI Applications

This **IBM Cloud Terraform tutorial** shows how to compose and integrate reusable Terraform modules to build a secure, scalable **Infrastructure as Code** solution on IBM Cloud. You will provision, configure, and operate the Loan Risk AI Agents application while applying IaC best practices for automation, compliance, and observability.

## Prerequisites

Before starting this tutorial, make sure you have the necessary tools, knowledge, and familiarity with IBM Cloud services. These prerequisites will help you follow along with provisioning infrastructure using Terraform modules and deploying the example Loan Risk AI Agents application.

- Install the [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started).
- Install [terraform CLI](https://developer.hashicorp.com/terraform/install).
- [IBM Cloud apikey](https://cloud.ibm.com/docs/account?topic=account-userapikey&interface=ui) to access the IBM Cloud.
- Familiar with the [Loan Risk AI Agents application](https://github.com/IBM/ai-agent-for-loan-risk).

## Step 1: Clone the Terraform project repository

Before provisioning any resources, you need to clone the sample repository that contains a pre-configured Terraform project structure. This ensures your infrastructure is modular, maintainable, and ready for TIM-based deployments.

### Clone the repository

Clone the sample IaC solutions repository and navigate to the AI application directory:

```bash
git clone https://github.com/terraform-ibm-modules/sample-iac-solutions.git
cd sample-iac-solutions/secure-infra-ai-app
```

### Understanding the project structure

The cloned repository follows a standard Terraform layout, where each file serves a single purpose. This structure promotes clarity, reuse, and predictable behavior. Refer to [this](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-understand-tim-structure) for more information.

```
secure-infra-ai-app/
├── main.tf            # Infrastructure components (modules & resources)
├── variables.tf       # Input variable definitions
├── outputs.tf         # Exported outputs
├── providers.tf       # Provider configuration
├── version.tf         # Terraform version constraints
└── README.md          # Project documentation
```

All the necessary Terraform configuration files are already present in the repository. You will only need to create the `terraform.tfvars` file (in step 6) to provide your environment-specific values.

## Step 2: Review IBM Cloud provider configuration

Before you can provision any resources, Terraform needs to know **how to connect to IBM Cloud**. The repository includes pre-configured provider settings in [`providers.tf`](providers.tf) and [`version.tf`](version.tf).
Review them to understand the provider setup, but no changes are needed.

### IBM Cloud and REST API providers

The [`providers.tf`](providers.tf) file tells Terraform how to authenticate with IBM Cloud and interact with services. It also configures the REST API provider to allow API calls to external endpoints.

The configuration includes:
- **IBM Cloud provider**: Authenticates using your API key and deploys resources in the specified region.
- **REST API provider**: Enables API calls with IAM token authentication.

### Terraform and provider versions

The [`version.tf`](version.tf) file ensures that Terraform uses the correct version and compatible provider versions for IBM Cloud and REST API.

## Step 3: Review input variables

To make your Terraform configuration **flexible and reusable**, input variables are defined in [`variables.tf`](variables.tf). These variables allow you to manage sensitive information, environment-specific values, and configuration parameters outside of your main code, enabling different environments (dev, test, prod) to use the same Terraform code with different values.

Review the [`variables.tf`](variables.tf) file. It defines the following variables:

- **`ibmcloud_api_key`** (required): Your IBM Cloud API key for authentication.
- **`watsonx_ai_api_key`** (optional): API key for IBM watsonx. If not provided, the IBM Cloud API key will be used.
- **`prefix`** (required): A prefix added to all resource names to avoid naming conflicts.
- **`region`** (optional): IBM Cloud region for deployment (default: `us-south`).

> **Tip**: Required variables must be provided via `terraform.tfvars` or environment variables. Optional variables can remain unset, in which case Terraform will use the default value.

## Step 4: Review infrastructure components

The [`main.tf`](main.tf) file in the repository contains the complete **Terraform configuration** that defines all infrastructure components required to deploy the Loan Risk AI Agents application. It orchestrates `resource groups`, `Code Engine project`, `secrets`, `builds`, `kms`, `cos`, and the `application deployment`. All resources use a **consistent naming prefix** (`${var.prefix}-`) to prevent naming conflicts and maintain uniformity across the deployment.

Review the [`main.tf`](main.tf) file to understand the infrastructure components:

<details>

<summary>Resource Group (Foundation)</summary>

A **resource group** is a logical container for IBM Cloud resources used for organization, IAM access control, and lifecycle management. This module typically acts as the **root dependency** for all other modules.

> **Reference**: See the [terraform-ibm-resource-group documentation](https://github.com/terraform-ibm-modules/terraform-ibm-resource-group/blob/main/README.md).

</details>

<details>

<summary>Code Engine Project</summary>

A **Code Engine project** hosts and manages the Loan Risk AI Agents application workloads in a serverless container environment. This project will serve as the deployment target for your containers.

> **Reference**: See the [terraform-ibm-code-engine-project documentation](https://github.com/terraform-ibm-modules/terraform-ibm-code-engine/tree/main/modules/project).

</details>

<details>

<summary>Code Engine Secret</summary>

A **Code Engine secret** grants access to the private container registry (`private.us.icr.io`), enabling the push of container images for the application. IBM Cloud Container Registry is the service that you can use to store and share your container images. This secret authenticates with the container registry during the build process.

> **Reference**: See the [terraform-ibm-code-engine-secret documentation](https://github.com/terraform-ibm-modules/terraform-ibm-code-engine/tree/main/modules/secret).

</details>

<details>

<summary>Container Registry Namespace</summary>

An **IBM Cloud Container Registry namespace** organizes and stores the container images used by the Code Engine project.

> **Reference**: See the [terraform-ibm-container-registry documentation](https://github.com/terraform-ibm-modules/terraform-ibm-container-registry/blob/main/README.md).

</details>

<details>

<summary>Code Engine Build</summary>

The **Code Engine build** configuration builds a **container image from source code** hosted at the [Loan Risk AI Agents repository](https://github.com/IBM/ai-agent-for-loan-risk) using the **Dockerfile** included in the repository. The build output is pushed to **IBM Cloud Container Registry** using the previously created **registry authentication secret**. The resulting **container image** serves as the **foundation for the AI application deployment**, enabling a **reproducible**, **automated**, and **build-from-source** workflow that integrates seamlessly with **Code Engine**.

Key configuration:
- `source_url` – Git repository containing the AI application source code.
- `strategy_type` – Uses the Dockerfile in the repository to build the image.
- `output_secret` – References the secret created earlier for registry authentication.
- `output_image` – Destination path in Container Registry for the built image.

> **Reference**: See the [terraform-ibm-code-engine-build documentation](https://github.com/terraform-ibm-modules/terraform-ibm-code-engine/tree/main/modules/build).

</details>

<details>

<summary>Key Protect and Customer-Managed Encryption Keys</summary>

An **IBM Key Protect instance** with a key ring and customer-managed encryption keys secures Cloud Object Storage buckets and the watsonx.ai project.

Key configuration:
- `key_protect_instance_name` – Name of the Key Protect service instance.
- `key_ring_name` – Logical container for organizing encryption keys.
- `key_name` – Customer-managed root key used to encrypt COS and watsonx.ai resources.
- `resource_group_id` – Resource group where the Key Protect instance is deployed.
- `region` – Region where the Key Protect service is provisioned.
> **Reference**: See the [terraform-ibm-kms-all-inclusive documentation](https://github.com/terraform-ibm-modules/terraform-ibm-kms-all-inclusive/blob/main/README.md).

</details>

<details>

<summary>Cloud Object Storage with Key Protect Encryption</summary>

A **Cloud Object Storage (COS)** instance and bucket with encryption using customer-managed keys from Key Protect for secure storage of watsonx.ai project data.

> **Reference**: See the [terraform-ibm-cos documentation](https://github.com/terraform-ibm-modules/terraform-ibm-cos/blob/main/README.md).

</details>

<details>

<summary>watsonx.ai Project with COS Encryption</summary>

A **watsonx.ai project** with integrated **Cloud Object Storage (COS)** and **customer-managed encryption keys** securely stores data for AI workloads and provides the project ID needed for deploying the Agentic AI agent.

Key configuration:

- `project_name` – Name of the watsonx.ai project.
- `watsonx_ai_studio_plan` – Service plan for watsonx.ai Studio (e.g., `professional-v1`).
- `watsonx_ai_runtime_plan` – Service plan for runtime environments (e.g., `v2-professional`).
- `cos_instance_crn`, `cos_kms_key_crn`, enable_cos_kms_encryption – COS settings.
- `resource_group_id`, `region` – Deployment settings.

> **Reference**: See the [terraform-ibm-watsonx-ai documentation](https://github.com/terraform-ibm-modules/terraform-ibm-watsonx-ai/blob/main/README.md).

</details>

<details>

<summary>Code Engine Application</summary>

A **Code Engine application** runs the containerized Loan Risk AI Agents application as a scalable, serverless workload.

Key configuration:

- `image_reference` – Path to the container image built in the previous step.
- `image_secret` – References the secret for registry access.
- `run_env_variables` – Environment variables for watsonx integration.

> **Reference**: See the [terraform-ibm-code-engine-application documentation](https://github.com/terraform-ibm-modules/terraform-ibm-code-engine/tree/main/modules/app).

</details>

## Step 5: Review output values

The [`outputs.tf`](outputs.tf) file defines output values that provide quick access to important resource information after deployment:

- **Resource Group ID** – For referencing in other services.
- **Code Engine Project ID** – For managing workloads.
- **Container Image URL** – For deployments.
- **Application Route URL** – Public endpoint to access the application.
- **watsonx.ai Project ID** – Required for AI agent integrations.

These outputs will be displayed after running `terraform apply` in the next step and can be queried anytime using `terraform output`.

## Step 6: Configure variables and deploy the infrastructure

In this step, you will configure your environment-specific variables and deploy the complete infrastructure using Terraform. This includes initializing modules, previewing planned changes, and applying the configuration to provision resources in IBM Cloud.

> **Note**: For more details about TIM module deployments, see [Deploy TIM Module guide](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-deploy-tim-module) or learn more about deployment best practices.

### Secure variables

Create the `terraform.tfvars` file. In your terminal, run:

```bash
touch terraform.tfvars
```

Update the `terraform.tfvars` file with your environment-specific values:

```terraform
ibmcloud_api_key             = "<your-IBM-cloud-api-key>"        # From IBM Cloud IAM           #pragma: allowlist secret
watsonx_ai_api_key           = "<your-watsonx-ai-api-key>"       # Optional         #pragma: allowlist secret
prefix                       = "<your-prefix>"                   # Define prefix to avoid naming conflicts
```

#### Guidelines:
1. Replace `<your-IBM-cloud-api-key>` with your actual IBM Cloud API key.
2. Replace `<your-prefix>` with a short, unique prefix for your resources.
3. Ensure this file is not checked into source control as it contains sensitive information.

### Deploy the infrastructure

Open a terminal and run the following commands to deploy the infrastructure:

```bash
terraform init   # Initialize providers and modules
terraform plan   # Preview changes without applying
terraform apply  # Apply changes (type 'yes' when prompted)
```

> **Note**: This may take a few minutes. While waiting, you can explore the resources being created in the IBM Cloud console.

Make sure you open these links in the target sandbox account:

- Code Engine Project section: https://cloud.ibm.com/containers/serverless/projects
    1. Click on your serverless project named `<your-initials>-ce-project`.
    2. In the project dashboard, navigate to the **Image builds** section from the left-hand menu to view your build configuration.
    3. Click on the build, then click `step-source-default` to see the logs of the AI app being built.
    4. Once the build is done, navigate to the **Applications** section to view your application configuration. You should see the app starting to deploy, based on the docker image just built.
    5. In the project dashboard, navigate to the **Secrets and configmaps** section to view your created secrets.
- Resource Groups section: https://cloud.ibm.com/account/resource-groups

> ✅ **Success**: After the apply completes, your IBM Cloud resources will be successfully provisioned.

> **Access the deployed application**: Use the `app_url` output from `terraform apply` — it provides the public URL of the running Loan Risk AI Agents sample application. The app may take up to a minute to fully load after deployment.

## Step 7: Verify and explore your deployment

After the `terraform apply` completes, it is important to verify that all resources have been correctly provisioned and are functioning as expected. This step guides you through exploring your IBM Cloud sandbox account to confirm deployment status.

### Explore Code Engine Project

Open the Code Engine Project section: https://cloud.ibm.com/containers/serverless/projects

1. Click on your serverless project named `<your-prefix>-ce-project`.
2. Navigate to the **Image builds** section to view your build configuration.
3. Click on the build, then **step-source-default** to see the logs of the AI app being built.
4. Once the build is complete, go to the **Applications** section to check that your app is starting.
5. Review the **Secrets and configmaps** section to confirm registry credentials and application secrets.

### Check Resource Groups

Open the Resource Groups section: https://cloud.ibm.com/account/resource-groups

- Confirm that your resource group exists and that all associated resources are listed.

### View all resources

Open the All Resources view: https://cloud.ibm.com/resources

- Use your prefix in the search/filter to locate all deployed resources.
- Verify that each resource is provisioned according to your configuration.
