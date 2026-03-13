# IBM Cloud Hub-and-Spoke 

This repository contains the complete Terraform configuration to provision a secure hub-and-spoke VPC architecture on IBM Cloud using [Terraform IBM Modules](https://github.com/terraform-ibm-modules).

For a detailed overview of the architecture, components, and the modules used in this directory, see the [Hub-and-Spoke Overview](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-hub-spoke-infrastructure).

## Prerequisites

- An [IBM Cloud account](https://cloud.ibm.com) with permissions to create VPC, VSI, Load Balancers, Transit Gateway, VPE, and COS resources.
- An [IBM Cloud API key](https://cloud.ibm.com/docs/account?topic=account-userapikey&interface=ui).
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started) installed and authenticated.
- [Terraform CLI](https://developer.hashicorp.com/terraform/install) (version 1.9.0 or later).
- Basic familiarity with [Terraform syntax and workflows](https://developer.hashicorp.com/terraform/tutorials).
- Basic familiarity with SSH.

## Repository structure

| File | Purpose |
|---|---|
| [`main.tf`](./main.tf) | All infrastructure components — resource group, VPCs, transit gateway, SSH key, jumpbox, workload servers, load balancers, VPEs, and COS |
| [`variables.tf`](./variables.tf) | Input variable definitions for `ibmcloud_api_key`, `prefix`, and `region` |
| [`outputs.tf`](./outputs.tf) | Exported values — jumpbox IP, workload IPs, load balancer hostname, VPE IPs, COS credentials |
| [`providers.tf`](./providers.tf) | IBM Cloud provider configuration and authentication |
| [`version.tf`](./version.tf) | Terraform (>= 1.9.0) and IBM Cloud provider (>= 1.80.4) version constraints |
| `terraform.tfvars` | Your environment-specific values (you create this, not committed to source control) |
| [`test_app.py`](./test_app.py) | Sample Python application that fetches content from COS via VPE and serves it on port 8080 |
| [`dummy_page.html`](./dummy_page.html) | Test HTML page uploaded to COS and served by the sample application |

### Network Foundation

In this step, the main network infrastructure for the hub-and-spoke deployment is defined using IBM Cloud Terraform modules. The [`main.tf`](./main.tf) file orchestrates all core components in a structured and consistent way. Resources use the `${var.prefix}-` naming convention to avoid conflicts and maintain uniform naming.

The following components are created in sequence:

- **Management VPC (Hub):** Jumpbox for secure access, public load balancer for incoming traffic.
- **Workload VPC (Spoke):** Application servers in private subnets, private load balancer for traffic distribution.
- **Secure Connectivity:** Transit gateway, security groups, and ACLs control communication between components.
- **Private Service Access:** Virtual Private Endpoints (VPEs) enable private access to IBM Cloud services.

This approach ensures a secure, organized, and scalable infrastructure deployment.

The infrastructure is defined in [`main.tf`](./main.tf) and builds the following components in order.

#### Resource group (Foundation)

A **resource group** is a logical container for IBM Cloud resources used for organization, IAM access control, and lifecycle management. This module typically acts as the **root dependency** for all other modules.

#### Management VPC (The Hub)

The **Management VPC** acts as the secure entry point for the hub-and-spoke infrastructure. This VPC hosts the jumpbox server and provides controlled internet access. The [terraform-ibm-landing-zone-vpc](https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vpc) module defines the VPC, its subnets across three availability zones, and the necessary network ACLs for secure traffic management.

The following elements are configured:

- **High availability:** Subnets across three availability zones.
- **Network ACLs:** Stateful and custom rules for inbound/outbound traffic.
- **Public access:** Jumpbox and public load balancer with controlled internet connectivity.
- **Subnet IP ranges:** Logical separation of resources per availability zone.

See [`main.tf`](./main.tf) for the full configuration.

#### Workload VPC (The Spoke)

The **Workload VPC** hosts your application servers. Unlike the Management VPC, this VPC is **private** with **no direct internet access**, improving security and reducing exposure to external threats. This module sets up subnets, network ACLs, and connectivity rules to allow controlled communication with the Management VPC.

The following elements are configured:

- **CIDR Ranges:** Separate address space from the Management VPC for proper routing.
- **Private Subnets:** No public gateways to prevent direct internet access.
- **Network ACLs:** Allow traffic only between Management and Workload VPCs, securing the environment.

See [`main.tf`](./main.tf) for the full configuration.

#### Transit Gateway

To **enable private communication** between the Management and Workload VPCs, a **Transit Gateway** is created. See [`main.tf`](./main.tf).

### Create an SSH Key for Server Access

To securely connect to your virtual servers, you need an **SSH key pair**. The configuration generates a new key pair, uploads the public key to IBM Cloud, and saves the private key locally. This allows you to securely SSH into your servers while keeping the private key confidential.

The following actions are performed:

- **Generate a key pair:** Creates a new RSA key pair for server authentication.
- **Store the private key locally:** Saves the key to `<your-prefix>_ssh_private_key.pem` (read-only for the owner).
- **Upload the public key to IBM Cloud:** Makes it available for server provisioning.

Note: Saving private keys directly to the filesystem is done here for tutorial simplicity. In a production environment, you should use a secure secret management tool like **IBM Cloud Secrets Manager**.

See [`main.tf`](./main.tf) for the full configuration.

### Provision the Jumpbox Server

A **jumpbox server** is provisioned in the Management VPC to provide secure remote access to your infrastructure. The jumpbox is assigned a **public IP** and configured with security rules to control inbound and outbound traffic. The [terraform-ibm-landing-zone-vsi](https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vsi) module simplifies deployment.

The following elements are configured:

- **Security Groups:** Protect the jumpbox and allow controlled access.
- **Floating IP:** Assigns a public IP for SSH connectivity.
- **VSI Configuration:** Defines instance type, subnet placement, and SSH key access.

See [`main.tf`](./main.tf) for the full configuration.

### Provision the Workload Servers and Private Load Balancer

**Workload servers** are provisioned in the private Workload VPC and a **private load balancer** is set up to distribute traffic to these servers. The jumpbox server in the Management VPC will be the only direct access point, ensuring the workload servers remain isolated from the public internet.

The following actions are performed:

- **Workload Servers:** Deploy Debian 12 minimal instances in private subnets.
- **Security Groups:** Restrict access to only the jumpbox and load balancer, while allowing outbound DNS and HTTPS calls.
- **Private Load Balancer:** Distributes incoming traffic from the Management VPC to workload servers using round-robin algorithm.

See [`main.tf`](./main.tf) for the full configuration.

### Exposing the Application to the Internet

To make the application accessible from the internet, a **public-facing load balancer** is set up. This load balancer will receive traffic from the internet and securely forward it to the **private load balancer** in the Workload VPC.

The following are created:

1. A **public load balancer** in the Management VPC.
2. A **load balancer pool** and **pool members** pointing to the private load balancer.
3. A **listener** to handle HTTP traffic.
4. A **security group** to allow internet traffic on port 80.

This setup follows a secure cloud design pattern called **Load Balancer Chaining**: the public load balancer serves as the secure entry point and resides in the Management VPC. It is the only component exposed to the internet. Traffic is then forwarded to the private load balancer in the isolated Workload VPC. This design ensures that no resources in the Workload VPC are publicly exposed.

See [`main.tf`](./main.tf) for the full configuration.

### Provision Virtual Private Endpoints (VPEs)

To allow private workload servers to securely access IBM Cloud services like Cloud Object Storage, **Virtual Private Endpoints (VPEs)** are used. A VPE provides a local IP representation of a remote IBM Cloud service within your VPC, ensuring that traffic remains on IBM Cloud's private network.

The following are created:

1. A **security group** for the VPE to allow inbound traffic from workload resources.
2. A **VPE gateway** connected to the workload VPC.
3. Access configured to specific IBM Cloud services (Cloud Object Storage).

See [`main.tf`](./main.tf) for the full configuration.

### Provision Cloud Object Storage

To store application data securely, a **Cloud Object Storage (COS)** instance and a bucket are created. This COS instance will be used by your workload servers or applications to persist data.

See [`main.tf`](./main.tf) for the full configuration.

### Define Outputs

Output values are defined in [`outputs.tf`](./outputs.tf) to provide quick access to important resource information after deployment. These values are used throughout the validation steps below.

## Deployment

### 1. Clone and configure

Clone the repository and navigate into it:

```sh
git clone https://github.com/terraform-ibm-modules/sample-iac-solutions.git
cd sample-iac-solutions/hub-and-spoke
```

To make your Terraform configuration flexible and reusable, input variables allow you to manage sensitive information and environment-specific values outside of your main code. This enables different environments (dev, test, prod) to use the same Terraform code with different values. Create a `terraform.tfvars` file with your environment-specific values:

- `ibmcloud_api_key` — Your IBM Cloud API key (required, sensitive).
- `prefix` — A short, unique string prepended to all resource names to avoid conflicts (required).
- `region` — The IBM Cloud region for deployment (optional, defaults to `us-south`).

Note: Make sure `terraform.tfvars` is **not committed to source control**.

### 2. Initialize and deploy

```sh
terraform init
terraform plan
terraform apply
```

Review the plan output carefully before confirming with `yes`. Provisioning typically takes 10–15 minutes, with the load balancers taking the longest.

While waiting, you can inspect the resources being created in the IBM Cloud console:

- [VPCs](https://cloud.ibm.com/infrastructure/network/vpcs)
- [Virtual Server Instances](https://cloud.ibm.com/infrastructure/compute/vs)
- [SSH Keys](https://cloud.ibm.com/infrastructure/compute/sshKeys)
- [Load Balancers](https://cloud.ibm.com/infrastructure/network/loadBalancers)
- [Security Groups](https://cloud.ibm.com/infrastructure/network/securityGroups)
- [VPC Network Topology](https://cloud.ibm.com/infrastructure/vpcLayout)
- [Virtual Private Endpoints](https://cloud.ibm.com/infrastructure/network/endpointGateways)

Ensure the region is set to `us-south` (or your configured region) on each page.

### 3. Gather outputs

After the apply completes, export the key values you will need for the validation steps. Open a terminal (referred to as **Terminal 1** from here on) and run:

```sh
cd <path-to-your-terraform-project>

export JUMPBOX_IP=$(terraform output -raw jumpbox_public_ip)
export WORKLOAD_IP_1=$(terraform output -json workload_server_private_ips | jq -r '.[0]')
export LB_HOSTNAME=$(terraform output -raw public_load_balancer_hostname)
export PRIVATE_KEY_FILE=$(terraform output -raw ssh_private_key_file_name)

echo "Jumpbox IP: $JUMPBOX_IP"
echo "Workload Server 1 IP: $WORKLOAD_IP_1"
echo "Public Load Balancer: $LB_HOSTNAME"
echo "Private Key File: $PRIVATE_KEY_FILE"
```

## Testing Connectivity and Applications

After deploying your IBM Cloud infrastructure, it is essential to verify connectivity and ensure that all resources are operational. This section guides you through accessing the jumpbox, testing private workload server connectivity, and preparing for application deployment.

### Get Your Infrastructure Outputs

Before testing connectivity, gather the key infrastructure outputs from Terraform. These values are required to access the jumpbox, workload servers, and load balancer in the following steps.

Open a new terminal — we will refer to this as **Terminal 1 (Local)**. Navigate to the directory where you ran `terraform apply` and deployed the infrastructure:

```sh
cd <path-to-your-terraform-project>
```

Retrieve the jumpbox public IP address:

```sh
export JUMPBOX_IP=$(terraform output -raw jumpbox_public_ip)
echo "Jumpbox IP: $JUMPBOX_IP"
```

Retrieve a workload server private IP address (use the first one for testing):

```sh
export WORKLOAD_IP_1=$(terraform output -json workload_server_private_ips | jq -r '.[0]')
echo "Workload Server 1 IP: $WORKLOAD_IP_1"
```

Retrieve the public load balancer hostname:

```sh
export LB_HOSTNAME=$(terraform output -raw public_load_balancer_hostname)
echo "Public Load Balancer: $LB_HOSTNAME"
```

Identify the private key file name:

```sh
export PRIVATE_KEY_FILE=$(terraform output -raw ssh_private_key_file_name)
echo "Private Key File: $PRIVATE_KEY_FILE"
```

### Test Connectivity to the Jumpbox

The jumpbox acts as your secure gateway into the private environment. Connecting to it first confirms that the public network access and SSH key configuration are correct.

SSH into the jumpbox using the public IP address and the private key file you retrieved:

```sh
ssh -i $PRIVATE_KEY_FILE root@$JUMPBOX_IP
```

When prompted to continue connecting, type `yes`. Upon successful connection, your terminal prompt will change to `root@<jumpbox-name>`, indicating that you are now logged into the jumpbox.

Note: **Terminal Management**: This terminal window (Terminal 1) is now connected to the jumpbox. We will refer to this session as the **Jumpbox Session**. In the next steps, you will open a new local terminal.

## Test Connectivity to a Private Workload Server

Once connected to the jumpbox, you can verify that private workload servers in the VPC are reachable. This confirms that **Transit Gateway routing, Network ACLs, and Security Groups** are correctly configured.

### Copy the Private Key to the Jumpbox

To connect from the jumpbox to the workload server, you must copy the SSH private key to the jumpbox.

1. Open a new terminal window and label it **Terminal 2 (Local)**.
2. In **Terminal 2 (Local)**, re-export the environment variables for the jumpbox IP and private key:

```sh
export JUMPBOX_IP=$(terraform output -raw jumpbox_public_ip)
export PRIVATE_KEY_FILE=$(terraform output -raw ssh_private_key_file_name)
```

3. Copy the private key to the jumpbox:

```sh
scp -i $PRIVATE_KEY_FILE $PRIVATE_KEY_FILE root@$JUMPBOX_IP:~/.
```

### Connect to the Workload Server

With the private key on the jumpbox, you can now access a private workload server.

1. In **Terminal 2 (Local)**, retrieve the workload server's private IP address and confirm the private key filename. Copy the output values:

```sh
export WORKLOAD_IP_1=$(terraform output -json workload_server_private_ips | jq -r '.[0]')
echo "Workload IP: $WORKLOAD_IP_1"
echo "Private Key Filename: $PRIVATE_KEY_FILE"
```

2. Switch back to **Terminal 1 (Jumpbox Session)** and set the environment variables using the values you copied:

```sh
export WORKLOAD_IP_1="<paste-workload-ip-here>"
export PRIVATE_KEY_FILE="<paste-key-file-name-here>"
```

3. Update the key permissions and connect to the workload server:

```sh
chmod 400 $PRIVATE_KEY_FILE
ssh -i $PRIVATE_KEY_FILE root@$WORKLOAD_IP_1
```

When prompted to continue connecting, type `yes`. If the connection is successful, your prompt will change to `root@<workload-server-name>`.

Note: You have successfully "jumped" from the public internet into the secure, private workload environment. **Terminal 1** is now your **Workload Session**. Keep this connection active.

## Deploy and Test the End-to-End Application

The final test validates the full data path from **Internet → Public Load Balancer → Private Load Balancer → Workload Server → VPE → Cloud Object Storage (COS)**. A sample Python application ([`test_app.py`](./test_app.py)) on the workload server reads a file from COS and serves it via a local HTTP server. A test HTML page ([`dummy_page.html`](./dummy_page.html)) is included in the repo for upload to COS.

### Copy the Application to the Workload Server

The application needs to be transferred from your local machine to the workload server via the jumpbox, since the workload server has no direct internet access.

**Local → Jumpbox** — If you are currently in the Workload Session (Terminal 1), type `exit` to return to the Jumpbox Session. Your prompt should be `root@<jumpbox-name>`.

Switch to **Terminal 2 (Local)** and copy `test_app.py` to the jumpbox:

```sh
scp -i $PRIVATE_KEY_FILE test_app.py root@$JUMPBOX_IP:~
```

**Jumpbox → Workload Server** — In **Terminal 1 (Jumpbox Session)**, copy the file to the workload server:

```sh
scp -i $PRIVATE_KEY_FILE test_app.py root@$WORKLOAD_IP_1:~
```

SSH back into the workload server from the jumpbox:

```sh
ssh -i $PRIVATE_KEY_FILE root@$WORKLOAD_IP_1
```

Your prompt should now be `root@<workload-server-name>` and you are back in the **Workload Session**.

### Upload a Test File to Cloud Object Storage (Terminal 2 — Local)

1. Log in to IBM Cloud using your API key and set your working region to us-south:

```sh
ibmcloud login --apikey <YOUR_API_KEY> -r us-south
```

2. Configure the COS CLI plugin with the CRN of the service instance created by Terraform:

```sh
export COS_CRN=$(terraform output -raw cos_instance_crn)
ibmcloud cos config crn --crn "${COS_CRN}"
```

3. Upload `dummy_page.html` to your COS bucket:

```sh
export BUCKET_NAME=$(terraform output -raw bucket_name)
ibmcloud cos object-put --bucket $BUCKET_NAME --key "index.html" --body dummy_page.html
```

### Install Dependencies and Run the Application (Workload Session)

1. **Gather Credentials (Terminal 2 — Local)** — Display the values on your local machine and copy them:

```sh
terraform output -json cos_access_key_id
terraform output -json cos_secret_access_key
terraform output workload_vpe_ips_1
echo $BUCKET_NAME
```

2. **Set Environment Variables (Terminal 1 — Workload Session)** — Paste the values you copied from your local terminal:

```sh
export COS_ACCESS_KEY_ID="<paste_access_key_id_here>"
export COS_SECRET_ACCESS_KEY="<paste_secret_access_key_here>"
export VPE_ENDPOINT="<paste_workload_vpe_ips_1>"
export COS_BUCKET_NAME="<paste_bucket_name_here>"
```

3. **Run the Application**:

```sh
nohup python3 test_app.py > app.log 2>&1 &
```

The application will start and listen on port 8080. Check the logs to verify:

```sh
tail app.log
```

You should see output similar to:

```
10.10.8.6 - - [06/Dec/2025 18:39:50] "GET / HTTP/1.0" 200 -
```

## Verify Public Access

The final step validates that your application is accessible from the public internet through the **public load balancer**. This confirms that your full end-to-end setup — **Internet → Public LB → Private LB → Workload Server → VPE → COS** — is working as expected.

### Access the Application

From your **local terminal (Terminal 2 — Local)**, retrieve the public load balancer hostname:

```sh
export LB_HOSTNAME=$(terraform output -raw public_load_balancer_hostname)
echo http://$LB_HOSTNAME
```

You can now access the application by navigating to `http://$LB_HOSTNAME` in any web browser or by running:

```sh
curl http://$LB_HOSTNAME
```

### Check the Result

You should see the content of the [`dummy_page.html`](./dummy_page.html) file, confirming that the application served content via the workload server and VPE.

Note: **Congratulations!** You have successfully tested your entire hub-and-spoke infrastructure, confirming secure access through the jumpbox, proper inter-VPC connectivity, and full end-to-end application data flow from the internet, through the public and private load balancers, to the private workload server and IBM Cloud Object Storage (COS).

## Cleanup

To avoid ongoing charges, destroy all provisioned resources:

```sh
terraform destroy
```

Confirm with `yes`. After the destroy completes, verify in the IBM Cloud console that all VPC, VSI, load balancer, Transit Gateway, VPE, and COS resources have been removed.

## References

- [Hub-and-Spoke Architecture Overview](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-hub-spoke-infrastructure)
- [Terraform IBM Modules](https://github.com/terraform-ibm-modules)
- [IBM Cloud VPC documentation](https://cloud.ibm.com/docs/vpc)
