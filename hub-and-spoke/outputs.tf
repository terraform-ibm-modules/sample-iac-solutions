output "ssh_private_key_file_name" {
  description = "Private key file name."
  value = "${var.prefix}_ssh_private_key.pem"
}

output "jumpbox_public_ip" {
  description = "Public IP address to connect to the jumpbox server"
  value       = module.jumpbox_server.fip_list[0].floating_ip
}

output "workload_server_private_ips" {
  description = "Private IP addresses of the workload servers"
  value       = module.workload_servers.list[*].ipv4_address
}

output "public_load_balancer_hostname" {
  description = "Public hostname to access the application through the load balancer"
  value       = ibm_is_lb.public_load_balancer.hostname
}

output "workload_vpe_ips" {
  description = "Private IP addresses of VPC endpoints for cloud services"
  value       = module.workload_vpes.vpe_ips
}

output "workload_vpe_ips_1" {
  description = "One of the Private IP addresses of VPC endpoints for cloud services"
  value = flatten([for vpe_ips in module.workload_vpes.vpe_ips : [for ip in vpe_ips : ip.address]])[0]
}

output "cos_instance_crn" {
  description = "COS instance CRN"
  value       = module.cos_storage.cos_instance_crn
}

output "bucket_name" {
  description = "Bucket name"
  value       = module.cos_storage.bucket_name
}

output "cos_access_key_id" {
  sensitive   = true
  description = "Access key ID for Cloud Object Storage (S3-compatible)"
  value       = module.cos_storage.resource_keys["workload-service-credentials"]["credentials"]["cos_hmac_keys.access_key_id"]
}

output "cos_secret_access_key" {
  sensitive   = true
  description = "Secret access key for Cloud Object Storage (S3-compatible)"
  value       = module.cos_storage.resource_keys["workload-service-credentials"]["credentials"]["cos_hmac_keys.secret_access_key"]
}