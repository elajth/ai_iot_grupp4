import boto3
import json
import uuid
import random
from datetime import datetime

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Wolf_Observations')
sns = boto3.client('sns')
topic_arn = 'arn:aws:sns:us-east-1:940482426560:WolfAlert'

MODEL_ARN = 'arn:aws:rekognition:us-east-1:940482426560:project/SheepSafe-Wolf-Detection/version/SheepSafe-Wolf-Detection.2025-04-08T16.38.52/1744123131325'

locations = ["Östhage", "Granskog", "Björkdal", "Rävlanda", "Vargträsk"]

def lambda_handler(event, context):
    print("🪵 Full event från S3-trigger:", json.dumps(event))
    if event.get("test") == "sns_only":
        print("📨 Testar SNS-publicering...")
        sns.publish(
            TopicArn=topic_arn,
            Message="🔔 This is a test alert from SheepSafe system.",
            Subject="Test: SheepSafe Alert"
        )
        return {
            'statusCode': 200,
            'body': json.dumps("Test-SNS published.")
        }

    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        print(f"📸 Bild mottagen: {key} i bucket: {bucket}")
    except KeyError as e:
        print(f"❌ Kunde inte läsa bucket eller key: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps('Felaktigt eventformat – Lambda ska triggas av S3.')
        }

    try:
        print("📤 Skickar bild till Rekognition...")
        response = rekognition.detect_custom_labels(
            ProjectVersionArn=MODEL_ARN,
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MinConfidence=70
        )
        print(f"✅ Rekognition-resultat: {response}")
    except Exception as e:
        print(f"❌ Fel vid anrop till Rekognition: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Fel vid bildanalys.')
        }

    labels = [label['Name'] for label in response['CustomLabels']]
    print(f"🔍 Extraherade etiketter: {labels}")

    if "wolf" in [label.lower() for label in labels]:
        print("🟥 WOLF identifierad – sparar till DynamoDB")

        distance = random.randint(10, 300)
        location = random.choice(locations)

        item = {
            'id': int(uuid.uuid4().int >> 64),
            'timestamp': datetime.utcnow().isoformat(),
            'image': key,
            'bucket': bucket,
            'label': 'wolf',
            'location': location,
            'distance': distance,
            'message': f"🐺 Wolf detected {distance} meters from {location}!"
        }

        try:
            table.put_item(Item=item)
            print(f"✅ Observation sparad i DynamoDB: {item}")
        except Exception as e:
            print(f"❌ Fel vid skrivning till DynamoDB: {e}")

        sns.publish(
            TopicArn=topic_arn,
            Message="⚠️ Wolf detected near the sheep farm!",
            Subject="SheepSafe Alert"
        )
    else:
        print("🟩 Ingen wolf – ingen åtgärd.")

    return {
        'statusCode': 200,
        'body': json.dumps('Lambda körd klart.')
    }
