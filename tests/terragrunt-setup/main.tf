locals {
  deps_path = "/tmp"
}

data "external" "install_terragrunt" {
  count   = var.install_terragrunt ? 1 : 0
  program = ["bash", "${path.module}/scripts/install-terragrunt.sh", local.deps_path]
}
