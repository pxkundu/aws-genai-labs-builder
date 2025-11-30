# Content Discovery & Search Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the intelligent content discovery and search system for media and entertainment applications. The system combines semantic search using Bedrock embeddings, visual search using Amazon Rekognition, and personalized recommendations.

## Architecture

The Content Discovery system consists of:

1. **Embedding Generation**: Bedrock Titan embeddings for semantic search
2. **Visual Feature Extraction**: Rekognition for image/video analysis
3. **Search Index**: OpenSearch for vector and keyword search
4. **Discovery API**: Unified API for semantic, visual, and hybrid search
5. **Personalization**: User preference-based ranking
6. **Caching Layer**: DynamoDB for real-time metrics

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured (Titan Embeddings)
- Amazon OpenSearch Service domain (or compatible vector database)
- Amazon Rekognition access
- S3 buckets with content assets
- DynamoDB tables for metadata

## Step 1: Set Up OpenSearch Domain

### 1.1 Create OpenSearch Domain

```bash
# Create OpenSearch domain via AWS Console or CLI
aws opensearch create-domain \
  --domain-name media-content-search \
  --cluster-config InstanceType=t3.small.search,InstanceCount=2 \
  --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=20 \
  --access-policies file://config/opensearch-access-policy.json \
  --engine-version OpenSearch_2.11 \
  --node-to-node-encryption-options Enabled=true \
  --encryption-at-rest-options Enabled=true \
  --domain-endpoint-options EnforceHTTPS=true,TLSSecurityPolicy=Policy-Min-TLS-1-2-2019-07 \
  --advanced-security-options Enabled=true,InternalUserDatabaseEnabled=true,MasterUserName=admin,MasterUserPassword=CHANGE_ME

# Wait for domain to be active
aws opensearch describe-domain --domain-name media-content-search \
  --query 'DomainStatus.Processing' --output text
```

### 1.2 Create Index Mapping

```python
# scripts/create_opensearch_index.py
import boto3
import json
import requests
from requests.auth import HTTPBasicAuth

opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
username = os.environ['OPENSEARCH_USERNAME']
password = os.environ['OPENSEARCH_PASSWORD']

index_name = 'media-content'
index_mapping = {
    'settings': {
        'number_of_shards': 2,
        'number_of_replicas': 1,
        'knn': True,
        'knn.algo_param.ef_search': 100
    },
    'mappings': {
        'properties': {
            'content_id': {'type': 'keyword'},
            'title': {'type': 'text', 'analyzer': 'standard'},
            'description': {'type': 'text', 'analyzer': 'standard'},
            'tags': {'type': 'keyword'},
            'content_type': {'type': 'keyword'},
            'embedding': {
                'type': 'knn_vector',
                'dimension': 1536,  # Titan embeddings dimension
                'method': {
                    'name': 'hnsw',
                    'space_type': 'cosinesimil',
                    'engine': 'nmslib'
                }
            },
            'visual_features': {
                'properties': {
                    'labels': {'type': 'keyword'},
                    'faces_count': {'type': 'integer'},
                    'text_detected': {'type': 'text'}
                }
            },
            'metadata': {
                'properties': {
                    'duration': {'type': 'float'},
                    'created_date': {'type': 'date'},
                    'genre': {'type': 'keyword'},
                    'rating': {'type': 'float'}
                }
            }
        }
    }
}

# Create index
response = requests.put(
    f'https://{opensearch_endpoint}/{index_name}',
    auth=HTTPBasicAuth(username, password),
    json=index_mapping,
    headers={'Content-Type': 'application/json'}
)

print(f"Index created: {response.status_code}")
```

## Step 2: Deploy Embedding Generation

### 2.1 Create Embedding Lambda

```bash
# Package Lambda function
cd lambda/embedding_generator
zip -r embedding_generator.zip embedding_generator.py

# Create Lambda function
aws lambda create-function \
  --function-name media-embedding-generator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler embedding_generator.lambda_handler \
  --zip-file fileb://embedding_generator.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{AWS_REGION=us-east-1}"

# Grant Bedrock permissions
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### 2.2 Batch Embedding Generation

```python
# scripts/generate_content_embeddings.py
import boto3
import json
from concurrent.futures import ThreadPoolExecutor

lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

def process_content_item(item):
    """Generate embedding for a single content item"""
    content_id = item['content_id']
    title = item.get('title', '')
    description = item.get('description', '')
    tags = ' '.join(item.get('tags', []))
    
    # Combine text for embedding
    text = f"{title} {description} {tags}"
    
    # Invoke embedding Lambda
    response = lambda_client.invoke(
        FunctionName='media-embedding-generator',
        Payload=json.dumps({
            'text': text,
            'content_id': content_id
        })
    )
    
    result = json.loads(response['Payload'].read())
    return result

# Load content from DynamoDB
table = dynamodb.Table('media-content-metadata')
items = table.scan()['Items']

# Generate embeddings in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_content_item, items))

print(f"Generated {len(results)} embeddings")
```

## Step 3: Set Up Visual Feature Extraction

### 3.1 Create Rekognition Lambda

```bash
# Package Lambda function
cd lambda/rekognition_feature_extractor
zip -r rekognition_feature_extractor.zip rekognition_feature_extractor.py

# Create Lambda function
aws lambda create-function \
  --function-name media-rekognition-extractor \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler rekognition_feature_extractor.lambda_handler \
  --zip-file fileb://rekognition_feature_extractor.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:rekognition-notifications,
    REKOGNITION_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/RekognitionServiceRole
  }"

# Grant Rekognition permissions
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonRekognitionFullAccess
```

### 3.2 Configure SNS for Video Analysis

```bash
# Create SNS topic
aws sns create-topic --name rekognition-notifications

# Subscribe Lambda to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:rekognition-notifications \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:ACCOUNT_ID:function:media-rekognition-video-handler
```

## Step 4: Deploy Search Functions

### 4.1 Semantic Search Lambda

```bash
# Package and deploy
cd lambda/semantic_search
zip -r semantic_search.zip semantic_search.py

aws lambda create-function \
  --function-name media-semantic-search \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler semantic_search.lambda_handler \
  --zip-file fileb://semantic_search.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    OPENSEARCH_ENDPOINT=search-media-content-search-xxxxx.us-east-1.es.amazonaws.com,
    OPENSEARCH_USERNAME=admin,
    OPENSEARCH_PASSWORD=CHANGE_ME
  }"
```

### 4.2 Visual Search Lambda

```bash
# Package and deploy
cd lambda/visual_search
zip -r visual_search.zip visual_search.py

aws lambda create-function \
  --function-name media-visual-search \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler visual_search.lambda_handler \
  --zip-file fileb://visual_search.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    OPENSEARCH_ENDPOINT=search-media-content-search-xxxxx.us-east-1.es.amazonaws.com,
    OPENSEARCH_USERNAME=admin,
    OPENSEARCH_PASSWORD=CHANGE_ME
  }"
```

### 4.3 Discovery API Lambda

```bash
# Package and deploy
cd lambda/discovery_api
zip -r discovery_api.zip discovery_api.py

aws lambda create-function \
  --function-name media-discovery-api \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler discovery_api.lambda_handler \
  --zip-file fileb://discovery_api.zip \
  --timeout 30 \
  --memory-size 512
```

## Step 5: Index Content

### 5.1 Index Content Script

```python
# scripts/index_content.py
import boto3
import json
import requests
from requests.auth import HTTPBasicAuth

opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

def index_content_item(item):
    """Index a single content item in OpenSearch"""
    # Get embedding
    embedding_response = lambda_client.invoke(
        FunctionName='media-embedding-generator',
        Payload=json.dumps({
            'text': f"{item.get('title', '')} {item.get('description', '')}",
            'content_id': item['content_id']
        })
    )
    embedding_result = json.loads(embedding_response['Payload'].read())
    
    # Get visual features if available
    visual_features = item.get('visual_features', {})
    
    doc = {
        'content_id': item['content_id'],
        'title': item.get('title', ''),
        'description': item.get('description', ''),
        'tags': item.get('tags', []),
        'content_type': item.get('content_type', 'video'),
        'embedding': embedding_result.get('embedding', []),
        'visual_features': visual_features,
        'metadata': item.get('metadata', {})
    }
    
    response = requests.put(
        f'https://{opensearch_endpoint}/media-content/_doc/{item["content_id"]}',
        auth=HTTPBasicAuth(os.environ['OPENSEARCH_USERNAME'], os.environ['OPENSEARCH_PASSWORD']),
        json=doc,
        headers={'Content-Type': 'application/json'}
    )
    
    return response.status_code

