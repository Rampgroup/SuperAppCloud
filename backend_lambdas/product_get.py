import json
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')
table = dynamodb.Table('products')  # Table name

def lambda_handler(event, context):
    # Input validation
    product_id = event.get("product_id")
    if not product_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing product_id in request"})
        }

    try:
        # Get item from DynamoDB
        response = table.get_item(
            Key={
                'product_id': product_id
            }
        )

        # Check if item exists
        item = response.get('Item')
        if not item:
            return {
                "statusCode": 404,
                "body": ({"error": "products not found"})
            }

        return {
            "statusCode": 200,
            "body": (item)
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": ({"error": "Internal server error", "details": str(e)})
        }
