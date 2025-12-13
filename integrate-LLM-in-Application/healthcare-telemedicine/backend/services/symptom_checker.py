"""
Symptom Checker Service - AI-powered symptom assessment
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


class SymptomCheckerService:
    """AI-powered symptom assessment service using Amazon Bedrock"""
    
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.comprehend_medical = boto3.client(
            'comprehendmedical',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.table_name = os.getenv('DYNAMODB_ASSESSMENTS_TABLE', 'telemedicine-assessments')
    
    async def assess_symptoms(
        self,
        symptoms: str,
        patient_id: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[list] = None,
        current_medications: Optional[list] = None
    ) -> dict:
        """
        Assess patient symptoms using AI
        
        Args:
            symptoms: Patient's symptom description
            patient_id: Optional patient identifier
            age: Patient age
            gender: Patient gender
            medical_history: List of known conditions
            current_medications: List of current medications
            
        Returns:
            Assessment results with risk level, conditions, and recommendations
        """
        assessment_id = str(uuid.uuid4())
        
        try:
            # Step 1: Extract medical entities using Comprehend Medical
            medical_entities = await self._extract_medical_entities(symptoms)
            
            # Step 2: Generate AI assessment using Bedrock
            ai_assessment = await self._generate_ai_assessment(
                symptoms=symptoms,
                medical_entities=medical_entities,
                age=age,
                gender=gender,
                medical_history=medical_history or [],
                current_medications=current_medications or []
            )
            
            # Step 3: Calculate risk score
            risk_level, risk_score = self._calculate_risk(ai_assessment, medical_entities)
            
            # Step 4: Prepare response
            result = {
                "assessment_id": assessment_id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "possible_conditions": ai_assessment.get("possible_conditions", []),
                "follow_up_questions": ai_assessment.get("follow_up_questions", []),
                "recommendations": ai_assessment.get("recommendations", []),
                "urgency": ai_assessment.get("urgency", "routine"),
                "disclaimer": "This assessment is for informational purposes only and does not constitute medical advice. Please consult a healthcare professional for proper diagnosis and treatment."
            }
            
            # Step 5: Store assessment
            await self._store_assessment(assessment_id, patient_id, symptoms, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in symptom assessment: {str(e)}")
            raise
    
    async def _extract_medical_entities(self, text: str) -> dict:
        """Extract medical entities using Amazon Comprehend Medical"""
        try:
            response = self.comprehend_medical.detect_entities_v2(Text=text)
            
            entities = {
                "symptoms": [],
                "conditions": [],
                "medications": [],
                "anatomy": [],
                "tests": []
            }
            
            for entity in response.get('Entities', []):
                category = entity.get('Category', '')
                entity_text = entity.get('Text', '')
                confidence = entity.get('Score', 0)
                
                if confidence > 0.7:  # Only include high-confidence entities
                    if category == 'MEDICAL_CONDITION':
                        if entity.get('Type') == 'DX_NAME':
                            entities["conditions"].append(entity_text)
                        else:
                            entities["symptoms"].append(entity_text)
                    elif category == 'MEDICATION':
                        entities["medications"].append(entity_text)
                    elif category == 'ANATOMY':
                        entities["anatomy"].append(entity_text)
                    elif category == 'TEST_TREATMENT_PROCEDURE':
                        entities["tests"].append(entity_text)
            
            return entities
            
        except ClientError as e:
            logger.warning(f"Comprehend Medical error: {str(e)}, using fallback")
            return {"symptoms": [], "conditions": [], "medications": [], "anatomy": [], "tests": []}
    
    async def _generate_ai_assessment(
        self,
        symptoms: str,
        medical_entities: dict,
        age: Optional[int],
        gender: Optional[str],
        medical_history: list,
        current_medications: list
    ) -> dict:
        """Generate AI assessment using Amazon Bedrock"""
        
        prompt = f"""You are a medical triage assistant. Analyze the following patient information and provide a structured assessment.

IMPORTANT: This is for triage purposes only. Always recommend consulting a healthcare professional.

Patient Information:
- Symptoms: {symptoms}
- Age: {age if age else 'Not provided'}
- Gender: {gender if gender else 'Not provided'}
- Medical History: {', '.join(medical_history) if medical_history else 'None reported'}
- Current Medications: {', '.join(current_medications) if current_medications else 'None reported'}

