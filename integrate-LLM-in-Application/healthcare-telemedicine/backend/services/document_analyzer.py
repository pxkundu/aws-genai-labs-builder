"""
Document Analyzer Service - AI-powered medical document analysis
"""
import os
import json
import uuid
import logging
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DocumentAnalyzerService:
    """Medical document analysis service using Textract and Comprehend Medical"""
    
    SUPPORTED_DOCUMENT_TYPES = [
        "lab_results",
        "prescription",
        "medical_history",
        "insurance",
        "referral",
        "discharge_summary",
        "general"
    ]
    
    def __init__(self):
        self.textract = boto3.client(
            'textract',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.comprehend_medical = boto3.client(
            'comprehendmedical',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.bucket_name = os.getenv('S3_DOCUMENTS_BUCKET', 'telemedicine-documents-dev')
    
    async def analyze_document(
        self,
        document_url: str,
        document_type: str = "general",
        patient_id: Optional[str] = None
    ) -> dict:
        """
        Analyze a medical document
        
        Args:
            document_url: S3 URL or presigned URL of the document
            document_type: Type of medical document
            patient_id: Optional patient identifier
            
        Returns:
            Analysis results with extracted entities and summary
        """
        analysis_id = str(uuid.uuid4())
        
        try:
            # Validate document type
            if document_type not in self.SUPPORTED_DOCUMENT_TYPES:
                document_type = "general"
            
            # Step 1: Extract text from document
            extracted_text = await self._extract_text(document_url)
            
            if not extracted_text:
                raise ValueError("Failed to extract text from document")
            
            # Step 2: Extract medical entities
            medical_entities = await self._extract_medical_entities(extracted_text)
            
            # Step 3: Generate AI summary and insights
            ai_analysis = await self._generate_ai_analysis(
                text=extracted_text,
                document_type=document_type,
                entities=medical_entities
            )
            
            result = {
                "analysis_id": analysis_id,
                "document_type": document_type,
                "extracted_entities": medical_entities,
                "summary": ai_analysis.get("summary", ""),
                "key_findings": ai_analysis.get("key_findings", []),
                "recommendations": ai_analysis.get("recommendations", []),
                "flags": ai_analysis.get("flags", []),
                "confidence_score": ai_analysis.get("confidence_score", 0.8)
            }
            
            # Store analysis
            await self._store_analysis(analysis_id, patient_id, document_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    async def _extract_text(self, document_url: str) -> str:
        """Extract text from document using Textract"""
        try:
            # Parse S3 URL
            if document_url.startswith("s3://"):
                parts = document_url.replace("s3://", "").split("/", 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ""
            else:
                # Assume it's a key in the default bucket
                bucket = self.bucket_name
                key = document_url
            
            # Call Textract
            response = self.textract.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            # Extract text from blocks
            text_blocks = []
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block.get('Text', ''))
            
            return '\n'.join(text_blocks)
            
        except ClientError as e:
            logger.error(f"Textract error: {str(e)}")
            raise
    
    async def _extract_medical_entities(self, text: str) -> dict:
        """Extract medical entities using Comprehend Medical"""
        try:
            # Truncate text if too long (Comprehend Medical limit)
            max_length = 20000
            if len(text) > max_length:
                text = text[:max_length]
            
            response = self.comprehend_medical.detect_entities_v2(Text=text)
            
            entities = {
                "conditions": [],
                "medications": [],
                "tests": [],
                "procedures": [],
                "anatomy": [],
                "dosages": [],
                "dates": [],
                "protected_health_info": []
            }
            
            for entity in response.get('Entities', []):
                category = entity.get('Category', '')
                entity_type = entity.get('Type', '')
                text_value = entity.get('Text', '')
                confidence = entity.get('Score', 0)
                
                if confidence < 0.7:
                    continue
                
                entity_data = {
                    "text": text_value,
                    "confidence": round(confidence, 2),
                    "type": entity_type
                }
                
                if category == 'MEDICAL_CONDITION':
                    entities["conditions"].append(entity_data)
                elif category == 'MEDICATION':
                    entities["medications"].append(entity_data)
                    # Check for dosage
                    for attr in entity.get('Attributes', []):
                        if attr.get('Type') == 'DOSAGE':
                            entities["dosages"].append({
                                "medication": text_value,
                                "dosage": attr.get('Text', '')
                            })
                elif category == 'TEST_TREATMENT_PROCEDURE':
                    if 'TEST' in entity_type:
                        entities["tests"].append(entity_data)
                    else:
                        entities["procedures"].append(entity_data)
                elif category == 'ANATOMY':
                    entities["anatomy"].append(entity_data)
                elif category == 'PROTECTED_HEALTH_INFORMATION':
                    entities["protected_health_info"].append({
                        "type": entity_type,
                        "detected": True  # Don't store actual PHI
                    })
                elif category == 'TIME_EXPRESSION':
                    entities["dates"].append(entity_data)
            
            return entities
            
        except ClientError as e:
            logger.error(f"Comprehend Medical error: {str(e)}")
            return {
                "conditions": [],
                "medications": [],
                "tests": [],
                "procedures": [],
                "anatomy": [],
                "dosages": [],
                "dates": [],
                "protected_health_info": []
            }
    
    async def _generate_ai_analysis(
        self,
        text: str,
        document_type: str,
        entities: dict
    ) -> dict:
        """Generate AI analysis using Bedrock"""
        
        # Truncate text for prompt
        max_text_length = 8000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "...[truncated]"
        
        prompt = f"""You are a medical document analyst. Analyze the following {document_type} document and provide a structured analysis.

Document Text:
{text}

Extracted Medical Entities:
- Conditions: {json.dumps([e['text'] for e in entities.get('conditions', [])])}
- Medications: {json.dumps([e['text'] for e in entities.get('medications', [])])}
- Tests: {json.dumps([e['text'] for e in entities.get('tests', [])])}
- Procedures: {json.dumps([e['text'] for e in entities.get('procedures', [])])}

Please provide your analysis in the following JSON format:
{{
    "summary": "A concise 2-3 sentence summary of the document",
    "key_findings": [
        "Important finding 1",
        "Important finding 2"
    ],
    "recommendations": [
        "Recommendation for patient or provider"
    ],
    "flags": [
        "Any concerning items that need attention"
    ],
    "confidence_score": 0.0 to 1.0
}}

IMPORTANT:
- Focus on clinically relevant information
- Flag any abnormal values or concerning findings
- Do not include specific PHI in your response
- Provide actionable recommendations when appropriate

Respond ONLY with the JSON object."""

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return self._get_fallback_analysis(document_type)
        except ClientError as e:
            logger.error(f"Bedrock error: {str(e)}")
            return self._get_fallback_analysis(document_type)
    
    def _get_fallback_analysis(self, document_type: str) -> dict:
        """Return fallback analysis when AI is unavailable"""
        return {
            "summary": f"Document type: {document_type}. Automated analysis unavailable.",
            "key_findings": ["Manual review recommended"],
            "recommendations": ["Please have a healthcare provider review this document"],
            "flags": [],
            "confidence_score": 0.5
        }
    
    async def _store_analysis(
        self,
        analysis_id: str,
        patient_id: Optional[str],
        document_type: str,
        result: dict
    ):
        """Store analysis in DynamoDB"""
        try:
            table = self.dynamodb.Table(os.getenv('DYNAMODB_ASSESSMENTS_TABLE', 'telemedicine-assessments'))
            
            item = {
                "assessment_id": analysis_id,
                "assessment_type": "document_analysis",
                "patient_id": patient_id or "anonymous",
                "document_type": document_type,
                "result": result,
                "created_at": datetime.utcnow().isoformat(),
                "ttl": int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)  # 1 year
            }
            
            table.put_item(Item=item)
            logger.info(f"Stored document analysis: {analysis_id}")
            
        except ClientError as e:
            logger.error(f"Failed to store analysis: {str(e)}")
    
    async def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """Retrieve a stored analysis"""
        try:
            table = self.dynamodb.Table(os.getenv('DYNAMODB_ASSESSMENTS_TABLE', 'telemedicine-assessments'))
            
            response = table.get_item(Key={"assessment_id": analysis_id})
            
            if 'Item' in response:
                return response['Item'].get('result')
            return None
            
        except ClientError as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return None
