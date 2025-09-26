# S3 Module - Healthcare ChatGPT Clone
# This module creates S3 buckets for knowledge base storage

# Knowledge Base S3 Bucket
resource "aws_s3_bucket" "knowledge_base" {
  bucket = var.knowledge_base_bucket_name
  
  tags = merge(var.tags, {
    Name = "${var.environment}-knowledge-base"
    Purpose = "Healthcare Knowledge Base"
  })
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Server Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  rule {
    id     = "delete_old_versions"
    status = "Enabled"
    
    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 Bucket CORS Configuration
resource "aws_s3_bucket_cors_configuration" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 Bucket Notification Configuration (for future use)
resource "aws_s3_bucket_notification" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  # Lambda function notification can be added here for real-time processing
  # lambda_function {
  #   lambda_function_arn = aws_lambda_function.processor.arn
  #   events              = ["s3:ObjectCreated:*"]
  #   filter_prefix       = "uploads/"
  # }
}

# S3 Bucket Policy for EC2 Access
resource "aws_s3_bucket_policy" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowEC2Access"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.environment}-ec2-role"
        }
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.knowledge_base.arn,
          "${aws_s3_bucket.knowledge_base.arn}/*"
        ]
      },
      {
        Sid    = "AllowBedrockAccess"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.knowledge_base.arn,
          "${aws_s3_bucket.knowledge_base.arn}/*"
        ]
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# S3 Bucket for Application Logs (optional)
resource "aws_s3_bucket" "application_logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = "${var.project_name}-application-logs-${var.environment}-${random_id.logs_suffix[0].hex}"
  
  tags = merge(var.tags, {
    Name = "${var.environment}-application-logs"
    Purpose = "Application Logs Storage"
  })
}

resource "random_id" "logs_suffix" {
  count       = var.enable_logging_bucket ? 1 : 0
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "application_logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.application_logs[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "application_logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.application_logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "application_logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.application_logs[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle for Logs
resource "aws_s3_bucket_lifecycle_configuration" "application_logs" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.application_logs[0].id

  rule {
    id     = "delete_old_logs"
    status = "Enabled"
    
    filter {}

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
