# Module 5: Audience Intelligence

## Learning Objectives

By the end of this module, you will be able to:

- Collect and process audience engagement events
- Build a data lake for audience analytics
- Create engagement and churn prediction models
- Generate AI-powered audience insights with Bedrock
- Build real-time analytics dashboards
- Optimize content strategy based on audience behavior

## Prerequisites

- Completed Module 4: Automated Content Generation
- Content published and generating engagement data
- Access to Amazon Kinesis or Kinesis Data Firehose
- Access to Amazon SageMaker
- Access to Amazon QuickSight (optional)
- Basic understanding of data analytics

## Duration

**Estimated Time**: 90 minutes

## Step 1: Set Up Engagement Event Collection

### 1.1 Define Event Schema

```python
# schemas/engagement_event.py
"""
Engagement event schema for audience analytics
"""
engagement_event_schema = {
    "event_id": "string",
    "user_id": "string",
    "content_id": "string",
    "event_type": "string",  # view, like, share, comment, complete, skip
    "timestamp": "string",  # ISO 8601
    "platform": "string",  # twitter, instagram, facebook, etc.
    "device_type": "string",  # mobile, desktop, tablet
    "location": {
        "country": "string",
        "region": "string",
        "city": "string"
    },
    "session_id": "string",
    "metadata": {
        "view_duration": "integer",  # seconds
        "completion_rate": "float",  # 0.0 to 1.0
        "interaction_count": "integer"
    }
}
```

### 1.2 Create Event Ingestion Lambda

```python
# lambda/engagement_event_ingestion.py
import json
import boto3
import os
from datetime import datetime

firehose = boto3.client('firehose', region_name=os.environ['AWS_REGION'])
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Ingest engagement events and send to Kinesis Firehose
    """
    # Parse API Gateway event
    body = json.loads(event.get('body', '{}'))
    events = body.get('events', [])
    
    # Validate and enrich events
    enriched_events = []
    for event_data in events:
        # Add server-side metadata
        event_data['ingestion_timestamp'] = datetime.now().isoformat()
        event_data['event_id'] = event_data.get('event_id', generate_event_id())
        
        # Validate required fields
        if validate_event(event_data):
            enriched_events.append(event_data)
    
    # Send to Kinesis Firehose
    records = []
    for event in enriched_events:
        records.append({
            'Data': json.dumps(event).encode('utf-8')
        })
    
    if records:
        # Batch send (max 500 records per request)
        for i in range(0, len(records), 500):
            batch = records[i:i+500]
            firehose.put_record_batch(
                DeliveryStreamName=os.environ['FIREHOSE_STREAM_NAME'],
                Records=batch
            )
    
    # Update real-time metrics in DynamoDB
    update_realtime_metrics(enriched_events)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'ingested': len(enriched_events),
            'failed': len(events) - len(enriched_events)
        })
    }

def validate_event(event):
    """Validate engagement event"""
    required_fields = ['user_id', 'content_id', 'event_type', 'timestamp']
    return all(field in event for field in required_fields)

def generate_event_id():
    """Generate unique event ID"""
    return f"evt-{datetime.now().timestamp()}-{os.urandom(4).hex()}"

def update_realtime_metrics(events):
    """Update real-time metrics in DynamoDB"""
    table = dynamodb.Table('realtime-metrics')
    
    # Aggregate by content_id
    content_metrics = {}
    for event in events:
        content_id = event['content_id']
        if content_id not in content_metrics:
            content_metrics[content_id] = {
                'views': 0,
                'likes': 0,
                'shares': 0,
                'comments': 0,
                'completions': 0
            }
        
        event_type = event['event_type']
        if event_type in content_metrics[content_id]:
            content_metrics[content_id][event_type + 's'] += 1
    
    # Update DynamoDB
    for content_id, metrics in content_metrics.items():
        table.update_item(
            Key={'content_id': content_id},
            UpdateExpression='ADD views :v, likes :l, shares :s, comments :c, completions :comp',
            ExpressionAttributeValues={
                ':v': metrics.get('views', 0),
                ':l': metrics.get('likes', 0),
                ':s': metrics.get('shares', 0),
                ':c': metrics.get('comments', 0),
                ':comp': metrics.get('completions', 0)
            }
        )
```

