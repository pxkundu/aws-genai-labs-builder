# Module 6: Testing and Optimization

## Overview
This module covers testing strategies and optimization techniques for Claude Code applications. You'll learn how to test generated code, optimize performance, manage costs, and implement monitoring and alerting.

## Learning Objectives
- Write comprehensive tests for Claude Code applications
- Optimize code generation performance
- Implement cost optimization strategies
- Set up monitoring and alerting
- Perform load testing
- Analyze and optimize application performance

## Prerequisites
- Completed Module 5: Infrastructure Deployment
- Understanding of testing concepts
- Familiarity with performance optimization
- Basic knowledge of monitoring and alerting

## Step 1: Testing Strategies

### 1.1 Unit Testing
Create `tests/unit/test_claude_code.py`:

```python
"""
Unit tests for Claude Code functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from code.examples.basic_claude_code import ClaudeCodeClient


class TestClaudeCodeClient:
    """Unit tests for ClaudeCodeClient"""
    
    @pytest.fixture
    def client(self):
        """Create ClaudeCodeClient instance"""
        return ClaudeCodeClient()
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_generate_code_success(self, mock_boto3, client):
        """Test successful code generation"""
        # Mock Bedrock response
        mock_response = {
            'body': MagicMock(read=lambda: b'{"content":[{"text":"def hello():\\n    print(\\"Hello\\")"}]}')
        }
        
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        result = client.generate_code(
            prompt="Generate a hello world function",
            language="python"
        )
        
        assert result['status'] == 'success'
        assert 'def hello()' in result['code']
        mock_bedrock.invoke_model.assert_called_once()
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_generate_code_error(self, mock_boto3, client):
        """Test code generation error handling"""
        # Mock Bedrock error
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.side_effect = Exception("Bedrock error")
        mock_boto3.return_value = mock_bedrock
        
        result = client.generate_code(
            prompt="Generate a hello world function",
            language="python"
        )
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_refactor_code_success(self, mock_boto3, client):
        """Test successful code refactoring"""
        original_code = "def add(a,b): return a+b"
        
        mock_response = {
            'body': MagicMock(read=lambda: b'{"content":[{"text":"def add(a: int, b: int) -> int:\\n    return a + b"}]}')
        }
        
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        result = client.refactor_code(
            code=original_code,
            instructions="Add type hints",
            language="python"
        )
        
        assert result['status'] == 'success'
        assert 'type hints' in result['refactored_code'].lower() or 'int' in result['refactored_code']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 1.2 Integration Testing
Create `tests/integration/test_api_integration.py`:

```python
"""
Integration tests for Claude Code API
"""

import pytest
import requests
import json
from typing import Dict, Any


