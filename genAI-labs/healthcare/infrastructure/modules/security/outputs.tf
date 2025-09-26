# Security Module Outputs

output "ec2_security_group_id" {
  description = "ID of the EC2 security group"
  value       = aws_security_group.ec2.id
}

output "ec2_security_group_arn" {
  description = "ARN of the EC2 security group"
  value       = aws_security_group.ec2.arn
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "rds_security_group_arn" {
  description = "ARN of the RDS security group"
  value       = aws_security_group.rds.arn
}

output "ec2_iam_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2_role.arn
}

output "ec2_iam_role_name" {
  description = "Name of the EC2 IAM role"
  value       = aws_iam_role.ec2_role.name
}

output "ec2_instance_profile_arn" {
  description = "ARN of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.arn
}

output "ec2_instance_profile_name" {
  description = "Name of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "s3_policy_arn" {
  description = "ARN of the S3 access policy"
  value       = aws_iam_policy.ec2_s3_policy.arn
}

output "rds_policy_arn" {
  description = "ARN of the RDS access policy"
  value       = aws_iam_policy.ec2_rds_policy.arn
}

output "secrets_policy_arn" {
  description = "ARN of the Secrets Manager access policy"
  value       = aws_iam_policy.ec2_secrets_policy.arn
}

output "bedrock_policy_arn" {
  description = "ARN of the Bedrock access policy"
  value       = aws_iam_policy.ec2_bedrock_policy.arn
}

output "cloudwatch_policy_arn" {
  description = "ARN of the CloudWatch access policy"
  value       = aws_iam_policy.ec2_cloudwatch_policy.arn
}
