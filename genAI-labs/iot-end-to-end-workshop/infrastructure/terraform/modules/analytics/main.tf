resource "aws_iotanalytics_channel" "channel" {
  name = "${var.name_prefix}-channel"
  tags = var.tags

  # The channel can be connected via rules or pipeline activities.
}

resource "aws_iotanalytics_datastore" "datastore" {
  name = "${var.name_prefix}-datastore"
  retention_period {
    number_of_days = 7
    unlimited      = false
  }
  tags = var.tags
}

resource "aws_iotanalytics_pipeline" "pipeline" {
  name = "${var.name_prefix}-pipeline"

  activity {
    channel {
      name    = "from_channel"
      channel_name = aws_iotanalytics_channel.channel.name
    }
  }

  activity {
    lambda {
      name        = "noop"
      batch_size  = 100
      lambda_name = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:does-not-exist"
    }
  }

  activity {
    datastore {
      name          = "to_store"
      datastore_name = aws_iotanalytics_datastore.datastore.name
    }
  }

  tags = var.tags
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_iotanalytics_dataset" "dataset" {
  name = "${var.name_prefix}-dataset"
  action {
    action_name = "sqlAction"
    query_action {
      sql_query = "SELECT * FROM ${aws_iotanalytics_datastore.datastore.name} LIMIT 100"
    }
  }
  tags = var.tags
}

output "datastore_name" {
  value = aws_iotanalytics_datastore.datastore.name
}


