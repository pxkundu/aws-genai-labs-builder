terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.50.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4.2"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name_prefix = "${var.project_name}-${data.aws_region.current.name}"
  tags        = merge(var.tags, { Project = var.project_name })
}

# IoT Endpoint (Data ATS)
resource "aws_iot_endpoint" "data" {
  endpoint_type = "iot:Data-ATS"
}

module "streaming" {
  source = "./modules/streaming"

  name_prefix = local.name_prefix
  tags        = local.tags
}

module "lambda_processor" {
  source = "./modules/lambda-processor"

  name_prefix          = local.name_prefix
  kinesis_stream_name  = module.streaming.kinesis_stream_name
  tags                 = local.tags
}

module "iot_core" {
  source = "./modules/iot-core"

  name_prefix              = local.name_prefix
  telemetry_topic_filter   = var.iot_telemetry_topic
  thing_type_name          = var.thing_type_name
  create_fleet_provisioning = var.create_fleet_provisioning

  kinesis_stream_arn = module.streaming.kinesis_stream_arn
  firehose_role_arn  = module.streaming.firehose_role_arn
  firehose_stream_arn = module.streaming.firehose_stream_arn
  s3_bucket_arn      = module.streaming.firehose_bucket_arn
  lambda_arn         = module.lambda_processor.lambda_function_arn
  iot_events_input_name = module.events.events_input_name

  enable_opensearch  = var.enable_opensearch
  opensearch_arn     = module.streaming.opensearch_arn
  opensearch_role_arn = module.streaming.opensearch_role_arn

  tags = local.tags
}

module "analytics" {
  source = "./modules/analytics"

  name_prefix         = local.name_prefix
  kinesis_stream_arn  = module.streaming.kinesis_stream_arn
  tags                = local.tags
}

module "events" {
  source = "./modules/events"

  name_prefix = local.name_prefix
  tags        = local.tags
}

module "defender" {
  source = "./modules/defender"

  name_prefix = local.name_prefix
  tags        = local.tags
}

module "monitoring" {
  source = "./modules/monitoring"

  name_prefix             = local.name_prefix
  kinesis_stream_name     = module.streaming.kinesis_stream_name
  firehose_delivery_name  = module.streaming.firehose_name
  lambda_function_name    = module.lambda_processor.lambda_function_name
  s3_bucket_name          = module.streaming.firehose_bucket_name
  tags                    = local.tags
}