### 1.3 Configure Kinesis Data Firehose

```bash
# Create Firehose delivery stream
aws firehose create-delivery-stream \
  --delivery-stream-name media-engagement-events \
  --s3-destination-configuration file://config/firehose-s3-config.json

# Firehose S3 configuration
cat > config/firehose-s3-config.json <<EOF
{
  "RoleARN": "arn:aws:iam::ACCOUNT_ID:role/FirehoseDeliveryRole",
  "BucketARN": "arn:aws:s3:::media-dev-data-lake",
  "Prefix": "engagement-events/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
  "BufferingHints": {
    "SizeInMBs": 5,
    "IntervalInSeconds": 60
  },
  "CompressionFormat": "GZIP",
  "DataFormatConversionConfiguration": {
    "Enabled": true,
    "InputFormatConfiguration": {
      "Deserializer": {
        "OpenXJsonSerDe": {}
      }
    },
    "OutputFormatConfiguration": {
      "Serializer": {
        "ParquetSerDe": {}
      }
    },
    "SchemaConfiguration": {
      "DatabaseName": "media_analytics",
      "TableName": "engagement_events",
      "RoleARN": "arn:aws:iam::ACCOUNT_ID:role/FirehoseDeliveryRole"
    }
  }
}
EOF
```

## Step 2: Build Data Lake with AWS Glue

### 2.1 Create Glue Database and Table

```python
# scripts/create_glue_table.py
import boto3

glue = boto3.client('glue', region_name='us-east-1')

# Create database
try:
    glue.create_database(
        DatabaseInput={
            'Name': 'media_analytics',
            'Description': 'Media engagement analytics data lake'
        }
    )
except glue.exceptions.AlreadyExistsException:
    print("Database already exists")

# Create table for engagement events
table_input = {
    'Name': 'engagement_events',
    'StorageDescriptor': {
        'Columns': [
            {'Name': 'event_id', 'Type': 'string'},
            {'Name': 'user_id', 'Type': 'string'},
            {'Name': 'content_id', 'Type': 'string'},
            {'Name': 'event_type', 'Type': 'string'},
            {'Name': 'timestamp', 'Type': 'timestamp'},
            {'Name': 'platform', 'Type': 'string'},
            {'Name': 'device_type', 'Type': 'string'},
            {'Name': 'location', 'Type': 'struct<country:string,region:string,city:string>'},
            {'Name': 'session_id', 'Type': 'string'},
            {'Name': 'metadata', 'Type': 'struct<view_duration:int,completion_rate:float,interaction_count:int>'}
        ],
        'Location': 's3://media-dev-data-lake/engagement-events/',
        'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
        'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
        'SerdeInfo': {
            'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
        },
        'Compressed': True
    },
    'PartitionKeys': [
        {'Name': 'year', 'Type': 'string'},
        {'Name': 'month', 'Type': 'string'},
        {'Name': 'day', 'Type': 'string'}
    ],
    'TableType': 'EXTERNAL_TABLE',
    'Parameters': {
        'classification': 'parquet',
        'typeOfData': 'file'
    }
}

try:
    glue.create_table(
        DatabaseName='media_analytics',
        TableInput=table_input
    )
    print("Table created successfully")
except glue.exceptions.AlreadyExistsException:
    print("Table already exists")
    # Update table if needed
    glue.update_table(
        DatabaseName='media_analytics',
        TableInput=table_input
    )
```

### 2.2 Create Feature Engineering Job

