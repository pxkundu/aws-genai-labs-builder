resource "aws_cloudwatch_dashboard" "ingestion" {
  dashboard_name = "${var.name_prefix}-ingestion"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric",
        x = 0, y = 0, width = 12, height = 6,
        properties = {
          metrics = [
            ["AWS/Kinesis", "IncomingRecords", "StreamName", var.kinesis_stream_name]
          ],
          period = 60,
          stat = "Sum",
          region = "${data.aws_region.current.name}",
          title = "Kinesis IncomingRecords"
        }
      },
      {
        type = "metric",
        x = 12, y = 0, width = 12, height = 6,
        properties = {
          metrics = [
            ["AWS/Firehose", "DeliveryToS3.Records", "DeliveryStreamName", var.firehose_delivery_name]
          ],
          period = 60,
          stat = "Sum",
          region = "${data.aws_region.current.name}",
          title = "Firehose DeliveryToS3 Records"
        }
      },
      {
        type = "metric",
        x = 0, y = 6, width = 12, height = 6,
        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", var.lambda_function_name]
          ],
          period = 60,
          stat = "Sum",
          region = "${data.aws_region.current.name}",
          title = "Lambda Errors"
        }
      }
    ]
  })
}

data "aws_region" "current" {}


