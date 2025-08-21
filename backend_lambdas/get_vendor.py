import json
import boto3
from botocore.exceptions import ClientError
 
region = "ca-central-1"
TABLE_NAME = "vendor"
 
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table(TABLE_NAME)
 
def lambda_handler(event, context):
    try:
        # Support both direct and API Gateway proxy events
        if "body" in event and event["body"]:
            body = json.loads(event["body"])
        else:
            body = event
 
        vendor_id = body.get("vendor_id")
        if not vendor_id:
            return _error("Missing vendor_id in request", 400)
 
        # Query DynamoDB
        response = table.get_item(Key={"vendor_id": vendor_id})
        if "Item" not in response:
            return _error(f"No vendor found with vendor_id: {vendor_id}", 404)
 
        return {
            "statusCode": 200,
            "body": {"vendor": response["Item"]}
        }
 
    except ClientError as e:
        return _error(f"DynamoDB error: {e.response['Error']['Message']}", 500)
    except Exception as e:
        return _error(f"Internal server error: {str(e)}", 500)
 
def _error(message, status_code=400):
    return {
        "statusCode": status_code,
        "body": {"error": message}
    }