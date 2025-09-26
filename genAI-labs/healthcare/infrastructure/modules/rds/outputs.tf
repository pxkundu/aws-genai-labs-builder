# RDS Module Outputs

output "cluster_identifier" {
  description = "RDS Aurora cluster identifier"
  value       = aws_rds_cluster.main.id
}

output "cluster_endpoint" {
  description = "RDS Aurora cluster endpoint"
  value       = aws_rds_cluster.main.endpoint
}

output "cluster_reader_endpoint" {
  description = "RDS Aurora cluster reader endpoint"
  value       = aws_rds_cluster.main.reader_endpoint
}

output "cluster_port" {
  description = "RDS Aurora cluster port"
  value       = aws_rds_cluster.main.port
}

output "cluster_arn" {
  description = "RDS Aurora cluster ARN"
  value       = aws_rds_cluster.main.arn
}

output "cluster_hosted_zone_id" {
  description = "RDS Aurora cluster hosted zone ID"
  value       = aws_rds_cluster.main.hosted_zone_id
}

output "cluster_resource_id" {
  description = "RDS Aurora cluster resource ID"
  value       = aws_rds_cluster.main.cluster_resource_id
}

output "cluster_database_name" {
  description = "RDS Aurora cluster database name"
  value       = aws_rds_cluster.main.database_name
}

output "cluster_master_username" {
  description = "RDS Aurora cluster master username"
  value       = aws_rds_cluster.main.master_username
  sensitive   = true
}

output "cluster_master_password" {
  description = "RDS Aurora cluster master password"
  value       = var.db_password != "" ? var.db_password : random_password.db_password[0].result
  sensitive   = true
}

output "cluster_instance_endpoints" {
  description = "RDS Aurora cluster instance endpoints"
  value       = aws_rds_cluster_instance.main[*].endpoint
}

output "cluster_instance_identifiers" {
  description = "RDS Aurora cluster instance identifiers"
  value       = aws_rds_cluster_instance.main[*].identifier
}

output "db_subnet_group_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_arn" {
  description = "DB subnet group ARN"
  value       = aws_db_subnet_group.main.arn
}

output "parameter_group_name" {
  description = "DB parameter group name"
  value       = aws_rds_cluster_parameter_group.main.name
}

output "parameter_group_arn" {
  description = "DB parameter group ARN"
  value       = aws_rds_cluster_parameter_group.main.arn
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN for database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "secrets_manager_secret_name" {
  description = "Secrets Manager secret name for database credentials"
  value       = aws_secretsmanager_secret.db_credentials.name
}

output "enhanced_monitoring_iam_role_arn" {
  description = "IAM role ARN for enhanced monitoring"
  value       = aws_iam_role.rds_enhanced_monitoring.arn
}

output "cloudwatch_alarm_cpu_arn" {
  description = "CloudWatch alarm ARN for CPU utilization"
  value       = aws_cloudwatch_metric_alarm.database_cpu.arn
}

output "cloudwatch_alarm_connections_arn" {
  description = "CloudWatch alarm ARN for database connections"
  value       = aws_cloudwatch_metric_alarm.database_connections.arn
}
