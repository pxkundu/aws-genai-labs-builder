resource "aws_iot_thing_type" "type" {
  name = var.thing_type_name
}

data "aws_iam_policy_document" "iot_rule_role_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["iot.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "iot_rule_role" {
  name               = "${var.name_prefix}-iot-rule-role"
  assume_role_policy = data.aws_iam_policy_document.iot_rule_role_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "iot_rule_policy" {
  statement {
    actions   = ["kinesis:PutRecord", "kinesis:PutRecords", "kinesis:DescribeStream"]
    resources = [var.kinesis_stream_arn]
  }
  statement {
    actions   = ["firehose:PutRecord", "firehose:PutRecordBatch"]
    resources = [var.firehose_stream_arn]
  }
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [var.lambda_arn]
  }
  statement {
    actions   = ["iotevents:BatchPutMessage"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "iot_rule_policy_inline" {
  role   = aws_iam_role.iot_rule_role.id
  policy = data.aws_iam_policy_document.iot_rule_policy.json
}

# IoT Policy for devices (least-privileged demo policy)
resource "aws_iot_policy" "device_policy" {
  name = "${var.name_prefix}-device-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "iot:Connect"
        ],
        Resource = ["*"]
      },
      {
        Effect = "Allow",
        Action = [
          "iot:Publish",
          "iot:Receive"
        ],
        Resource = ["*"]
      },
      {
        Effect = "Allow",
        Action = [
          "iot:Subscribe"
        ],
        Resource = ["*"]
      }
    ]
  })
}

# Rule: send telemetry to Kinesis, Firehose, Lambda, and IoT Events
resource "aws_iot_topic_rule" "telemetry_rule" {
  name        = "${var.name_prefix}-telemetry"
  enabled     = true
  sql         = "SELECT * FROM '${var.telemetry_topic_filter}'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn = aws_iam_role.iot_rule_role.arn
    stream_name = regex("arn:aws:kinesis:[^:]+:[0-9]+:stream/(.*)", var.kinesis_stream_arn)[0]
    partition_key = "${topic(2)}"
  }

  firehose {
    role_arn           = var.firehose_role_arn
    delivery_stream_name = regex("arn:aws:firehose:[^:]+:[0-9]+:deliverystream/(.*)", var.firehose_stream_arn)[0]
    separator          = "\\n"
  }

  lambda {
    function_arn = var.lambda_arn
  }

  iot_events {
    input_name = var.iot_events_input_name
    role_arn   = aws_iam_role.iot_rule_role.arn
  }

  tags = var.tags
}

output "policy_name" {
  value = aws_iot_policy.device_policy.name
}

locals {
  provisioning_template_body = jsonencode({
    Parameters = {
      SerialNumber = {
        Type = "String"
      }
    },
    Resources = {
      thing = {
        Type = "AWS::IoT::Thing",
        Properties = {
          ThingName = { "Ref": "SerialNumber" },
          ThingTypeName = "${var.thing_type_name}"
        }
      },
      certificate = {
        Type = "AWS::IoT::Certificate",
        Properties = {
          CertificateId = { Ref = "AWS::IoT::Certificate::Id" },
          Status        = "ACTIVE"
        }
      },
      policy = {
        Type = "AWS::IoT::Policy",
        Properties = {
          PolicyName = "${var.name_prefix}-device-policy"
        }
      }
    }
  })
}

resource "aws_iot_provisioning_template" "fleet_template" {
  count                         = var.create_fleet_provisioning ? 1 : 0
  name                          = "${var.name_prefix}-fleet-template"
  description                   = "Fleet provisioning template for workshop devices"
  enabled                       = true
  provisioning_role_arn         = aws_iam_role.iot_rule_role.arn
  template_body                 = local.provisioning_template_body
}