```python
# scripts/feature_engineering.py
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("MediaEngagementFeatureEngineering") \
    .getOrCreate()

# Read engagement events
events_df = spark.read.parquet("s3://media-dev-data-lake/engagement-events/")

# Feature engineering
features_df = events_df \
    .withColumn("hour_of_day", hour(col("timestamp"))) \
    .withColumn("day_of_week", dayofweek(col("timestamp"))) \
    .withColumn("is_weekend", when(dayofweek(col("timestamp")).isin([1, 7]), 1).otherwise(0)) \
    .groupBy("user_id", "content_id", "platform") \
    .agg(
        count("*").alias("total_interactions"),
        sum(when(col("event_type") == "view", 1).otherwise(0)).alias("view_count"),
        sum(when(col("event_type") == "like", 1).otherwise(0)).alias("like_count"),
        sum(when(col("event_type") == "share", 1).otherwise(0)).alias("share_count"),
        sum(when(col("event_type") == "complete", 1).otherwise(0)).alias("completion_count"),
        avg(col("metadata.view_duration")).alias("avg_view_duration"),
        avg(col("metadata.completion_rate")).alias("avg_completion_rate"),
        max(col("timestamp")).alias("last_interaction")
    ) \
    .withColumn("engagement_score", 
        (col("like_count") * 2 + col("share_count") * 3 + col("completion_count") * 5) / 
        (col("view_count") + 1)
    ) \
    .withColumn("days_since_last_interaction", 
        datediff(current_date(), col("last_interaction"))
    )

# Write features to S3
features_df.write \
    .mode("overwrite") \
    .parquet("s3://media-dev-data-lake/features/user-content-features/")

print("Feature engineering completed")
```

## Step 3: Build Engagement Prediction Model

### 3.1 Train Engagement Model

```python
# sagemaker/train_engagement_model.py
import boto3
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.predictor import Predictor

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Create estimator
estimator = SKLearn(
    entry_point='engagement_model.py',
    role=role,
    instance_type='ml.m5.xlarge',
    framework_version='1.0-1',
    py_version='py3',
    hyperparameters={
        'n_estimators': 100,
        'max_depth': 10,
        'learning_rate': 0.1
    },
    sagemaker_session=sagemaker_session
)

# Train model
estimator.fit({
    'training': 's3://media-dev-data-lake/features/user-content-features/training/',
    'validation': 's3://media-dev-data-lake/features/user-content-features/validation/'
})

# Deploy model
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.t2.medium',
    endpoint_name='engagement-prediction-endpoint'
)
```

### 3.2 Engagement Model Code

```python
# sagemaker/engagement_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def model_fn(model_dir):
    """Load model"""
    model = joblib.load(os.path.join(model_dir, 'model.joblib'))
    return model

def input_fn(request_body, request_content_type):
    """Parse input data"""
    if request_content_type == 'application/json':
        data = pd.read_json(request_body)
        return data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Make predictions"""
    predictions = model.predict(input_data)
    return predictions

def output_fn(prediction, content_type):
    """Format output"""
    return json.dumps({'predictions': prediction.tolist()})

if __name__ == '__main__':
    # Load training data
    train_data = pd.read_csv('/opt/ml/input/data/training/train.csv')
    
    # Prepare features and target
    feature_columns = [
        'total_interactions', 'view_count', 'like_count', 'share_count',
        'avg_view_duration', 'avg_completion_rate', 'days_since_last_interaction',
        'hour_of_day', 'day_of_week', 'is_weekend'
    ]
    
    X = train_data[feature_columns]
    y = train_data['engagement_score']
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=10,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    
    print(f"Train R2: {r2_score(y_train, train_pred)}")
    print(f"Val R2: {r2_score(y_val, val_pred)}")
    
    # Save model
    joblib.dump(model, os.path.join('/opt/ml/model', 'model.joblib'))
```

## Step 4: Generate AI-Powered Insights

### 4.1 Create Insights Generator

