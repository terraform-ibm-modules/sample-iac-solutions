locals {
  deps_path = "/tmp"
}

data "external" "install_terragrunt" {
  program = ["bash", "${path.module}/scripts/install-terragrunt.sh", local.deps_path]
}
