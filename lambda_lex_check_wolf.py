import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Wolf_Observations')

def lambda_handler(event, context):
    today = datetime.utcnow().date().isoformat()

    response = table.scan()
    items = response.get('Items', [])

    wolves_today = [
        item for item in items
        if item.get('label') == 'wolf' and item.get('timestamp', '').startswith(today)
    ]

    if wolves_today:
        msg = f"There have been {len(wolves_today)} wolf detection(s) today."
    else:
        msg = "No wolf detections recorded today."

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": event['sessionState']['intent']['name'],
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": msg
            }
        ]
    }