```python
# lambda/audience_insights_generator.py
import json
import boto3
import os
from datetime import datetime, timedelta

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])
athena = boto3.client('athena', region_name=os.environ['AWS_REGION'])
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Generate AI-powered audience insights
    """
    content_id = event.get('content_id')
    time_range = event.get('time_range', '7d')  # 7d, 30d, 90d
    
    # Query engagement data from Athena
    engagement_data = query_engagement_data(content_id, time_range)
    
    # Get predictions from SageMaker
    predictions = get_engagement_predictions(engagement_data)
    
    # Generate insights with Bedrock
    insights = generate_insights(engagement_data, predictions)
    
    return {
        'statusCode': 200,
        'content_id': content_id,
        'time_range': time_range,
        'engagement_data': engagement_data,
        'predictions': predictions,
        'insights': insights
    }

def query_engagement_data(content_id, time_range):
    """Query engagement data from Athena"""
    days = int(time_range.replace('d', ''))
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = f"""
    SELECT 
        event_type,
        platform,
        device_type,
        location.country as country,
        COUNT(*) as event_count,
        AVG(metadata.view_duration) as avg_duration,
        AVG(metadata.completion_rate) as avg_completion
    FROM media_analytics.engagement_events
    WHERE content_id = '{content_id}'
        AND timestamp >= TIMESTAMP '{start_date}'
    GROUP BY event_type, platform, device_type, location.country
    """
    
    # Execute Athena query
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'media_analytics'},
        ResultConfiguration={'OutputLocation': 's3://media-dev-data-lake/athena-results/'}
    )
    
    query_execution_id = response['QueryExecutionId']
    
    # Wait for query completion and get results
    # (Implementation details omitted for brevity)
    
    return {
        'total_views': 1000,
        'total_likes': 150,
        'total_shares': 50,
        'avg_completion_rate': 0.75,
        'top_platforms': ['instagram', 'twitter', 'facebook'],
        'top_countries': ['US', 'UK', 'CA']
    }

def get_engagement_predictions(engagement_data):
    """Get engagement predictions from SageMaker"""
    # Prepare features
    features = {
        'total_interactions': engagement_data['total_views'],
        'view_count': engagement_data['total_views'],
        'like_count': engagement_data['total_likes'],
        'share_count': engagement_data['total_shares'],
        'avg_completion_rate': engagement_data['avg_completion_rate']
    }
    
    # Invoke SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName='engagement-prediction-endpoint',
        ContentType='application/json',
        Body=json.dumps([features])
    )
    
    predictions = json.loads(response['Body'].read())
    return predictions

def generate_insights(engagement_data, predictions):
    """Generate insights using Bedrock"""
    prompt = f"""Analyze the following audience engagement data and provide actionable insights:

Engagement Data:
{json.dumps(engagement_data, indent=2)}

Predictions:
{json.dumps(predictions, indent=2)}

Provide insights in the following format:
{{
  "summary": "Overall performance summary",
  "strengths": ["strength1", "strength2"],
  "opportunities": ["opportunity1", "opportunity2"],
  "recommendations": [
    {{
      "action": "recommendation text",
      "priority": "high/medium/low",
      "expected_impact": "description"
    }}
  ],
  "trends": ["trend1", "trend2"],
  "audience_insights": {{
    "demographics": "insights about audience demographics",
    "behavior": "insights about audience behavior",
    "preferences": "insights about content preferences"
  }}
}}
"""
    
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    insights_text = result['content'][0]['text']
    insights = json.loads(insights_text)
    
    return insights
```

## Step 5: Build Analytics Dashboard

### 5.1 Create QuickSight Dataset

```python
# scripts/create_quicksight_dataset.py
import boto3

quicksight = boto3.client('quicksight', region_name='us-east-1')

# Create data source
data_source = quicksight.create_data_source(
    AwsAccountId='ACCOUNT_ID',
    DataSourceId='media-engagement-s3',
    Name='Media Engagement S3',
    Type='S3',
    DataSourceParameters={
        'S3Parameters': {
            'ManifestFileLocation': {
                'Bucket': 'media-dev-data-lake',
                'Key': 'quicksight-manifest.json'
            }
        }
    },
    Permissions=[
        {
            'Principal': f'arn:aws:quicksight:us-east-1:ACCOUNT_ID:user/default/USER_NAME',
            'Actions': ['quicksight:DescribeDataSource', 'quicksight:DescribeDataSourcePermissions', 'quicksight:PassDataSource']
        }
    ]
)

# Create dataset
dataset = quicksight.create_data_set(
    AwsAccountId='ACCOUNT_ID',
    DataSetId='media-engagement-dataset',
    Name='Media Engagement Dataset',
    ImportMode='SPICE',  # In-memory for fast queries
    PhysicalTableMap={
        'engagement_table': {
            'S3Source': {
                'DataSourceArn': data_source['Arn'],
                'InputColumns': [
                    {'Name': 'event_id', 'Type': 'STRING'},
                    {'Name': 'user_id', 'Type': 'STRING'},
                    {'Name': 'content_id', 'Type': 'STRING'},
                    {'Name': 'event_type', 'Type': 'STRING'},
                    {'Name': 'timestamp', 'Type': 'DATETIME'},
                    {'Name': 'platform', 'Type': 'STRING'},
                    {'Name': 'engagement_score', 'Type': 'DECIMAL'}
                ]
            }
        }
    },
    Permissions=[
        {
            'Principal': f'arn:aws:quicksight:us-east-1:ACCOUNT_ID:user/default/USER_NAME',
            'Actions': ['quicksight:DescribeDataSet', 'quicksight:DescribeDataSetPermissions', 'quicksight:PassDataSet']
        }
    ]
)
```

