import boto3
import json
import random
from datetime import datetime

iot = boto3.client('iot-data', region_name='us-east-1')  # byt region om nödvändigt

def lambda_handler(event, context):
    payload = {
        "motion": random.choice([True, False]),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = iot.publish(
        topic='sensor/motion',
        qos=1,
        payload=json.dumps(payload)
    )
    
    return {
        'statusCode': 200,
        'body': f'Motion published: {payload}'
    }
