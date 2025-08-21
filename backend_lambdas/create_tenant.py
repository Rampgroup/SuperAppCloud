# import json
# import boto3
# from datetime import datetime
# import dateutil.tz

# # Initialize DynamoDB once per container
# ddb = boto3.resource('dynamodb')
# TABLE_NAME = 'tenant'  # Replace with your DynamoDB table name

# def lambda_handler(event, context):
#     table = ddb.Table(TABLE_NAME)
    
#     # Increment the tenant counter atomically
#     response = table.update_item(
#         Key={'tenant_id': 'tenant_counter'},
#         UpdateExpression="SET tenant_count = if_not_exists(tenant_count, :start) + :incr",
#         ExpressionAttributeValues={':start': 0, ':incr': 1},
#         ReturnValues="UPDATED_NEW"
#     )
#     tenant_count = response['Attributes'].get('tenant_count', 0)
    
#     # Ensure tenant_count is an integer
#     tenant_count = int(tenant_count)
    
#     # Format tenant_id with leading zeros
#     tenant_id = f"tnt_{tenant_count:04d}"
    
#     # Get current time in IST using dateutil
#     india_timezone = dateutil.tz.gettz('Asia/Kolkata')
#     now = datetime.now(india_timezone).strftime("%d/%m/%Y, %I:%M %p")  # Format: 02/07/2025, 11:41 AM
    
#     # Build item with all values as strings
#     item = {
#         "tenant_id": tenant_id,
#         "time": now,
#         "tenant_name": event.get("tenant_name", ""),
#         "app_type": event.get("app_type", ""),
#         "domain_id": event.get("domain_id", ""),
#         "domain": event.get("domain", ""),
#         "address": event.get("address", ""),
#         "email": event.get("email", ""),
#         "phone_number": event.get("phone_number", ""),
#         "primary_color": event.get("primary_color", ""),
#         "language": event.get("language", ""),
#         "timezone": event.get("timezone", ""),
#         "status": event.get("status", ""),
#         "plan_type": event.get("plan_type", "")
#     }
    
#     # Insert into DynamoDB
#     try:
#         table.put_item(Item=item)
#         return {
#             "statusCode": 200,
#             "body": json.dumps({"message": "Tenant inserted", "tenant_id": tenant_id})
#         }
#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"message": "Failed to insert tenant", "error": str(e)})
#         }



import json
import boto3
from datetime import datetime
import dateutil.tz

ddb = boto3.resource('dynamodb')
TABLE_NAME = 'tenant'

def lambda_handler(event, context):
    # Handle Postman (API Gateway) JSON body
    if isinstance(event.get("body"), str):
        try:
            event = json.loads(event["body"])
        except Exception:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid JSON format in body"})
            }

    table = ddb.Table(TABLE_NAME)

    try:
        # Count existing tenants (excluding items that don't match pattern)
        scan_response = table.scan(
            ProjectionExpression="tenant_id"
        )
        tenant_items = scan_response.get('Items', [])
        
        # Filter valid tenant_ids like 'TNT_01'
        tenant_ids = [
            item['tenant_id'] for item in tenant_items
            if item.get('tenant_id', '').startswith('TNT_')
        ]
        
        # Extract numeric part and find max
        max_num = 0
        for tid in tenant_ids:
            try:
                num = int(tid.split('_')[1])
                if num > max_num:
                    max_num = num
            except:
                continue
        
        new_tenant_id = f"TNT_{max_num + 1:02d}"

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error generating tenant_id", "error": str(e)})
        }

    # Current time in IST
    india_timezone = dateutil.tz.gettz('Asia/Kolkata')
    now = datetime.now(india_timezone).strftime("%d/%m/%Y, %I:%M %p")

    item = {
        "tenant_id": new_tenant_id,
        "time": now,
        "tenant_name": event.get("tenant_name", ""),
        "app_type": event.get("app_type", ""),
        "domain_id": event.get("domain_id", ""),
        "domain": event.get("domain", ""),
        "address": event.get("address", ""),
        "email": event.get("email", ""),
        "phone_number": event.get("phone_number", ""),
        "primary_color": event.get("primary_color", ""),
        "language": event.get("language", ""),
        "timezone": event.get("timezone", ""),
        "status": event.get("status", ""),
        "plan_type": event.get("plan_type", "")
    }

    try:
        table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": {
                "message": "Tenant inserted",
                "tenant_id": new_tenant_id
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Failed to insert tenant", "error": str(e)})
        }
