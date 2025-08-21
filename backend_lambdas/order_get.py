import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders')  # Replace with your actual table name if different

def lambda_handler(event, context):
    order_id = event.get("order_id")

    if not order_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'order_id' in the payload."})
        }

    try:
        response = table.get_item(
            Key={
                'order_id': order_id
            }
        )

        item = response.get("Item")

        if not item:
            return {
                "statusCode": 200,
                "body": {}
            }

        return {
            "statusCode": 200,
            "body": item
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": f"Internal server error: {str(e)}"}
        }
