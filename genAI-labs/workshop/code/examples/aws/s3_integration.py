"""
S3 Integration for storing generated code
"""

import boto3
import json
from datetime import datetime
from typing import Dict, Any, List


class S3CodeStorage:
    """Store and retrieve generated code in S3"""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        """Initialize S3 client"""
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', region_name=region)
    
    def store_code(
        self,
        code: str,
        language: str,
        prompt: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store generated code in S3
        
        Args:
            code: Generated code
            language: Programming language
            prompt: Original prompt
            metadata: Additional metadata
        
        Returns:
            S3 object key
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        key = f"generated-code/{language}/{timestamp}.py"
        
        # Create metadata
        file_metadata = {
            'language': language,
            'prompt': prompt[:500],  # Truncate if too long
            'generated_at': datetime.utcnow().isoformat(),
            'code_length': str(len(code)),
            **(metadata or {})
        }
        
        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=code.encode('utf-8'),
            ContentType='text/plain',
            Metadata=file_metadata
        )
        
        return key
    
    def retrieve_code(self, key: str) -> Dict[str, Any]:
        """
        Retrieve code from S3
        
        Args:
            key: S3 object key
        
        Returns:
            Dictionary with code and metadata
        """
        response = self.s3.get_object(
            Bucket=self.bucket_name,
            Key=key
        )
        
        code = response['Body'].read().decode('utf-8')
        metadata = response.get('Metadata', {})
        
        return {
            'code': code,
            'metadata': metadata,
            'key': key
        }
    
    def list_codes(self, language: str = None, prefix: str = 'generated-code/') -> List[Dict[str, Any]]:
        """
        List stored code files
        
        Args:
            language: Filter by language
            prefix: S3 prefix
        
        Returns:
            List of code files
        """
        prefix = f"{prefix}{language}/" if language else prefix
        
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        files = []
        for obj in response.get('Contents', []):
            files.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            })
        
        return files


if __name__ == "__main__":
    # Example usage
    storage = S3CodeStorage(bucket_name='claude-code-workshop')
    
    # Store code
    code = """
def hello_world():
    print("Hello, World!")
"""
    
    key = storage.store_code(
        code=code,
        language='python',
        prompt='Generate a hello world function',
        metadata={'example': 'true'}
    )
    
    print(f"Code stored at: {key}")
    
    # Retrieve code
    result = storage.retrieve_code(key)
    print(f"Retrieved code: {result['code']}")
    
    # List codes
    files = storage.list_codes(language='python')
    print(f"Found {len(files)} Python files")

