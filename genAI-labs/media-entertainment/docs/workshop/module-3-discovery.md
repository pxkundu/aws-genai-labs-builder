# Module 3: Content Discovery & Search

## Learning Objectives

By the end of this module, you will be able to:

- Implement semantic search using Bedrock embeddings
- Build visual search with Amazon Rekognition
- Design and populate search indexes (OpenSearch/vector DB)
- Create a unified discovery API for multi-modal search
- Implement personalized ranking and recommendations
- Optimize search performance and relevance

## Prerequisites

- Completed Module 2: AI Content Studio
- Content stored in S3 with metadata
- Access to Amazon Bedrock (embeddings)
- Access to Amazon Rekognition
- Access to Amazon OpenSearch Service (or vector database)
- Basic understanding of vector embeddings

## Duration

**Estimated Time**: 90 minutes

## Step 1: Set Up Embedding Generation

### 1.1 Create Embedding Lambda

```python
# lambda/embedding_generator.py
import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Generate embeddings for text content using Bedrock
    """
    text = event.get('text', '')
    content_id = event.get('content_id', '')
    
    # Use Titan Embeddings model
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({
            'inputText': text
        })
    )
    
    result = json.loads(response['body'].read())
    embedding = result['embedding']
    
    return {
        'statusCode': 200,
        'content_id': content_id,
        'embedding': embedding,
        'dimension': len(embedding)
    }
```

### 1.2 Generate Embeddings for Content Library

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

## Step 2: Set Up Visual Feature Extraction

### 2.1 Create Rekognition Feature Extractor

```python
# lambda/rekognition_feature_extractor.py
import json
import boto3
import os

rekognition = boto3.client('rekognition', region_name=os.environ['AWS_REGION'])
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Extract visual features from images/videos using Rekognition
    """
    s3_bucket = event.get('s3_bucket')
    s3_key = event.get('s3_key')
    content_type = event.get('content_type', 'image')  # image or video
    
    features = {}
    
    if content_type == 'image':
        # Detect labels, faces, objects, text
        labels_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
            MaxLabels=20,
            MinConfidence=70
        )
        
        faces_response = rekognition.detect_faces(
            Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
            Attributes=['ALL']
        )
        
        text_response = rekognition.detect_text(
            Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
        )
        
        features = {
            'labels': [label['Name'] for label in labels_response['Labels']],
            'faces_count': len(faces_response['Faces']),
            'text_detected': [text['DetectedText'] for text in text_response['TextDetections']],
            'moderation': rekognition.detect_moderation_labels(
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
            )['ModerationLabels']
        }
    
    elif content_type == 'video':
        # Start video analysis job
        job_response = rekognition.start_label_detection(
            Video={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
            NotificationChannel={
                'SNSTopicArn': os.environ['SNS_TOPIC_ARN'],
                'RoleArn': os.environ['REKOGNITION_ROLE_ARN']
            }
        )
        
        features = {
            'job_id': job_response['JobId'],
            'status': 'IN_PROGRESS'
        }
    
    return {
        'statusCode': 200,
        'features': features
    }
```

### 2.2 Process Video Analysis Results

```python
# lambda/rekognition_video_handler.py
import json
import boto3

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Handle Rekognition video analysis completion
    """
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    job_id = sns_message['JobId']
    status = sns_message['Status']
    
    if status == 'SUCCEEDED':
        # Get job results
        response = rekognition.get_label_detection(JobId=job_id)
        
        labels = []
        for label_detection in response['Labels']:
            labels.append({
                'name': label_detection['Label']['Name'],
                'confidence': label_detection['Label']['Confidence'],
                'timestamp': label_detection['Timestamp']
            })
        
        # Store in DynamoDB
        table = dynamodb.Table('media-content-metadata')
        content_id = sns_message['Video']['S3ObjectName'].split('/')[-1]
        
        table.update_item(
            Key={'content_id': content_id},
            UpdateExpression='SET visual_features = :vf',
            ExpressionAttributeValues={':vf': {'labels': labels}}
        )
    
    return {'statusCode': 200}
```

## Step 3: Set Up OpenSearch Index

### 3.1 Create OpenSearch Domain

```bash
# Create OpenSearch domain (via console or CloudFormation)
# Domain name: media-content-search
# Instance type: t3.small.search
# EBS volume: 20GB
# Access policy: Allow Lambda and API Gateway
```

### 3.2 Create Index Mapping

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

### 3.3 Index Content Documents

```python
# scripts/index_content.py
import boto3
import json
import requests
from requests.auth import HTTPBasicAuth

opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
dynamodb = boto3.resource('dynamodb')

def index_content_item(item):
    """Index a single content item in OpenSearch"""
    doc = {
        'content_id': item['content_id'],
        'title': item.get('title', ''),
        'description': item.get('description', ''),
        'tags': item.get('tags', []),
        'content_type': item.get('content_type', 'video'),
        'embedding': item.get('embedding', []),
        'visual_features': item.get('visual_features', {}),
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
    index_content_item(item)
    print(f"Indexed: {item['content_id']}")
```

