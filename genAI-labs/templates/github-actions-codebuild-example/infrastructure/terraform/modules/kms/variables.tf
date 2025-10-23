# KMS Module Variables

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "description" {
  description = "Description of the KMS key"
  type        = string
  default     = "KMS key for GitHub Actions CodeBuild"
}

variable "deletion_window_in_days" {
  description = "Deletion window in days for the KMS key"
  type        = number
  default     = 7
}

variable "enable_key_rotation" {
  description = "Enable automatic key rotation"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
