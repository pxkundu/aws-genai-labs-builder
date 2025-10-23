# CloudWatch Module for GitHub Actions CodeBuild

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "codebuild" {
  name              = "/aws/codebuild/${var.name_prefix}"
  retention_in_days = var.log_retention_days

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-codebuild-logs"
  })
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.name_prefix}-codebuild-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/CodeBuild", "Duration", "ProjectName", var.codebuild_project_name],
            [".", "Builds", ".", "."],
            [".", "FailedBuilds", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "CodeBuild Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/CodeBuild", "Builds", "ProjectName", var.codebuild_project_name],
            [".", "FailedBuilds", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Build Success Rate"
          period  = 300
        }
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "build_failure_rate" {
  alarm_name          = "${var.name_prefix}-build-failure-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FailedBuilds"
  namespace           = "AWS/CodeBuild"
  period              = "300"
  statistic           = "Sum"
  threshold           = "3"
  alarm_description   = "This metric monitors build failures"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ProjectName = var.codebuild_project_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "build_duration" {
  alarm_name          = "${var.name_prefix}-build-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/CodeBuild"
  period              = "300"
  statistic           = "Average"
  threshold           = "1800"  # 30 minutes
  alarm_description   = "This metric monitors build duration"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ProjectName = var.codebuild_project_name
  }

  tags = var.tags
}

# Data source
data "aws_region" "current" {}