## Step 4: Implement Semantic Search

### 4.1 Create Semantic Search Lambda

```python
# lambda/semantic_search.py
import json
import boto3
import os
import requests
from requests.auth import HTTPBasicAuth

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Perform semantic search using embeddings
    """
    query = event.get('query', '')
    limit = event.get('limit', 10)
    
    # Generate query embedding
    embedding_response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({
            'inputText': query
        })
    )
    
    embedding_result = json.loads(embedding_response['body'].read())
    query_embedding = embedding_result['embedding']
    
    # Search OpenSearch
    opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
    
    search_query = {
        'size': limit,
        'query': {
            'knn': {
                'embedding': {
                    'vector': query_embedding,
                    'k': limit
                }
            }
        },
        '_source': ['content_id', 'title', 'description', 'tags', 'metadata']
    }
    
    response = requests.post(
        f'https://{opensearch_endpoint}/media-content/_search',
        auth=HTTPBasicAuth(os.environ['OPENSEARCH_USERNAME'], os.environ['OPENSEARCH_PASSWORD']),
        json=search_query,
        headers={'Content-Type': 'application/json'}
    )
    
    results = response.json()
    
    # Format results
    hits = []
    for hit in results['hits']['hits']:
        hits.append({
            'content_id': hit['_source']['content_id'],
            'title': hit['_source']['title'],
            'description': hit['_source']['description'],
            'score': hit['_score'],
            'metadata': hit['_source'].get('metadata', {})
        })
    
    return {
        'statusCode': 200,
        'results': hits,
        'total': results['hits']['total']['value']
    }
```

## Step 5: Implement Visual Search

### 5.1 Create Visual Search Lambda

```python
# lambda/visual_search.py
import json
import boto3
import os
import requests
from requests.auth import HTTPBasicAuth

rekognition = boto3.client('rekognition', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Perform visual search using Rekognition features
    """
    image_s3_bucket = event.get('image_s3_bucket')
    image_s3_key = event.get('image_s3_key')
    limit = event.get('limit', 10)
    
    # Extract features from query image
    labels_response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': image_s3_bucket, 'Name': image_s3_key}},
        MaxLabels=20,
        MinConfidence=70
    )
    
    query_labels = [label['Name'] for label in labels_response['Labels']]
    
    # Search OpenSearch for matching visual features
    opensearch_endpoint = os.environ['OPENSEARCH_ENDPOINT']
    
    search_query = {
        'size': limit,
        'query': {
            'terms': {
                'visual_features.labels': query_labels
            }
        },
        '_source': ['content_id', 'title', 'visual_features', 'metadata']
    }
    
    response = requests.post(
        f'https://{opensearch_endpoint}/media-content/_search',
        auth=HTTPBasicAuth(os.environ['OPENSEARCH_USERNAME'], os.environ['OPENSEARCH_PASSWORD']),
        json=search_query,
        headers={'Content-Type': 'application/json'}
    )
    
    results = response.json()
    
    # Format results
    hits = []
    for hit in results['hits']['hits']:
        hits.append({
            'content_id': hit['_source']['content_id'],
            'title': hit['_source']['title'],
            'matching_labels': list(set(query_labels) & set(hit['_source'].get('visual_features', {}).get('labels', []))),
            'score': hit['_score']
        })
    
    return {
        'statusCode': 200,
        'results': hits,
        'total': results['hits']['total']['value']
    }
```

## Step 6: Create Unified Discovery API

### 6.1 Discovery API Handler

