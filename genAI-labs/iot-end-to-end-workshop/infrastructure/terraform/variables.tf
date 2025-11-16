variable "project_name" {
  description = "Project name prefix for resource naming."
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy the workshop."
  type        = string
  default     = "us-east-1"
}

variable "enable_opensearch" {
  description = "Whether to deploy an OpenSearch domain and a rule target."
  type        = bool
  default     = false
}

variable "iot_telemetry_topic" {
  description = "MQTT topic for device telemetry."
  type        = string
  default     = "devices/+/telemetry"
}

variable "thing_type_name" {
  description = "Default thing type name."
  type        = string
  default     = "workshopThingType"
}

variable "create_fleet_provisioning" {
  description = "Create a sample Fleet Provisioning template."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags applied to all resources."
  type        = map(string)
  default     = {}
}


