variable "install_terragrunt" {
  type        = bool
  description = "Set to true to automatically install terragrunt. Set to false if terragrunt is already available in the environment."
  default     = true
}
