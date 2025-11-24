# Inventory Optimization Guide

## Overview

This guide explains how to implement AI-powered inventory management and demand forecasting for retail e-commerce applications. The solution uses Amazon SageMaker for time-series forecasting and Amazon Bedrock for generating business insights and recommendations.

## Architecture

The inventory optimization system includes:

1. **Data Collection**: Historical sales data from DynamoDB and S3
2. **Forecasting Models**: SageMaker time-series models
3. **GenAI Insights**: Bedrock for business intelligence
4. **Alert System**: EventBridge for automated reordering
5. **Dashboard**: QuickSight for visualization

## Prerequisites

- Historical sales data (minimum 6 months)
- SageMaker endpoint deployed
- Bedrock model access
- DynamoDB tables for inventory
- EventBridge configured

## Step 1: Prepare Historical Data

### 1.1 Data Structure

```python
# Sample data structure
{
    "product_id": "PROD-001",
    "date": "2024-01-01",
    "quantity_sold": 150,
    "price": 29.99,
    "category": "Electronics",
    "season": "Winter",
    "promotion": false
}
```

### 1.2 Load Historical Data

```python
# load_historical_data.py
import boto3
import pandas as pd
from datetime import datetime, timedelta

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def load_historical_sales(product_id: str, months: int = 12):
    """Load historical sales data"""
    
    # Query DynamoDB
    table = dynamodb.Table('retail-sales-history')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    response = table.query(
        KeyConditionExpression='product_id = :pid AND sale_date BETWEEN :start AND :end',
        ExpressionAttributeValues={
            ':pid': product_id,
            ':start': start_date.isoformat(),
            ':end': end_date.isoformat()
        }
    )
    
    return pd.DataFrame(response['Items'])
```

## Step 2: Train Forecasting Model

### 2.1 Prepare Training Data

```python
# prepare_training_data.py
import pandas as pd
import numpy as np

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for time-series forecasting"""
    
    # Create time-based features
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Create lag features
    df['lag_7'] = df['quantity_sold'].shift(7)
    df['lag_30'] = df['quantity_sold'].shift(30)
    
    # Rolling averages
    df['rolling_7'] = df['quantity_sold'].rolling(window=7).mean()
    df['rolling_30'] = df['quantity_sold'].rolling(window=30).mean()
    
    return df
```

### 2.2 Train Model with SageMaker

```python
# train_forecast_model.py
import boto3
import sagemaker
from sagemaker.estimator import Estimator

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Upload training data
training_data_path = sagemaker_session.upload_data(
    path='data/training/forecast_training.csv',
    key_prefix='forecast-training'
)

# Create estimator
estimator = Estimator(
    image_uri='your-ecr-repo/forecast:latest',
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    sagemaker_session=sagemaker_session
)

# Train model
estimator.fit({'training': training_data_path})

# Deploy endpoint
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='retail-forecast-endpoint'
)
```

## Step 3: Implement Forecasting Service

### 3.1 Forecast Service

```python
# forecast_service.py
import boto3
import json
import pandas as pd
from typing import Dict, List, Any

class InventoryForecastService:
    def __init__(self):
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.bedrock = boto3.client('bedrock-runtime')
        self.dynamodb = boto3.resource('dynamodb')
        
        self.inventory_table = self.dynamodb.Table('retail-inventory')
        self.forecasts_table = self.dynamodb.Table('retail-forecasts')
    
    def forecast_demand(self, product_id: str, horizon_days: int = 30) -> Dict[str, Any]:
        """Generate demand forecast for a product"""
        
        # Get historical data
        historical_data = self.get_historical_data(product_id)
        
        # Prepare features
        features = self.prepare_features(historical_data)
        
        # Get ML forecast
        ml_forecast = self.get_ml_forecast(features, horizon_days)
        
        # Generate AI insights
        ai_insights = self.generate_forecast_insights(
            product_id, ml_forecast, historical_data
        )
        
        # Calculate optimal inventory level
        optimal_inventory = self.calculate_optimal_inventory(
            ml_forecast, ai_insights
        )
        
        return {
            'product_id': product_id,
            'forecast_period': horizon_days,
            'predicted_demand': ml_forecast['demand'],
            'confidence_interval': ml_forecast['confidence'],
            'optimal_inventory': optimal_inventory,
            'insights': ai_insights,
            'recommendations': ai_insights.get('recommendations', [])
        }
    
    def get_ml_forecast(self, features: pd.DataFrame, horizon: int) -> Dict:
        """Get forecast from SageMaker model"""
        
        payload = {
            'features': features.to_dict('records'),
            'horizon': horizon
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName='retail-forecast-endpoint',
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        return {
            'demand': result['forecast'],
            'confidence': result['confidence_interval']
        }
    
    def generate_forecast_insights(self, product_id: str, 
                                   forecast: Dict, historical: pd.DataFrame) -> Dict:
        """Generate AI-powered business insights"""
        
        # Calculate statistics
        avg_demand = historical['quantity_sold'].mean()
        trend = 'increasing' if forecast['demand'] > avg_demand else 'decreasing'
        
        prompt = f"""
        Analyze this demand forecast and provide business insights:
        
        Product: {product_id}
        Forecasted Demand: {forecast['demand']} units
        Confidence: {forecast['confidence']}%
        Historical Average: {avg_demand} units
        Trend: {trend}
        
        Provide:
        1. Key factors driving this forecast
        2. Business recommendations
        3. Risk factors to monitor
        4. Optimal inventory level suggestions
        
        Format as JSON with keys: factors, recommendations, risks, inventory_suggestions
        """
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        return json.loads(result['content'][0]['text'])
    
    def calculate_optimal_inventory(self, forecast: Dict, insights: Dict) -> int:
        """Calculate optimal inventory level"""
        
        base_demand = forecast['demand']
        safety_stock = base_demand * 0.2  # 20% safety stock
        lead_time_demand = base_demand * 0.1  # 10% for lead time
        
        optimal = int(base_demand + safety_stock + lead_time_demand)
        
        # Adjust based on AI insights
        if insights.get('risks'):
            optimal = int(optimal * 1.1)  # Increase by 10% if risks identified
        
        return optimal
```

