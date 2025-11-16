variable "name_prefix" {
  type = string
}

variable "telemetry_topic_filter" {
  type = string
}

variable "thing_type_name" {
  type = string
}

variable "create_fleet_provisioning" {
  type = bool
}

variable "kinesis_stream_arn" {
  type = string
}

variable "firehose_role_arn" {
  type = string
}

variable "firehose_stream_arn" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "lambda_arn" {
  type = string
}

variable "iot_events_input_name" {
  type        = string
  description = "IoT Events input name to publish to"
}

variable "enable_opensearch" {
  type    = bool
  default = false
}

variable "opensearch_arn" {
  type    = string
  default = null
}

variable "opensearch_role_arn" {
  type    = string
  default = null
}

variable "tags" {
  type    = map(string)
  default = {}
}


