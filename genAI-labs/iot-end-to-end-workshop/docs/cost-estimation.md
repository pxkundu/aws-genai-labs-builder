# Cost Estimation Guide

This document provides cost estimates for running the AWS IoT End-to-End Workshop infrastructure.

## Service Cost Breakdown

### AWS IoT Core
- **Message Pricing**: $1.00 per million messages (first 5 billion messages/month)
- **Device Shadow**: $1.25 per million shadow operations
- **Device Registry**: Free (first 1 million things)
- **Rules Engine**: $0.15 per million rule evaluations
- **Estimated Monthly Cost**: 
  - 1 device, 1 message/minute = ~43,200 messages/month = **$0.04/month**
  - 100 devices, 1 message/minute = ~4.32M messages/month = **$4.32/month**

### Amazon Kinesis Data Streams
- **Shard Hours**: $0.015 per shard-hour
- **PUT Payload Units**: $0.014 per million units
- **Estimated Monthly Cost**:
  - 1 shard, 24/7 = 730 shard-hours = **$10.95/month**
  - Data ingestion: ~$0.01/month for typical IoT workloads

### Amazon Kinesis Data Firehose
- **Data Ingestion**: $0.029 per GB ingested
- **Data Delivery to S3**: Free
- **Estimated Monthly Cost**:
  - 1GB/month = **$0.03/month**
  - 10GB/month = **$0.29/month**

### Amazon S3
- **Storage**: $0.023 per GB/month (Standard storage)
- **PUT Requests**: $0.005 per 1,000 requests
- **GET Requests**: $0.0004 per 1,000 requests
- **Estimated Monthly Cost**:
  - 10GB storage = **$0.23/month**
  - 100K PUT requests = **$0.50/month**

### AWS Lambda
- **Requests**: First 1 million requests/month free, then $0.20 per million
- **Compute**: $0.0000166667 per GB-second
- **Estimated Monthly Cost**:
  - 1M invocations, 128MB, 1s duration = **~$0.20/month**
  - Typical IoT processing: **$0.10-$1.00/month**

### AWS IoT Analytics
- **Message Ingestion**: $0.50 per million messages
- **Data Storage**: $0.30 per GB/month
- **Query Execution**: $0.005 per query
- **Estimated Monthly Cost**:
  - 1M messages/month = **$0.50/month**
  - 1GB storage = **$0.30/month**
  - 100 queries/month = **$0.50/month**
  - **Total: ~$1.30/month**

### AWS IoT Events
- **Input Messages**: $0.15 per million messages
- **Detector Evaluations**: $0.15 per million evaluations
- **Estimated Monthly Cost**:
  - 1M messages/month = **$0.15/month**
  - 1M evaluations/month = **$0.15/month**
  - **Total: ~$0.30/month**

### AWS IoT Device Defender
- **Audit**: $0.10 per audit check
- **Metrics**: $0.10 per million metrics
- **Estimated Monthly Cost**:
  - 1 audit/month = **$0.10/month**
  - 1M metrics/month = **$0.10/month**
  - **Total: ~$0.20/month**

### Amazon CloudWatch
- **Custom Metrics**: $0.30 per metric/month (first 10 free)
- **Dashboard**: $3.00 per dashboard/month (first 3 free)
- **Logs Ingestion**: $0.50 per GB
- **Estimated Monthly Cost**:
  - 5 custom metrics = **Free**
  - 1 dashboard = **Free**
  - 1GB logs = **$0.50/month**

### Amazon OpenSearch Service (Optional)
- **Instance**: t3.small.search = ~$0.036/hour = **$26.28/month**
- **Storage**: $0.10 per GB/month
- **Estimated Monthly Cost**: **$30-50/month** (for small cluster)

## Total Monthly Cost Estimates

### Small Scale (1-10 devices)
- IoT Core: $0.10
- Kinesis: $11.00
- Firehose: $0.10
- S3: $1.00
- Lambda: $0.50
- IoT Analytics: $1.50
- IoT Events: $0.30
- Device Defender: $0.20
- CloudWatch: $0.50
- **Total: ~$15-20/month**

### Medium Scale (100 devices)
- IoT Core: $5.00
- Kinesis: $11.00
- Firehose: $1.00
- S3: $5.00
- Lambda: $2.00
- IoT Analytics: $5.00
- IoT Events: $1.00
- Device Defender: $0.50
- CloudWatch: $2.00
- **Total: ~$32-35/month**

### Large Scale (1,000 devices)
- IoT Core: $50.00
- Kinesis: $22.00 (2 shards)
- Firehose: $10.00
- S3: $20.00
- Lambda: $10.00
- IoT Analytics: $20.00
- IoT Events: $5.00
- Device Defender: $2.00
- CloudWatch: $5.00
- **Total: ~$144-150/month**

## Cost Optimization Tips

1. **Kinesis Sharding**: Use minimum shards (1) for low-volume workloads
2. **S3 Lifecycle Policies**: Move old data to Glacier/Deep Archive after 30 days
3. **Lambda Memory**: Right-size Lambda functions (128MB is often sufficient)
4. **IoT Analytics**: Use scheduled queries instead of continuous queries when possible
5. **CloudWatch Logs**: Set retention policies (7-30 days) to reduce storage costs
6. **Device Defender**: Run audits on-demand or weekly instead of daily
7. **OpenSearch**: Only enable if you need search/visualization capabilities

## AWS Free Tier

Many services have free tier allowances:
- **IoT Core**: 250,000 messages/month free (first 12 months)
- **Lambda**: 1M requests/month free (permanent)
- **S3**: 5GB storage, 20K GET requests/month free (first 12 months)
- **CloudWatch**: 10 custom metrics, 3 dashboards free (permanent)

## Cost Monitoring

Use AWS Cost Explorer and set up billing alerts:
- Create CloudWatch billing alarms
- Use AWS Cost Anomaly Detection
- Review monthly cost reports

## Cleanup

Always destroy resources when not in use:
```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```

This will eliminate all ongoing costs.

