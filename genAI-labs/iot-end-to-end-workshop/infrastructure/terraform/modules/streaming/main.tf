resource "aws_s3_bucket" "raw" {
  bucket = "${var.name_prefix}-raw-telemetry"
  tags   = var.tags
}

resource "aws_kinesis_stream" "telemetry" {
  name             = "${var.name_prefix}-telemetry"
  shard_count      = 1
  retention_period = 24
  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
  tags = var.tags
}

data "aws_iam_policy_document" "firehose_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "firehose" {
  name               = "${var.name_prefix}-firehose-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "firehose_access" {
  statement {
    actions = ["s3:PutObject", "s3:AbortMultipartUpload", "s3:ListBucket", "s3:GetBucketLocation"]
    resources = [
      aws_s3_bucket.raw.arn,
      "${aws_s3_bucket.raw.arn}/*"
    ]
  }
  statement {
    actions   = ["kinesis:DescribeStream", "kinesis:GetShardIterator", "kinesis:GetRecords", "kinesis:ListShards"]
    resources = [aws_kinesis_stream.telemetry.arn]
  }
  statement {
    actions   = ["logs:PutLogEvents"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "firehose_policy" {
  role   = aws_iam_role.firehose.id
  policy = data.aws_iam_policy_document.firehose_access.json
}

resource "aws_kinesis_firehose_delivery_stream" "raw_to_s3" {
  name        = "${var.name_prefix}-raw-to-s3"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.raw.arn
    buffering_size = 5
    buffering_interval = 60
    compression_format = "GZIP"
    prefix = "year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    error_output_prefix = "errors/!{firehose:error-output-type}/"
    cloudwatch_logging_options {
      enabled = true
      log_group_name  = "/aws/kinesisfirehose/${var.name_prefix}-raw-to-s3"
      log_stream_name = "S3Delivery"
    }
  }

  tags = var.tags
}

# Optional placeholders for OpenSearch wiring (exposed as nulls if unused).
output "opensearch_arn" {
  value       = null
  description = "Optional OpenSearch domain ARN (not provisioned by default)."
}

output "opensearch_role_arn" {
  value       = null
  description = "Optional role for IoT rule to write to OpenSearch (not provisioned)."
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.telemetry.name
}

output "kinesis_stream_arn" {
  value = aws_kinesis_stream.telemetry.arn
}

output "firehose_name" {
  value = aws_kinesis_firehose_delivery_stream.raw_to_s3.name
}

output "firehose_stream_arn" {
  value = aws_kinesis_firehose_delivery_stream.raw_to_s3.arn
}

output "firehose_role_arn" {
  value = aws_iam_role.firehose.arn
}

output "firehose_bucket_name" {
  value = aws_s3_bucket.raw.bucket
}

output "firehose_bucket_arn" {
  value = aws_s3_bucket.raw.arn
}


