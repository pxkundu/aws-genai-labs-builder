"""
Triage Service - AI-powered patient prioritization
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


class TriageService:
    """Virtual triage service for patient prioritization"""
    
    # Triage levels with priorities
    TRIAGE_LEVELS = {
        "emergency": {"priority": 1, "color": "red", "max_wait": "immediate"},
        "urgent": {"priority": 2, "color": "orange", "max_wait": "1 hour"},
        "semi-urgent": {"priority": 3, "color": "yellow", "max_wait": "4 hours"},
        "non-urgent": {"priority": 4, "color": "green", "max_wait": "24 hours"},
        "routine": {"priority": 5, "color": "blue", "max_wait": "scheduled"}
    }
    
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.sns = boto3.client(
            'sns',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.assessments_table = os.getenv('DYNAMODB_ASSESSMENTS_TABLE', 'telemedicine-assessments')
        self.sessions_table = os.getenv('DYNAMODB_SESSIONS_TABLE', 'telemedicine-sessions')
    
    async def evaluate_triage(
        self,
        assessment_id: str,
        patient_id: Optional[str] = None,
        vital_signs: Optional[dict] = None
    ) -> dict:
        """
        Evaluate triage level based on assessment
        
        Args:
            assessment_id: ID of the symptom assessment
            patient_id: Optional patient identifier
            vital_signs: Optional vital signs data
            
        Returns:
            Triage evaluation with level, priority, and recommendations
        """
        triage_id = str(uuid.uuid4())
        
        try:
            # Get assessment data
            assessment = await self._get_assessment(assessment_id)
            
            if not assessment:
                raise ValueError(f"Assessment not found: {assessment_id}")
            
            # Evaluate triage with AI
            triage_result = await self._ai_triage_evaluation(
                assessment=assessment,
                vital_signs=vital_signs
            )
            
            # Determine triage level
            triage_level = triage_result.get("triage_level", "routine")
            level_info = self.TRIAGE_LEVELS.get(triage_level, self.TRIAGE_LEVELS["routine"])
            
            result = {
                "triage_id": triage_id,
                "triage_level": triage_level,
                "priority": level_info["priority"],
                "recommended_action": triage_result.get("recommended_action", "Schedule appointment"),
                "estimated_wait_time": level_info["max_wait"],
                "provider_notes": triage_result.get("provider_notes", ""),
                "alert_sent": False
            }
            
            # Send alerts for high-priority cases
            if level_info["priority"] <= 2:
                await self._send_alert(result, assessment, patient_id)
                result["alert_sent"] = True
            
            # Store triage result
            await self._store_triage(triage_id, assessment_id, patient_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in triage evaluation: {str(e)}")
            raise
    
    async def _get_assessment(self, assessment_id: str) -> Optional[dict]:
        """Retrieve assessment from DynamoDB"""
        try:
            table = self.dynamodb.Table(self.assessments_table)
            response = table.get_item(Key={"assessment_id": assessment_id})
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error retrieving assessment: {str(e)}")
            return None
    
    async def _ai_triage_evaluation(
        self,
        assessment: dict,
        vital_signs: Optional[dict]
    ) -> dict:
        """Use AI to evaluate triage level"""
        
        result = assessment.get('result', {})
        
        prompt = f"""You are a medical triage specialist. Evaluate the following patient assessment and determine the appropriate triage level.

Assessment Information:
- Symptoms: {assessment.get('symptoms', 'Not provided')}
- Risk Level: {result.get('risk_level', 'unknown')}
- Risk Score: {result.get('risk_score', 0)}
- Possible Conditions: {json.dumps(result.get('possible_conditions', []))}
- Urgency Indicated: {result.get('urgency', 'routine')}

Vital Signs: {json.dumps(vital_signs) if vital_signs else 'Not provided'}

Triage Levels (choose one):
1. emergency - Life-threatening, immediate attention required
2. urgent - Serious condition, needs attention within 1 hour
3. semi-urgent - Moderate symptoms, can wait up to 4 hours
4. non-urgent - Minor issues, can wait up to 24 hours
5. routine - General inquiries, can be scheduled

Provide your evaluation in JSON format:
{{
    "triage_level": "one of the levels above",
    "reasoning": "brief explanation",
    "recommended_action": "specific action to take",
    "provider_notes": "notes for the healthcare provider",
    "escalation_needed": true/false
}}

Respond ONLY with the JSON object."""

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI triage evaluation error: {str(e)}")
            # Fallback based on risk score
            risk_score = result.get('risk_score', 30)
            if risk_score >= 80:
                return {"triage_level": "urgent", "recommended_action": "Seek immediate care"}
            elif risk_score >= 50:
                return {"triage_level": "semi-urgent", "recommended_action": "Schedule same-day appointment"}
            else:
                return {"triage_level": "routine", "recommended_action": "Schedule regular appointment"}
    
    async def _send_alert(self, triage: dict, assessment: dict, patient_id: Optional[str]):
        """Send alert for high-priority triage cases"""
        try:
            topic_arn = os.getenv('SNS_ALERT_TOPIC_ARN')
            
            if not topic_arn:
                logger.warning("SNS topic ARN not configured, skipping alert")
                return
            
            message = {
                "alert_type": "HIGH_PRIORITY_TRIAGE",
                "triage_id": triage["triage_id"],
                "triage_level": triage["triage_level"],
                "patient_id": patient_id or "anonymous",
                "symptoms": assessment.get("symptoms", ""),
                "recommended_action": triage["recommended_action"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject=f"🚨 {triage['triage_level'].upper()} Triage Alert"
            )
            
            logger.info(f"Alert sent for triage: {triage['triage_id']}")
            
        except ClientError as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    async def _store_triage(
        self,
        triage_id: str,
        assessment_id: str,
        patient_id: Optional[str],
        result: dict
    ):
        """Store triage result in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            item = {
                "session_id": triage_id,
                "session_type": "triage",
                "assessment_id": assessment_id,
                "patient_id": patient_id or "anonymous",
                "result": result,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "ttl": int(datetime.utcnow().timestamp()) + (7 * 24 * 60 * 60)  # 7 days
            }
            
            table.put_item(Item=item)
            logger.info(f"Stored triage: {triage_id}")
            
        except ClientError as e:
            logger.error(f"Failed to store triage: {str(e)}")
    
    async def get_queue(self) -> list:
        """Get current triage queue sorted by priority"""
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            # Scan for pending triage sessions
            response = table.scan(
                FilterExpression="session_type = :type AND #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":type": "triage",
                    ":status": "pending"
                }
            )
            
            items = response.get('Items', [])
            
            # Sort by priority
            queue = []
            for item in items:
                result = item.get('result', {})
                queue.append({
                    "triage_id": item.get('session_id'),
                    "patient_id": item.get('patient_id'),
                    "triage_level": result.get('triage_level', 'routine'),
                    "priority": result.get('priority', 5),
                    "estimated_wait_time": result.get('estimated_wait_time', 'scheduled'),
                    "created_at": item.get('created_at')
                })
            
            # Sort by priority (lower = higher priority)
            queue.sort(key=lambda x: (x['priority'], x['created_at']))
            
            return queue
            
        except ClientError as e:
            logger.error(f"Error getting triage queue: {str(e)}")
            return []
    
    async def update_status(self, triage_id: str, status: str) -> bool:
        """Update triage status"""
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            table.update_item(
                Key={"session_id": triage_id},
                UpdateExpression="SET #status = :status, updated_at = :updated",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": status,
                    ":updated": datetime.utcnow().isoformat()
                }
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Error updating triage status: {str(e)}")
            return False