Extracted Medical Entities:
- Identified Symptoms: {', '.join(medical_entities.get('symptoms', [])) or 'None identified'}
- Possible Conditions: {', '.join(medical_entities.get('conditions', [])) or 'None identified'}
- Body Areas: {', '.join(medical_entities.get('anatomy', [])) or 'None identified'}

Please provide your assessment in the following JSON format:
{{
    "possible_conditions": [
        {{"name": "condition name", "likelihood": "high/medium/low", "description": "brief description"}}
    ],
    "follow_up_questions": [
        "question 1",
        "question 2"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ],
    "urgency": "emergency/urgent/semi-urgent/routine",
    "red_flags": ["any concerning symptoms that need immediate attention"]
}}

Respond ONLY with the JSON object, no additional text."""

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2048,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Parse JSON response
            assessment = json.loads(content)
            return assessment
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return self._get_fallback_assessment()
        except ClientError as e:
            logger.error(f"Bedrock error: {str(e)}")
            return self._get_fallback_assessment()
    
    def _calculate_risk(self, assessment: dict, entities: dict) -> tuple:
        """Calculate risk level and score based on assessment"""
        
        urgency = assessment.get("urgency", "routine").lower()
        red_flags = assessment.get("red_flags", [])
        
        # Base score by urgency
        urgency_scores = {
            "emergency": 90,
            "urgent": 70,
            "semi-urgent": 50,
            "routine": 30
        }
        
        base_score = urgency_scores.get(urgency, 30)
        
        # Adjust for red flags
        if red_flags:
            base_score = min(100, base_score + len(red_flags) * 10)
        
        # Determine risk level
        if base_score >= 80:
            risk_level = "high"
        elif base_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, base_score
    
    def _get_fallback_assessment(self) -> dict:
        """Return fallback assessment when AI is unavailable"""
        return {
            "possible_conditions": [
                {"name": "Unable to assess", "likelihood": "unknown", "description": "Please consult a healthcare provider"}
            ],
            "follow_up_questions": [
                "How long have you been experiencing these symptoms?",
                "Have you taken any medications for these symptoms?",
                "Do you have any allergies?"
            ],
            "recommendations": [
                "Please consult with a healthcare professional for proper evaluation",
                "If symptoms worsen, seek immediate medical attention"
            ],
            "urgency": "routine",
            "red_flags": []
        }
    
    async def _store_assessment(
        self,
        assessment_id: str,
        patient_id: Optional[str],
        symptoms: str,
        result: dict
    ):
        """Store assessment in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.table_name)
            
            item = {
                "assessment_id": assessment_id,
                "patient_id": patient_id or "anonymous",
                "symptoms": symptoms,
                "result": result,
                "created_at": datetime.utcnow().isoformat(),
                "ttl": int(datetime.utcnow().timestamp()) + (90 * 24 * 60 * 60)  # 90 days
            }
            
            table.put_item(Item=item)
            logger.info(f"Stored assessment: {assessment_id}")
            
        except ClientError as e:
            logger.error(f"Failed to store assessment: {str(e)}")
            # Don't raise - assessment can still be returned
    
    async def process_followup(self, assessment_id: str, answers: dict) -> dict:
        """Process follow-up question answers and update assessment"""
        try:
            # Get original assessment
            table = self.dynamodb.Table(self.table_name)
            response = table.get_item(Key={"assessment_id": assessment_id})
            
            if 'Item' not in response:
                raise ValueError(f"Assessment not found: {assessment_id}")
            
            original = response['Item']
            
            # Generate updated assessment with follow-up answers
            prompt = f"""Based on the original symptoms and follow-up answers, provide an updated assessment.

Original Symptoms: {original.get('symptoms')}
Follow-up Answers: {json.dumps(answers)}

Provide updated assessment in JSON format with possible_conditions, recommendations, and urgency."""

            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            updated = json.loads(response_body['content'][0]['text'])
            
            return {
                "assessment_id": assessment_id,
                "updated": True,
                **updated
            }
            
        except Exception as e:
            logger.error(f"Error processing follow-up: {str(e)}")
            raise