# Load and index all content
table = dynamodb.Table('media-content-metadata')
items = table.scan()['Items']

for item in items:
    status = index_content_item(item)
    print(f"Indexed {item['content_id']}: {status}")
```

## Step 6: Set Up Personalization

### 6.1 User Preference Tracker

```bash
# Create DynamoDB table
aws dynamodb create-table \
  --table-name user-preferences \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create Lambda
cd lambda/user_preference_tracker
zip -r user_preference_tracker.zip user_preference_tracker.py

aws lambda create-function \
  --function-name media-user-preference-tracker \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler user_preference_tracker.lambda_handler \
  --zip-file fileb://user_preference_tracker.zip \
  --timeout 10 \
  --memory-size 256
```

### 6.2 Personalized Search Lambda

```bash
# Package and deploy
cd lambda/personalized_search
zip -r personalized_search.zip personalized_search.py

aws lambda create-function \
  --function-name media-personalized-search \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler personalized_search.lambda_handler \
  --zip-file fileb://personalized_search.zip \
  --timeout 30 \
  --memory-size 512
```

## Step 7: Testing and Validation

### 7.1 Test Semantic Search

```bash
# Test semantic search
aws lambda invoke \
  --function-name media-semantic-search \
  --payload '{
    "query": "action movies with car chases",
    "limit": 5
  }' \
  search_results.json

cat search_results.json | jq '.results'
```

### 7.2 Test Visual Search

```bash
# Test visual search
aws lambda invoke \
  --function-name media-visual-search \
  --payload '{
    "image_s3_bucket": "media-dev-raw",
    "image_s3_key": "query-images/car.jpg",
    "limit": 5
  }' \
  visual_results.json
```

### 7.3 Test Discovery API

```bash
# Test via API Gateway
curl "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/discover?type=semantic&q=comedy&limit=10"

curl "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/discover?type=visual&image_bucket=media-dev-raw&image_key=query.jpg&limit=10"

curl "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/discover?type=hybrid&q=action&image_bucket=media-dev-raw&image_key=query.jpg&limit=10"
```

## Best Practices

### Embedding Generation
- Batch process embeddings for efficiency
- Cache embeddings to avoid regeneration
- Use consistent text preprocessing
- Monitor embedding dimensions and quality

### Visual Features
- Extract features during content ingestion
- Store features in searchable format
- Update features when content changes
- Use confidence thresholds for filtering

### Search Index
- Optimize index settings for your use case
- Use appropriate shard and replica counts
- Monitor index size and performance
- Implement index aliases for zero-downtime updates

### Personalization
- Track diverse user interactions
- Update preferences in real-time
- Balance personalization with diversity
- Respect user privacy preferences

### Performance
- Implement result caching
- Use appropriate k values for KNN search
- Optimize query complexity
- Monitor search latency

## Troubleshooting

### Common Issues

**Low Search Relevance**
- Tune embedding models and parameters
- Improve content metadata quality
- Adjust hybrid search weights
- Add query expansion

**Slow Search Performance**
- Optimize OpenSearch cluster size
- Use appropriate k values for KNN
- Implement result caching
- Consider search tiering

**Missing Visual Features**
- Verify Rekognition permissions
- Check S3 bucket access
- Monitor video analysis job status
- Implement retry logic

**OpenSearch Connection Errors**
- Verify endpoint and credentials
- Check security group rules
- Verify VPC configuration if applicable
- Test connectivity from Lambda

## Next Steps

- **Content Generation**: Implement automated content creation
- **Audience Intelligence**: Build analytics and insights
- **Optimization**: Fine-tune search algorithms
- **Integration**: Connect to recommendation systems

---

For more information, see the [Content Discovery Workshop Module](../workshop/module-3-discovery.md).

