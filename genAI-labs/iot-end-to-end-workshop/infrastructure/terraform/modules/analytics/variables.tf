variable "name_prefix" {
  type = string
}

variable "kinesis_stream_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}


