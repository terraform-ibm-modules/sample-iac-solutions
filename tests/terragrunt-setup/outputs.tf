output "install_terragrunt_status" {
  description = "Status returned by the terragrunt installation script."
  value       = var.install_terragrunt ? data.external.install_terragrunt[0].result.status : "skipped"
}