## Step 4: Automated Reordering

### 4.1 Reorder Logic

```python
# reorder_service.py
import boto3
from forecast_service import InventoryForecastService

class ReorderService:
    def __init__(self):
        self.forecast_service = InventoryForecastService()
        self.eventbridge = boto3.client('events')
        self.dynamodb = boto3.resource('dynamodb')
        
        self.inventory_table = self.dynamodb.Table('retail-inventory')
    
    def check_reorder_needed(self, product_id: str) -> bool:
        """Check if reorder is needed"""
        
        # Get current inventory
        inventory = self.inventory_table.get_item(
            Key={'product_id': product_id}
        )['Item']
        
        current_stock = inventory['current_stock']
        reorder_point = inventory['reorder_point']
        
        # Get forecast
        forecast = self.forecast_service.forecast_demand(product_id)
        optimal_inventory = forecast['optimal_inventory']
        
        # Check if reorder needed
        if current_stock <= reorder_point:
            return True
        
        # Check if forecast suggests higher inventory
        if optimal_inventory > current_stock * 1.5:
            return True
        
        return False
    
    def trigger_reorder(self, product_id: str):
        """Trigger reorder event"""
        
        forecast = self.forecast_service.forecast_demand(product_id)
        
        # Send event to EventBridge
        self.eventbridge.put_events(
            Entries=[{
                'Source': 'retail.inventory',
                'DetailType': 'Reorder Required',
                'Detail': json.dumps({
                    'product_id': product_id,
                    'current_stock': self.get_current_stock(product_id),
                    'optimal_inventory': forecast['optimal_inventory'],
                    'recommended_order_quantity': forecast['optimal_inventory'],
                    'urgency': 'high' if forecast['confidence'] > 0.8 else 'medium'
                })
            }]
        )
```

## Step 5: Monitoring and Alerts

### 5.1 CloudWatch Metrics

```python
# metrics.py
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_forecast_metrics(product_id: str, forecast: Dict):
    """Publish forecast metrics to CloudWatch"""
    
    cloudwatch.put_metric_data(
        Namespace='Retail/Inventory',
        MetricData=[
            {
                'MetricName': 'ForecastedDemand',
                'Value': forecast['demand'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ProductId', 'Value': product_id}
                ]
            },
            {
                'MetricName': 'ForecastConfidence',
                'Value': forecast['confidence'],
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'ProductId', 'Value': product_id}
                ]
            }
        ]
    )
```

## Best Practices

1. **Data Quality**: Ensure clean, consistent historical data
2. **Model Retraining**: Retrain models monthly or quarterly
3. **Safety Stock**: Maintain appropriate safety stock levels
4. **Monitoring**: Track forecast accuracy and adjust models
5. **Business Rules**: Combine ML forecasts with business knowledge

## Troubleshooting

### Low Forecast Accuracy

- Review historical data quality
- Check for data anomalies
- Retrain model with more data
- Adjust feature engineering

### High Inventory Costs

- Optimize safety stock levels
- Improve forecast accuracy
- Implement just-in-time ordering
- Review supplier lead times

## Next Steps

- Implement multi-product forecasting
- Add seasonal adjustment models
- Integrate with supplier systems
- Build inventory optimization dashboard

---

**For more details, see the [Workshop Module 3](../workshop/module-3-inventory.md)**