class TestClaudeCodeAPI:
    """Integration tests for Claude Code API"""
    
    @pytest.fixture
    def api_base_url(self):
        """API base URL"""
        return "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
    
    def test_generate_code_endpoint(self, api_base_url):
        """Test code generation endpoint"""
        url = f"{api_base_url}/generate"
        
        payload = {
            "prompt": "Generate a Python function to calculate factorial",
            "language": "python",
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'code' in data
        assert 'language' in data
        assert data['language'] == 'python'
    
    def test_generate_code_missing_prompt(self, api_base_url):
        """Test code generation with missing prompt"""
        url = f"{api_base_url}/generate"
        
        payload = {
            "language": "python"
        }
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_health_endpoint(self, api_base_url):
        """Test health check endpoint"""
        url = f"{api_base_url}/health"
        
        response = requests.get(url)
        
        assert response.status_code == 200
```

### 1.3 End-to-End Testing
Create `tests/e2e/test_e2e_workflow.py`:

```python
"""
End-to-end tests for Claude Code workflow
"""

import pytest
import boto3
import json
from code.examples.basic_claude_code import ClaudeCodeClient
from code.examples.aws.s3_integration import S3CodeStorage
from code.examples.aws.dynamodb_integration import DynamoDBResults


class TestE2EWorkflow:
    """End-to-end tests for complete workflow"""
    
    @pytest.fixture
    def client(self):
        """Create ClaudeCodeClient"""
        return ClaudeCodeClient()
    
    @pytest.fixture
    def s3_storage(self):
        """Create S3 storage"""
        return S3CodeStorage(bucket_name='claude-code-workshop')
    
    @pytest.fixture
    def dynamodb_results(self):
        """Create DynamoDB results"""
        return DynamoDBResults(table_name='claude-code-results')
    
    def test_complete_workflow(self, client, s3_storage, dynamodb_results):
        """Test complete workflow: generate -> store -> retrieve"""
        # Generate code
        prompt = "Generate a Python function to calculate Fibonacci"
        result = client.generate_code(
            prompt=prompt,
            language="python"
        )
        
        assert result['status'] == 'success'
        generated_code = result['code']
        
        # Store in S3
        s3_key = s3_storage.store_code(
            code=generated_code,
            language="python",
            prompt=prompt
        )
        
        assert s3_key is not None
        
        # Store metadata in DynamoDB
        result_id = dynamodb_results.store_result(
            prompt=prompt,
            generated_code=generated_code,
            language="python"
        )
        
        assert result_id is not None
        
        # Retrieve from DynamoDB
        retrieved_result = dynamodb_results.get_result(result_id)
        assert retrieved_result is not None
        assert retrieved_result['language'] == 'python'
        
        # Retrieve from S3
        s3_result = s3_storage.retrieve_code(s3_key)
        assert s3_result['code'] == generated_code
```

## Step 2: Performance Optimization

### 2.1 Code Generation Optimization
Create `code/examples/optimization/performance_optimization.py`:

```python
"""
Performance optimization for Claude Code generation
"""

import time
import json
import boto3
from typing import Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta


class OptimizedClaudeCodeClient:
    """Optimized Claude Code client with caching"""
    
    def __init__(self, cache_ttl: int = 3600):
        """Initialize with caching"""
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        self.cache_ttl = cache_ttl
        self.cache = {}
    
    @lru_cache(maxsize=100)
    def generate_code_cached(self, prompt: str, language: str) -> str:
        """Generate code with caching"""
        cache_key = f"{language}:{prompt}"
        
        # Check cache
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if cached_result['timestamp'] + timedelta(seconds=self.cache_ttl) > datetime.utcnow():
                return cached_result['code']
        
        # Generate new code
        result = self._generate_code(prompt, language)
        
        # Store in cache
        self.cache[cache_key] = {
            'code': result,
            'timestamp': datetime.utcnow()
        }
        
        return result
    
    def _generate_code(self, prompt: str, language: str) -> str:
        """Internal code generation"""
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4000,
                'messages': [{
                    'role': 'user',
                    'content': f'Generate {language} code: {prompt}'
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    
    def batch_generate(self, prompts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Batch code generation for better performance"""
        results = []
        
        for prompt_data in prompts:
            start_time = time.time()
            
            result = self.generate_code_cached(
                prompt=prompt_data['prompt'],
                language=prompt_data.get('language', 'python')
            )
            
            end_time = time.time()
            
            results.append({
                'prompt': prompt_data['prompt'],
                'language': prompt_data.get('language', 'python'),
                'code': result,
                'generation_time': end_time - start_time
            })
        
        return results


def benchmark_performance():
    """Benchmark code generation performance"""
    client = OptimizedClaudeCodeClient()
    
    prompts = [
        {'prompt': 'Generate a factorial function', 'language': 'python'},
        {'prompt': 'Generate a Fibonacci function', 'language': 'python'},
        {'prompt': 'Generate a sorting function', 'language': 'python'}
    ]
    
    # Test without cache
    start_time = time.time()
    for prompt_data in prompts:
        client._generate_code(
            prompt=prompt_data['prompt'],
            language=prompt_data['language']
        )
    no_cache_time = time.time() - start_time
    
    # Test with cache
    start_time = time.time()
    client.batch_generate(prompts)
    cached_time = time.time() - start_time
    
    print(f"Without cache: {no_cache_time:.2f}s")
    print(f"With cache: {cached_time:.2f}s")
    print(f"Speedup: {no_cache_time / cached_time:.2f}x")


if __name__ == "__main__":
    benchmark_performance()
```

## Step 3: Cost Optimization

### 3.1 Cost Optimization Strategies
Create `code/examples/optimization/cost_optimization.py`:

```python
"""
Cost optimization strategies for Claude Code
"""

import boto3
from typing import Dict, Any, Optional
from datetime import datetime


class CostOptimizedClaudeCode:
    """Cost-optimized Claude Code client"""
    
    # Model pricing (per 1M tokens, approximate)
    MODEL_PRICING = {
        'anthropic.claude-3-haiku-20240307-v1:0': {
            'input': 0.25,  # $0.25 per 1M input tokens
            'output': 1.25   # $1.25 per 1M output tokens
        },
        'anthropic.claude-3-5-sonnet-20241022-v2:0': {
            'input': 3.00,
            'output': 15.00
        },
        'anthropic.claude-3-opus-20240229-v1:0': {
            'input': 15.00,
            'output': 75.00
        }
    }
    
    def __init__(self):
        """Initialize cost-optimized client"""
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.usage_stats = []
    
    def select_model(self, complexity: str = 'medium') -> str:
        """
        Select appropriate model based on complexity
        
        Args:
            complexity: 'simple', 'medium', or 'complex'
        
        Returns:
            Model ID
        """
        if complexity == 'simple':
            return 'anthropic.claude-3-haiku-20240307-v1:0'
        elif complexity == 'medium':
            return 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        else:
            return 'anthropic.claude-3-opus-20240229-v1:0'
    
    def estimate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for code generation
        
        Args:
            model_id: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        pricing = self.MODEL_PRICING.get(model_id)
        if not pricing:
            return 0.0
        
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        
        return input_cost + output_cost
    
    def track_usage(self, model_id: str, input_tokens: int, output_tokens: int):
        """Track usage for cost analysis"""
        cost = self.estimate_cost(model_id, input_tokens, output_tokens)
        
        self.usage_stats.append({
            'timestamp': datetime.utcnow().isoformat(),
            'model_id': model_id,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        })
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        if not self.usage_stats:
            return {'total_cost': 0.0, 'total_requests': 0}
        
        total_cost = sum(stat['cost'] for stat in self.usage_stats)
        total_requests = len(self.usage_stats)
        
        return {
            'total_cost': total_cost,
            'total_requests': total_requests,
            'average_cost_per_request': total_cost / total_requests if total_requests > 0 else 0.0
        }


def main():
    """Example usage"""
    client = CostOptimizedClaudeCode()
    
    # Simple task - use Haiku
    simple_model = client.select_model('simple')
    print(f"Simple task model: {simple_model}")
    
    # Complex task - use Sonnet
    complex_model = client.select_model('complex')
    print(f"Complex task model: {complex_model}")
    
    # Estimate cost
    cost = client.estimate_cost(
        model_id=simple_model,
        input_tokens=1000,
        output_tokens=500
    )
    print(f"Estimated cost: ${cost:.4f}")
    
    # Track usage
    client.track_usage(simple_model, 1000, 500)
    
    # Get summary
    summary = client.get_usage_summary()
    print(f"Usage summary: {summary}")


if __name__ == "__main__":
    main()
```

## Step 4: Monitoring and Alerting

### 4.1 Monitoring Setup
Create `code/examples/monitoring/monitoring_setup.py`:

```python
"""
Monitoring and alerting setup for Claude Code
"""

import boto3
import json
from datetime import datetime
from typing import Dict, Any


class ClaudeCodeMonitoring:
    """Monitoring and alerting for Claude Code"""
    
    def __init__(self):
        """Initialize monitoring"""
        self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        self.sns = boto3.client('sns', region_name='us-east-1')
        self.namespace = 'ClaudeCode/Workshop'
    
    def publish_metric(self, metric_name: str, value: float, unit: str = 'Count'):
        """Publish custom metric to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Timestamp': datetime.utcnow(),
                    'Unit': unit
                }]
            )
        except Exception as e:
            print(f"Failed to publish metric: {str(e)}")
    
    def send_alert(self, topic_arn: str, subject: str, message: str):
        """Send alert via SNS"""
        try:
            self.sns.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=message
            )
        except Exception as e:
            print(f"Failed to send alert: {str(e)}")
    
    def create_alarm(self, alarm_name: str, metric_name: str, threshold: float):
        """Create CloudWatch alarm"""
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName=metric_name,
                Namespace=self.namespace,
                Period=300,
                Statistic='Average',
                Threshold=threshold,
                ActionsEnabled=True
            )
        except Exception as e:
            print(f"Failed to create alarm: {str(e)}")


