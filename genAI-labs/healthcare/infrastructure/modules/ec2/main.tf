# EC2 Module - Healthcare ChatGPT Clone
# This module creates EC2 instance for OpenWebUI and backend API

# Data source for latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script for EC2 initialization
locals {
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    OPENWEBUI_PORT          = var.openwebui_port
    API_PORT                = var.api_port
    DB_HOST                 = var.db_endpoint
    DB_PORT                 = "5432"
    DB_NAME                 = var.db_name
    DB_USER                 = var.db_username
    DB_PASSWORD             = var.db_password
    S3_BUCKET               = var.knowledge_base_bucket
    OPENAI_API_KEY          = var.openai_api_key
    AWS_REGION              = var.aws_region
    ENVIRONMENT             = var.environment
    PROJECT_NAME            = var.project_name
  }))
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = var.ami_id != "" ? var.ami_id : data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = var.security_group_ids
  subnet_id              = var.public_subnet_ids[0]
  iam_instance_profile   = data.aws_iam_instance_profile.ec2_profile.name

  user_data = local.user_data

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 50
    delete_on_termination = true
    encrypted             = true

    tags = merge(var.tags, {
      Name = "${var.environment}-ec2-root-volume"
    })
  }

  # Additional EBS volume for application data
  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_type           = "gp3"
    volume_size           = 100
    delete_on_termination = true
    encrypted             = true

    tags = merge(var.tags, {
      Name = "${var.environment}-ec2-data-volume"
    })
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-instance"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# IAM Instance Profile (referenced from security module)
data "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.environment}-ec2-profile"
}

# Elastic IP for the instance
resource "aws_eip" "main" {
  instance = aws_instance.main.id
  domain   = "vpc"

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-eip"
  })
}

# CloudWatch Log Group for EC2 logs
resource "aws_cloudwatch_log_group" "ec2_logs" {
  name              = "/aws/ec2/${var.environment}-${var.project_name}"
  retention_in_days = 30

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-logs"
  })
}

# CloudWatch Agent configuration
resource "aws_ssm_parameter" "cloudwatch_config" {
  name  = "/${var.environment}/${var.project_name}/cloudwatch-config"
  type  = "String"
  value = jsonencode({
    logs = {
      logs_collected = {
        files = {
          collect_list = [
            {
              file_path = "/var/log/cloud-init-output.log"
              log_group_name = "/aws/ec2/${var.environment}-${var.project_name}"
              log_stream_name = "{instance_id}/cloud-init-output.log"
            },
            {
              file_path = "/var/log/docker.log"
              log_group_name = "/aws/ec2/${var.environment}-${var.project_name}"
              log_stream_name = "{instance_id}/docker.log"
            },
            {
              file_path = "/var/log/openwebui.log"
              log_group_name = "/aws/ec2/${var.environment}-${var.project_name}"
              log_stream_name = "{instance_id}/openwebui.log"
            }
          ]
        }
      }
    }
    metrics = {
      namespace = "CWAgent"
      metrics_collected = {
        cpu = {
          measurement = ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"]
          metrics_collection_interval = 60
        }
        disk = {
          measurement = ["used_percent"]
          metrics_collection_interval = 60
          resources = ["*"]
        }
        diskio = {
          measurement = ["io_time", "read_bytes", "write_bytes", "reads", "writes"]
          metrics_collection_interval = 60
          resources = ["*"]
        }
        mem = {
          measurement = ["mem_used_percent"]
          metrics_collection_interval = 60
        }
        netstat = {
          measurement = ["tcp_established", "tcp_time_wait"]
          metrics_collection_interval = 60
        }
        swap = {
          measurement = ["swap_used_percent"]
          metrics_collection_interval = 60
        }
      }
    }
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-cloudwatch-config"
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.environment}-ec2-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EC2 CPU utilization"
  alarm_actions       = []

  dimensions = {
    InstanceId = aws_instance.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-high-cpu-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${var.environment}-ec2-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "CWAgent"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EC2 memory utilization"
  alarm_actions       = []

  dimensions = {
    InstanceId = aws_instance.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-high-memory-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "high_disk" {
  alarm_name          = "${var.environment}-ec2-high-disk"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors EC2 disk utilization"
  alarm_actions       = []

  dimensions = {
    InstanceId = aws_instance.main.id
    device     = "/dev/nvme0n1"
    fstype     = "ext4"
    path       = "/"
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-high-disk-alarm"
  })
}

# Auto Scaling Group (optional, for future scaling)
resource "aws_launch_template" "main" {
  name_prefix   = "${var.environment}-"
  image_id      = var.ami_id != "" ? var.ami_id : data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_pair_name

  vpc_security_group_ids = var.security_group_ids

  iam_instance_profile {
    name = data.aws_iam_instance_profile.ec2_profile.name
  }

  user_data = local.user_data

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      volume_type           = "gp3"
      volume_size           = 50
      delete_on_termination = true
      encrypted             = true
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.tags, {
      Name = "${var.environment}-ec2-template"
    })
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-launch-template"
  })
}
