# RDS Module - Healthcare ChatGPT Clone
# This module creates RDS Aurora PostgreSQL cluster for chat data storage

# Random password for database if not provided
resource "random_password" "db_password" {
  count   = var.db_password == "" ? 1 : 0
  length  = 16
  special = true
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.environment}-db-subnet-group"
  })
}

# DB Parameter Group
resource "aws_rds_cluster_parameter_group" "main" {
  family = "aurora-postgresql15"
  name   = "${var.environment}-aurora-postgresql15-params"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-aurora-postgresql15-params"
  })
}

# DB Cluster Parameter Group
resource "aws_rds_cluster_parameter_group" "cluster" {
  family = "aurora-postgresql15"
  name   = "${var.environment}-aurora-postgresql15-cluster-params"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-aurora-postgresql15-cluster-params"
  })
}

# Aurora PostgreSQL Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "${var.environment}-aurora-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = var.db_engine_version
  database_name           = var.db_name
  master_username         = var.db_username
  master_password         = var.db_password != "" ? var.db_password : random_password.db_password[0].result
  backup_retention_period = var.backup_retention_period
  preferred_backup_window = var.backup_window
  preferred_maintenance_window = var.maintenance_window
  db_subnet_group_name    = aws_db_subnet_group.main.name
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster.name
  vpc_security_group_ids  = var.security_group_ids
  storage_encrypted       = true
  deletion_protection     = var.enable_deletion_protection
  skip_final_snapshot     = !var.enable_deletion_protection
  final_snapshot_identifier = var.enable_deletion_protection ? "${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Serverless v2 configuration
  serverlessv2_scaling_configuration {
    max_capacity = var.max_capacity
    min_capacity = var.min_capacity
  }

  # Enable Performance Insights
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  tags = merge(var.tags, {
    Name = "${var.environment}-aurora-cluster"
  })
}

# Aurora PostgreSQL Cluster Instances
resource "aws_rds_cluster_instance" "main" {
  count              = 2
  identifier         = "${var.environment}-aurora-instance-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  # Performance Insights
  performance_insights_enabled = var.enable_performance_insights
  performance_insights_retention_period = var.enable_performance_insights ? 7 : null
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn

  tags = merge(var.tags, {
    Name = "${var.environment}-aurora-instance-${count.index + 1}"
  })
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${var.environment}-rds-enhanced-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-rds-enhanced-monitoring-role"
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# DB Snapshot (for development/testing)
resource "aws_db_cluster_snapshot" "main" {
  count            = var.enable_deletion_protection ? 0 : 1
  db_cluster_identifier          = aws_rds_cluster.main.id
  db_cluster_snapshot_identifier = "${var.environment}-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = merge(var.tags, {
    Name = "${var.environment}-db-snapshot"
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.environment}-rds-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = []

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-rds-cpu-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.environment}-rds-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS database connections"
  alarm_actions       = []

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-rds-connections-alarm"
  })
}

# Secrets Manager Secret for Database Credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.environment}-rds-credentials"
  description = "Database credentials for ${var.environment} environment"

  tags = merge(var.tags, {
    Name = "${var.environment}-rds-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password != "" ? var.db_password : random_password.db_password[0].result
    engine   = "postgres"
    host     = aws_rds_cluster.main.endpoint
    port     = aws_rds_cluster.main.port
    dbname   = var.db_name
  })
}
