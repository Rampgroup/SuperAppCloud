# import boto3
# import json

# dynamodb = boto3.resource('dynamodb')

# def lambda_handler(event, context):
#     try:
#         # ✅ For REST API Gateway, body is a string
#         if 'body' in event:
#             body = event['body']
#             if isinstance(body, str):
#                 body = json.loads(body)
#         else:
#             body = event

#         # ✅ Safely extract and lowercase the type
#         table_type = body.get('type', '').lower()

#         # ✅ Only allow 'vendor' or 'tenant'
#         if table_type not in ['vendor', 'tenant']:
#             return {
#                 "statusCode": 400,
#                 "headers": {"Content-Type": "application/json"},
#                 "body": {"error": "Invalid type. Must be 'vendor' or 'tenant'."}
#             }

#         # ✅ Scan correct table
#         table = dynamodb.Table(table_type)
#         response = table.scan()
#         items = response.get('Items', [])

#         return {
#             "statusCode": 200,
#             "headers": {"Content-Type": "application/json"},
#             "body": {
#                 "type": table_type,
#                 "count": len(items),
#                 "data": items
#             }
#         }

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "headers": {"Content-Type": "application/json"},
#             "body": {"error": str(e)}
#         }


import boto3
import json
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Parse body safely
        body = json.loads(event["body"]) if "body" in event and isinstance(event["body"], str) else event

        table_type = body.get('type', '').lower()
        if table_type not in ['vendor', 'tenant']:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": {"error": "Invalid type. Must be 'vendor' or 'tenant'."}
            }

        table = dynamodb.Table(table_type)

        if table_type == "vendor" and "tenant_id" in body:
            response = table.scan(
                FilterExpression=Attr("tenant_id").eq(body["tenant_id"])
            )
        else:
            response = table.scan()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "type": table_type,
                "count": len(response.get("Items", [])),
                "data": response.get("Items", [])
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": {"error": str(e)}
        }
