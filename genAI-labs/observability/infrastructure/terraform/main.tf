terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_region" "current" {}

locals {
  name_prefix = "${var.environment}-genai-observability"
}

resource "random_uuid" "dash_id" {}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/observability/${local.name_prefix}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id
  tags              = merge(var.tags, { "Component" = "logging" })
}

resource "aws_xray_group" "app" {
  group_name        = "${local.name_prefix}-xray"
  filter_expression = "service(""genai-observability-service"")"
  insights_configuration {
    insights_enabled = true
  }
  tags = merge(var.tags, { "Component" = "tracing" })
}

resource "aws_amp_workspace" "this" {
  alias = "${local.name_prefix}-amp"
  tags  = merge(var.tags, { "Component" = "metrics" })
}

resource "aws_grafana_workspace" "this" {
  account_access_type     = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type         = "SERVICE_MANAGED"
  grafana_version         = "9.4"
  tags                    = merge(var.tags, { "Component" = "analytics" })
}

resource "aws_grafana_workspace_api_key" "datasource_writer" {
  workspace_id = aws_grafana_workspace.this.id
  key_name     = "${local.name_prefix}-datasource"
  key_role     = "ADMIN"
  seconds_to_live = 86400
}

resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"
  tags = merge(var.tags, { "Component" = "alerting" })
}

resource "aws_cloudwatch_metric_alarm" "latency" {
  alarm_name          = "${local.name_prefix}-prompt-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "genai_prompt_latency_ms"
  namespace           = var.custom_metric_namespace
  period              = 300
  statistic           = "Average"
  threshold           = var.prompt_latency_threshold_ms
  alarm_description   = "GenAI prompt latency exceeded threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    Service = "genai-observability-service"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
  tags          = merge(var.tags, { "Component" = "alerting" })
}

resource "aws_cloudwatch_dashboard" "this" {
  dashboard_name = "${local.name_prefix}-dashboard"
  dashboard_body = file("${path.module}/../../resources/dashboards/cloudwatch-dashboard.json")
}

resource "aws_cloudwatch_log_subscription_filter" "security" {
  name            = "${local.name_prefix}-security"
  log_group_name  = aws_cloudwatch_log_group.app.name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" }"
  destination_arn = var.security_lambda_arn

  depends_on = [aws_cloudwatch_log_group.app]
}

resource "aws_lambda_function" "ai_ops" {
  count            = var.enable_ai_ops ? 1 : 0
  function_name    = "${local.name_prefix}-ai-ops"
  role             = var.ai_ops_lambda_role_arn
  handler          = "index.handler"
  runtime          = "python3.11"
  filename         = var.ai_ops_lambda_package
  timeout          = 60
  environment {
    variables = {
      SNS_TOPIC_ARN       = aws_sns_topic.alerts.arn
      BEDROCK_MODEL_ID    = var.bedrock_model_id
      BEDROCK_REGION      = var.aws_region
      OBS_DASHBOARD_URL   = aws_cloudwatch_dashboard.this.dashboard_arn
    }
  }
  tags = merge(var.tags, { "Component" = "aiops" })
}

resource "aws_eventbridge_rule" "ai_ops" {
  name        = "${local.name_prefix}-ai-ops"
  description = "Trigger AI Ops lambda on CloudWatch alarms"
  event_pattern = jsonencode({
    "source" : ["aws.cloudwatch"],
    "detail-type" : ["CloudWatch Alarm State Change"],
    "detail" : {
      "alarmName" : [aws_cloudwatch_metric_alarm.latency.alarm_name]
    }
  })
}

resource "aws_eventbridge_target" "ai_ops" {
  count     = var.enable_ai_ops ? 1 : 0
  rule      = aws_eventbridge_rule.ai_ops.name
  target_id = "ai-ops-lambda"
  arn       = aws_lambda_function.ai_ops[0].arn
}

resource "aws_lambda_permission" "ai_ops" {
  count         = var.enable_ai_ops ? 1 : 0
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_ops[0].function_name
  principal     = "events.${data.aws_partition.current.dns_suffix}"
  source_arn    = aws_eventbridge_rule.ai_ops.arn
}
