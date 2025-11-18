"""
Enhanced Lambda Processor for IoT Telemetry

This Lambda function enriches incoming IoT messages with:
- Device metadata lookup
- Anomaly detection
- Geospatial enrichment (if coordinates present)
- Alert generation for threshold violations
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
sns = boto3.client('sns', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Optional: Device metadata table (create separately if needed)
DEVICE_METADATA_TABLE = os.environ.get('DEVICE_METADATA_TABLE', '')
ALERT_SNS_TOPIC = os.environ.get('ALERT_SNS_TOPIC', '')

# Thresholds for anomaly detection
TEMP_THRESHOLD_HIGH = float(os.environ.get('TEMP_THRESHOLD_HIGH', '85.0'))
TEMP_THRESHOLD_LOW = float(os.environ.get('TEMP_THRESHOLD_LOW', '5.0'))
HUMIDITY_THRESHOLD_HIGH = float(os.environ.get('HUMIDITY_THRESHOLD_HIGH', '90.0'))


def get_device_metadata(device_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve device metadata from DynamoDB if table exists."""
    if not DEVICE_METADATA_TABLE:
        return None
    
    try:
        table = dynamodb.Table(DEVICE_METADATA_TABLE)
        response = table.get_item(Key={'deviceId': device_id})
        return response.get('Item')
    except Exception as e:
        print(f"Error fetching device metadata: {e}")
        return None


def detect_anomalies(payload: Dict[str, Any]) -> list:
    """Detect anomalies in telemetry data."""
    anomalies = []
    
    if 'temperature' in payload:
        temp = payload['temperature']
        if temp > TEMP_THRESHOLD_HIGH:
            anomalies.append({
                'type': 'high_temperature',
                'value': temp,
                'threshold': TEMP_THRESHOLD_HIGH,
                'severity': 'critical' if temp > 90 else 'warning'
            })
        elif temp < TEMP_THRESHOLD_LOW:
            anomalies.append({
                'type': 'low_temperature',
                'value': temp,
                'threshold': TEMP_THRESHOLD_LOW,
                'severity': 'warning'
            })
    
    if 'humidity' in payload:
        humidity = payload['humidity']
        if humidity > HUMIDITY_THRESHOLD_HIGH:
            anomalies.append({
                'type': 'high_humidity',
                'value': humidity,
                'threshold': HUMIDITY_THRESHOLD_HIGH,
                'severity': 'warning'
            })
    
    if 'vibration' in payload:
        vibration = payload['vibration']
        if vibration > 4.0:
            anomalies.append({
                'type': 'high_vibration',
                'value': vibration,
                'threshold': 4.0,
                'severity': 'critical'
            })
    
    return anomalies


def send_alert(device_id: str, anomalies: list, payload: Dict[str, Any]):
    """Send alert via SNS if topic is configured."""
    if not ALERT_SNS_TOPIC or not anomalies:
        return
    
    critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
    if not critical_anomalies:
        return
    
    alert_message = {
        'deviceId': device_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'anomalies': critical_anomalies,
        'originalPayload': payload
    }
    
    try:
        sns.publish(
            TopicArn=ALERT_SNS_TOPIC,
            Subject=f"Critical Alert: {device_id}",
            Message=json.dumps(alert_message, indent=2)
        )
        print(f"Alert sent for device {device_id}: {critical_anomalies}")
    except Exception as e:
        print(f"Error sending alert: {e}")


def enrich_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich payload with metadata and computed fields."""
    enriched = payload.copy()
    device_id = payload.get('deviceId', 'unknown')
    
    # Add processing metadata
    enriched['_processing'] = {
        'processedAt': datetime.utcnow().isoformat() + 'Z',
        'processor': 'lambda-enrichment',
        'version': '1.0'
    }
    
    # Add device metadata if available
    metadata = get_device_metadata(device_id)
    if metadata:
        enriched['_deviceMetadata'] = {
            'location': metadata.get('location'),
            'manufacturer': metadata.get('manufacturer'),
            'model': metadata.get('model'),
            'firmwareVersion': metadata.get('firmwareVersion')
        }
    
    # Detect anomalies
    anomalies = detect_anomalies(payload)
    if anomalies:
        enriched['_anomalies'] = anomalies
        enriched['hasAnomalies'] = True
        send_alert(device_id, anomalies, payload)
    else:
        enriched['hasAnomalies'] = False
    
    # Geospatial enrichment (if coordinates present)
    if 'latitude' in payload and 'longitude' in payload:
        # In production, you might call a geocoding service here
        enriched['_geospatial'] = {
            'coordinates': [payload['longitude'], payload['latitude']],
            'type': 'Point'
        }
    
    return enriched


def lambda_handler(event, context):
    """
    Process IoT messages from Kinesis.
    
    Event structure (Kinesis):
    {
        "Records": [
            {
                "kinesis": {
                    "data": "base64-encoded-payload"
                }
            }
        ]
    }
    """
    processed_records = []
    
    for record in event.get('Records', []):
        try:
            # Decode Kinesis record
            if 'kinesis' in record:
                payload_data = record['kinesis']['data']
                import base64
                decoded = base64.b64decode(payload_data).decode('utf-8')
                payload = json.loads(decoded)
            else:
                # Direct JSON payload (for testing)
                payload = record if isinstance(record, dict) else json.loads(record)
            
            # Enrich payload
            enriched = enrich_payload(payload)
            processed_records.append(enriched)
            
        except Exception as e:
            print(f"Error processing record: {e}")
            print(f"Record: {record}")
            continue
    
    return {
        'statusCode': 200,
        'processedCount': len(processed_records),
        'records': processed_records
    }

