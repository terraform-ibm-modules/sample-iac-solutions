output "install_terragrunt_status" {
  description = "Status returned by the terragrunt installation script."
  value       = data.external.install_terragrunt.result.status
}
