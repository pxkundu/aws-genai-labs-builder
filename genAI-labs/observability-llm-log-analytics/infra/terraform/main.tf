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

locals {
  name          = "${var.project}-${var.environment}"
  lambda_bucket = "${local.name}-lambda"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "lambda" {
  bucket        = "${local.lambda_bucket}-${random_id.suffix.hex}"
  force_destroy = true
  tags          = var.tags
}

resource "aws_iam_role" "lambda" {
  name = "${local.name}-llm-alert-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name = "${local.name}-lambda-policy"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["bedrock:InvokeModel"],
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
      },
      {
        Effect = "Allow",
        Action = ["es:ESHttpGet"],
        Resource = var.opensearch_read_arn
      },
      {
        Effect   = "Allow",
        Action   = ["ssm:GetParameter"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_sns_topic" "alerts" {
  name = "${local.name}-alerts"
  tags = var.tags
}

resource "aws_lambda_function" "llm_alert" {
  function_name    = "${local.name}-llm-alert"
  role             = aws_iam_role.lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  s3_bucket        = aws_s3_bucket.lambda.bucket
  s3_key           = var.lambda_package_key
  timeout          = 60
  memory_size      = 512
  environment {
    variables = {
      OPENSEARCH_ENDPOINT = var.opensearch_endpoint
      BEDROCK_MODEL_ID    = var.bedrock_model_id
      SLACK_WEBHOOK_URL   = var.slack_webhook_url
      ALERT_TOPIC_ARN     = aws_sns_topic.alerts.arn
    }
  }
  tags = var.tags
}

resource "aws_eventbridge_rule" "cloudwatch_alarm" {
  name        = "${local.name}-cw-alarm"
  description = "Route CloudWatch alarms for LLM enrichment"
  event_pattern = jsonencode({
    "source": ["aws.cloudwatch"],
    "detail-type": ["CloudWatch Alarm State Change"]
  })
}

resource "aws_eventbridge_target" "lambda" {
  rule      = aws_eventbridge_rule.cloudwatch_alarm.name
  target_id = "lambda-llm"
  arn       = aws_lambda_function.llm_alert.arn
}

resource "aws_lambda_permission" "allow_events" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.llm_alert.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_eventbridge_rule.cloudwatch_alarm.arn
}

resource "aws_cloudwatch_metric_alarm" "sample_latency" {
  alarm_name          = "${local.name}-sample-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "genai_prompt_latency_ms"
  namespace           = var.metric_namespace
  period              = 60
  statistic           = "Average"
  threshold           = var.latency_threshold_ms
  alarm_description   = "Sample latency alarm for LLM enrichment workflow"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  tags                = var.tags
}