### 5.2 Create Dashboard API

```python
# lambda/dashboard_api.py
import json
import boto3

athena = boto3.client('athena', region_name='us-east-1')

def lambda_handler(event, context):
    """
    API for dashboard metrics
    """
    metric_type = event.get('queryStringParameters', {}).get('metric')
    time_range = event.get('queryStringParameters', {}).get('time_range', '7d')
    
    if metric_type == 'engagement_over_time':
        data = get_engagement_over_time(time_range)
    elif metric_type == 'top_content':
        data = get_top_content(time_range)
    elif metric_type == 'platform_performance':
        data = get_platform_performance(time_range)
    elif metric_type == 'audience_demographics':
        data = get_audience_demographics(time_range)
    else:
        data = {'error': 'Invalid metric type'}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }

def get_engagement_over_time(time_range):
    """Get engagement metrics over time"""
    # Query Athena and return time series data
    return {
        'data': [
            {'date': '2024-01-01', 'views': 1000, 'likes': 150, 'shares': 50},
            {'date': '2024-01-02', 'views': 1200, 'likes': 180, 'shares': 60}
        ]
    }
```

## Step 6: Test Audience Intelligence System

### 6.1 Send Test Events

```bash
# Send test engagement events
curl -X POST https://API_ID.execute-api.us-east-1.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "user_id": "user-123",
        "content_id": "content-456",
        "event_type": "view",
        "timestamp": "2024-01-15T10:00:00Z",
        "platform": "instagram",
        "device_type": "mobile",
        "metadata": {
          "view_duration": 30,
          "completion_rate": 0.8
        }
      }
    ]
  }'
```

### 6.2 Generate Insights

```bash
# Generate insights for content
aws lambda invoke \
  --function-name media-audience-insights-generator \
  --payload '{
    "content_id": "content-456",
    "time_range": "7d"
  }' \
  insights_output.json

cat insights_output.json
```

## Best Practices

### Event Collection
- Use consistent event schemas
- Validate events before ingestion
- Implement retry logic for failed events
- Monitor ingestion latency

### Data Lake
- Partition data by date for efficient queries
- Use columnar formats (Parquet) for analytics
- Implement data retention policies
- Regular data quality checks

### Model Training
- Use feature engineering for better predictions
- Regular model retraining with new data
- A/B test model versions
- Monitor model performance metrics

### Insights Generation
- Combine quantitative and qualitative analysis
- Provide actionable recommendations
- Update insights regularly
- Track insight accuracy over time

## Troubleshooting

### Common Issues

**Low Event Ingestion Rate**
- Check Firehose buffer settings
- Verify Lambda concurrency limits
- Monitor API Gateway throttling
- Check S3 write permissions

**Slow Query Performance**
- Optimize Athena queries
- Use appropriate partition columns
- Consider data compression
- Implement query result caching

**Model Prediction Errors**
- Validate input feature format
- Check model endpoint status
- Monitor model drift
- Retrain with recent data

## Next Steps

- **Module 6**: Deploy to production with monitoring
- **Enhancements**: Add real-time streaming analytics
- **Integration**: Connect to content recommendation systems
- **Optimization**: Implement predictive content scheduling

---

**Ready for Module 6? Continue with [Production Deployment](./module-6-deployment.md)!**

