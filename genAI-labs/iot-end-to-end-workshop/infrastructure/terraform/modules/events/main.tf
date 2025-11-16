resource "aws_iotevents_input" "input" {
  name = "${var.name_prefix}-events-input"
  tags = var.tags

  input_definition {
    attributes {
      json_path = "$.deviceId"
    }
    attributes {
      json_path = "$.tempC"
    }
    attributes {
      json_path = "$.status"
    }
  }
}

resource "aws_iam_role" "events_role" {
  name = "${var.name_prefix}-events-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "iotevents.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
  tags = var.tags
}

resource "aws_iotevents_detector_model" "detector" {
  detector_model_name = "${var.name_prefix}-detector"
  role_arn            = aws_iam_role.events_role.arn

  detector_model_definition {
    initial_state_name = "normal"

    state {
      state_name = "normal"
      on_input {
        transition_events {
          event_name = "temp_high"
          condition  = "currentInput(\"${aws_iotevents_input.input.name}\") AND (input.tempC > 35)"
          next_state = "alarm"
        }
      }
    }

    state {
      state_name = "alarm"
      on_input {
        transition_events {
          event_name = "temp_ok"
          condition  = "currentInput(\"${aws_iotevents_input.input.name}\") AND (input.tempC <= 35)"
          next_state = "normal"
        }
      }
    }
  }

  tags = var.tags
}

output "events_input_name" {
  value = aws_iotevents_input.input.name
}

output "detector_model_name" {
  value = aws_iotevents_detector_model.detector.detector_model_name
}


