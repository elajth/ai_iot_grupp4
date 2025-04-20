import boto3
import json
import random

s3 = boto3.client('s3')

SOURCE_BUCKET = 'mock-camera-samples'
DEST_BUCKET = 'sheepsafe-wolves'
WOLF_IMAGE = 'wolf.png'
EMPTY_IMAGE = 'nothing.png'

def lambda_handler(event, context):

    # Extrahera motion från event direkt
    motion_detected = event.get('motion', False)

    if not motion_detected:
        print("Ingen rörelse, ingen bild tas.")
        return {'statusCode': 200, 'body': 'No motion detected'}

    # Välj bild
    chosen_image = EMPTY_IMAGE if random.random() < 0.5 else WOLF_IMAGE
    #chosen_image = WOLF_IMAGE
    destination_key = f'snapshot_{context.aws_request_id}.jpg'

    print(f"Kopierar {chosen_image} till {destination_key}")

    # Kopiera bild till destination
    s3.copy_object(
        Bucket=DEST_BUCKET,
        CopySource={'Bucket': SOURCE_BUCKET, 'Key': chosen_image},
        Key=destination_key,
        ContentType='image/jpeg'
    )

    return {
        'statusCode': 200,
        'body': f"Copied {chosen_image} to {destination_key}"
    }
