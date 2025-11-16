variable "name_prefix" {
  type = string
}

variable "kinesis_stream_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}


