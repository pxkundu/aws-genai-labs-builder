variable "name_prefix" {
  type = string
}

variable "kinesis_stream_name" {
  type = string
}

variable "firehose_delivery_name" {
  type = string
}

variable "lambda_function_name" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}