```python
# lambda/discovery_api.py
import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Unified discovery API supporting text, image, and hybrid search
    """
    http_method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters') or {}
    
    search_type = query_params.get('type', 'semantic')  # semantic, visual, hybrid
    query = query_params.get('q', '')
    limit = int(query_params.get('limit', 10))
    
    results = []
    
    if search_type == 'semantic':
        # Semantic search
        response = lambda_client.invoke(
            FunctionName='media-semantic-search',
            Payload=json.dumps({
                'query': query,
                'limit': limit
            })
        )
        results = json.loads(response['Payload'].read())
    
    elif search_type == 'visual':
        # Visual search
        image_s3_bucket = query_params.get('image_bucket')
        image_s3_key = query_params.get('image_key')
        
        response = lambda_client.invoke(
            FunctionName='media-visual-search',
            Payload=json.dumps({
                'image_s3_bucket': image_s3_bucket,
                'image_s3_key': image_s3_key,
                'limit': limit
            })
        )
        results = json.loads(response['Payload'].read())
    
    elif search_type == 'hybrid':
        # Hybrid search (combine semantic and visual)
        semantic_response = lambda_client.invoke(
            FunctionName='media-semantic-search',
            Payload=json.dumps({
                'query': query,
                'limit': limit * 2
            })
        )
        semantic_results = json.loads(semantic_response['Payload'].read())
        
        if query_params.get('image_bucket'):
            visual_response = lambda_client.invoke(
                FunctionName='media-visual-search',
                Payload=json.dumps({
                    'image_s3_bucket': query_params['image_bucket'],
                    'image_s3_key': query_params['image_key'],
                    'limit': limit * 2
                })
            )
            visual_results = json.loads(visual_response['Payload'].read())
            
            # Combine and rank results
            combined = {}
            for result in semantic_results.get('results', []):
                content_id = result['content_id']
                combined[content_id] = {
                    **result,
                    'semantic_score': result['score'],
                    'visual_score': 0
                }
            
            for result in visual_results.get('results', []):
                content_id = result['content_id']
                if content_id in combined:
                    combined[content_id]['visual_score'] = result['score']
                else:
                    combined[content_id] = {
                        **result,
                        'semantic_score': 0,
                        'visual_score': result['score']
                    }
            
            # Calculate hybrid score and sort
            results_list = list(combined.values())
            for result in results_list:
                result['hybrid_score'] = (
                    result['semantic_score'] * 0.6 +
                    result['visual_score'] * 0.4
                )
            
            results_list.sort(key=lambda x: x['hybrid_score'], reverse=True)
            results = {'results': results_list[:limit], 'total': len(results_list)}
        else:
            results = semantic_results
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(results)
    }
```

## Step 7: Implement Personalized Ranking

### 7.1 User Preference Tracking

```python
# lambda/user_preference_tracker.py
import json
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Track user preferences for personalization
    """
    user_id = event.get('user_id')
    content_id = event.get('content_id')
    action = event.get('action')  # view, like, share, complete
    
    table = dynamodb.Table('user-preferences')
    
    # Update user preferences
    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='ADD preferences.#content_id :value',
        ExpressionAttributeNames={'#content_id': content_id},
        ExpressionAttributeValues={':value': 1},
        ReturnValues='UPDATED_NEW'
    )
    
    # Track interaction
    interactions_table = dynamodb.Table('user-interactions')
    interactions_table.put_item(
        Item={
            'user_id': user_id,
            'content_id': content_id,
            'action': action,
            'timestamp': event.get('timestamp')
        }
    )
    
    return {'statusCode': 200}
```

### 7.2 Personalized Search Ranking

```python
# lambda/personalized_search.py
import json
import boto3

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Perform personalized search with user preference boosting
    """
    user_id = event.get('user_id')
    query = event.get('query', '')
    limit = event.get('limit', 10)
    
    # Get base search results
    search_response = lambda_client.invoke(
        FunctionName='media-semantic-search',
        Payload=json.dumps({
            'query': query,
            'limit': limit * 2
        })
    )
    search_results = json.loads(search_response['Payload'].read())
    
    # Get user preferences
    table = dynamodb.Table('user-preferences')
    try:
        user_prefs = table.get_item(Key={'user_id': user_id})['Item']
        preferred_content = user_prefs.get('preferences', {})
    except KeyError:
        preferred_content = {}
    
    # Boost preferred content
    for result in search_results.get('results', []):
        content_id = result['content_id']
        base_score = result['score']
        
        # Apply personalization boost
        if content_id in preferred_content:
            result['personalized_score'] = base_score * 1.5
        else:
            result['personalized_score'] = base_score
    
    # Re-sort by personalized score
    search_results['results'].sort(key=lambda x: x['personalized_score'], reverse=True)
    search_results['results'] = search_results['results'][:limit]
    
    return {
        'statusCode': 200,
        'results': search_results['results']
    }
```

## Step 8: Test Discovery System

### 8.1 Test Semantic Search

```bash
# Test semantic search
aws lambda invoke \
  --function-name media-semantic-search \
  --payload '{
    "query": "action movies with car chases",
    "limit": 5
  }' \
  search_results.json

cat search_results.json
```

### 8.2 Test Visual Search

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

cat visual_results.json
```

### 8.3 Test Discovery API

```bash
# Test via API Gateway
curl "https://API_ID.execute-api.us-east-1.amazonaws.com/prod/discover?type=semantic&q=comedy&limit=10"

curl "https://API_ID.execute-api.us-east-1.amazonaws.com/prod/discover?type=visual&image_bucket=media-dev-raw&image_key=query.jpg&limit=10"
```

## Best Practices

### Embedding Generation
- Batch process embeddings for efficiency
- Cache embeddings to avoid regeneration
- Use consistent text preprocessing
- Monitor embedding dimensions

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

## Next Steps

- **Module 4**: Implement automated content generation
- **Enhancements**: Add faceted search and filters
- **Integration**: Connect to recommendation systems
- **Optimization**: Implement search result caching

---

**Ready for Module 4? Continue with [Automated Content Generation](./module-4-generation.md)!**

