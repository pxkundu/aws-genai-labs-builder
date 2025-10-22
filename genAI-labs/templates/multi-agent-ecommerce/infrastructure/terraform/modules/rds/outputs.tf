# Outputs for RDS Module

output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_hosted_zone_id" {
  description = "Hosted zone ID of the RDS instance"
  value       = aws_db_instance.main.hosted_zone_id
}

output "db_instance_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "Name of the RDS instance"
  value       = aws_db_instance.main.db_name
}

output "db_instance_username" {
  description = "Username of the RDS instance"
  value       = aws_db_instance.main.username
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.db.id
}

output "db_security_group_arn" {
  description = "ARN of the database security group"
  value       = aws_security_group.db.arn
}

output "db_subnet_group_id" {
  description = "ID of the database subnet group"
  value       = aws_db_subnet_group.main.id
}

output "db_subnet_group_arn" {
  description = "ARN of the database subnet group"
  value       = aws_db_subnet_group.main.arn
}

output "db_parameter_group_id" {
  description = "ID of the database parameter group"
  value       = aws_db_parameter_group.main.id
}

output "db_parameter_group_arn" {
  description = "ARN of the database parameter group"
  value       = aws_db_parameter_group.main.arn
}

output "db_option_group_id" {
  description = "ID of the database option group"
  value       = aws_db_option_group.main.id
}

output "db_option_group_arn" {
  description = "ARN of the database option group"
  value       = aws_db_option_group.main.arn
}

output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
  sensitive   = true
}

output "db_credentials_secret_name" {
  description = "Name of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.name
  sensitive   = true
}

output "rds_enhanced_monitoring_role_arn" {
  description = "ARN of the RDS enhanced monitoring role"
  value       = aws_iam_role.rds_enhanced_monitoring.arn
}

output "postgresql_log_group_name" {
  description = "Name of the PostgreSQL CloudWatch log group"
  value       = aws_cloudwatch_log_group.postgresql.name
}

output "postgresql_log_group_arn" {
  description = "ARN of the PostgreSQL CloudWatch log group"
  value       = aws_cloudwatch_log_group.postgresql.arn
}

output "postgresql_upgrade_log_group_name" {
  description = "Name of the PostgreSQL upgrade CloudWatch log group"
  value       = aws_cloudwatch_log_group.postgresql_upgrade.name
}

output "postgresql_upgrade_log_group_arn" {
  description = "ARN of the PostgreSQL upgrade CloudWatch log group"
  value       = aws_cloudwatch_log_group.postgresql_upgrade.arn
}
