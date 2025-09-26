# Terraform Backend Configuration
# This file configures the S3 backend for Terraform state storage

terraform {
  backend "s3" {
    # These values will be provided via CLI or environment variables
    # Example: terraform init -backend-config="bucket=your-terraform-state-bucket"
    # bucket = "healthcare-chatgpt-terraform-state"
    # key    = "healthcare-chatgpt-clone/terraform.tfstate"
    # region = "us-east-1"
    # encrypt = true
    # dynamodb_table = "terraform-state-lock"
  }
}