def main():
    """Example usage"""
    monitoring = ClaudeCodeMonitoring()
    
    # Publish metrics
    monitoring.publish_metric('CodeGenerationSuccess', 1)
    monitoring.publish_metric('CodeGenerationTime', 2.5, 'Seconds')
    monitoring.publish_metric('CodeGenerationCost', 0.01, 'None')
    
    print("Metrics published successfully")


if __name__ == "__main__":
    main()
```

## Step 5: Load Testing

### 5.1 Load Testing Script
Create `tests/load/load_test.py`:

```python
"""
Load testing for Claude Code API
"""

import requests
import time
import concurrent.futures
from typing import List, Dict, Any
import statistics


class LoadTester:
    """Load testing for Claude Code API"""
    
    def __init__(self, api_url: str):
        """Initialize load tester"""
        self.api_url = api_url
    
    def generate_request(self, prompt: str) -> Dict[str, Any]:
        """Generate a single request"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "prompt": prompt,
                    "language": "python",
                    "max_tokens": 1000
                },
                timeout=300
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_load_test(self, num_requests: int, concurrent_requests: int = 10) -> Dict[str, Any]:
        """Run load test"""
        prompts = [
            f"Generate a Python function for task {i}"
            for i in range(num_requests)
        ]
        
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(self.generate_request, prompt) for prompt in prompts]
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        return {
            'total_requests': num_requests,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / num_requests * 100,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'average_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        }


def main():
    """Example usage"""
    tester = LoadTester("https://your-api-id.execute-api.us-east-1.amazonaws.com/prod")
    
    # Run load test
    results = tester.run_load_test(num_requests=100, concurrent_requests=10)
    
    print("Load Test Results:")
    print(f"Total Requests: {results['total_requests']}")
    print(f"Successful: {results['successful_requests']}")
    print(f"Failed: {results['failed_requests']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"Requests/Second: {results['requests_per_second']:.2f}")
    print(f"Average Response Time: {results['average_response_time']:.2f}s")
    print(f"Median Response Time: {results['median_response_time']:.2f}s")
    print(f"P95 Response Time: {results['p95_response_time']:.2f}s")


if __name__ == "__main__":
    main()
```

## Step 6: Exercises

### Exercise 1: Write Unit Tests
Write comprehensive unit tests for your Claude Code client.

### Exercise 2: Write Integration Tests
Create integration tests for your API endpoints.

### Exercise 3: Optimize Performance
Implement caching and batch processing for better performance.

### Exercise 4: Cost Optimization
Implement cost tracking and optimization strategies.

### Exercise 5: Load Testing
Perform load testing and analyze results.

## Troubleshooting

### Common Issues

#### Tests Fail
- Check test environment setup
- Verify AWS credentials
- Review test data and fixtures

#### Performance Issues
- Implement caching
- Optimize prompts
- Use appropriate models

#### Cost Concerns
- Use cheaper models for simple tasks
- Implement caching
- Monitor usage

## Next Steps

✅ **Module 6 Complete!**

You have successfully:
- Written comprehensive tests
- Optimized performance
- Implemented cost optimization
- Set up monitoring and alerting
- Performed load testing

**🎉 Workshop Complete!**

You've successfully completed all modules of the Claude Code on AWS Workshop. You now have the knowledge and skills to:
- Build Claude Code applications
- Integrate with AWS services
- Deploy production-ready infrastructure
- Test and optimize your applications

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Performance Optimization Guide](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Cost Optimization Guide](https://aws.amazon.com/pricing/)

