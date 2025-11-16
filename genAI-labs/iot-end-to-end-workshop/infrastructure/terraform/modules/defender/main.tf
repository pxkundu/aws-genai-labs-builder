resource "aws_iot_security_profile" "baseline" {
  name = "${var.name_prefix}-defender-profile"

  behaviors {
    name = "PublishRateLimit"
    metric = "aws:num-messages-published"
    criteria {
      comparison_operator = "less-than-equals"
      value {
        count = 120
      }
      duration_seconds = 300
    }
  }

  additional_metrics_to_retain_v2 = [
    "aws:num-messages-published",
    "aws:incoming-bytes",
    "aws:auth-failures"
  ]

  tags = var.tags
}


