data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name_prefix}-lambda-proc-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions   = ["kinesis:PutRecord", "kinesis:PutRecords", "kinesis:DescribeStream"]
    resources = ["*"]
  }
  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "lambda_inline" {
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/build/processor.zip"

  source {
    content  = <<EOF
import json
import os
import boto3
import base64

kinesis = boto3.client("kinesis")
STREAM = os.environ.get("TARGET_STREAM")

def handler(event, context):
    records = []
    for rec in event.get("records", event.get("Records", [])):
        # Handle IoT Rule Lambda invocation (event is message body) or Kinesis event
        payload_b64 = rec.get("kinesis", {}).get("data")
        if payload_b64:
            payload = base64.b64decode(payload_b64)
        else:
            payload = json.dumps(rec).encode("utf-8")
        try:
            data = json.loads(payload)
        except Exception:
            data = {"raw": payload.decode("utf-8")}
        data["enriched"] = True
        records.append({"Data": (json.dumps(data) + "\n").encode("utf-8"), "PartitionKey": data.get("deviceId", "unknown")})
    if records:
        kinesis.put_records(Records=records, StreamName=STREAM)
    return {"status": "ok", "count": len(records)}
EOF
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "processor" {
  function_name = "${var.name_prefix}-lambda-processor"
  role          = aws_iam_role.lambda.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.12"
  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TARGET_STREAM = var.kinesis_stream_name
    }
  }
  tags = var.tags
}

output "lambda_function_arn" {
  value = aws_lambda_function.processor.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.processor.function_name
}


