import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
vendor_table = dynamodb.Table('vendor')
product_table = dynamodb.Table('products')
tenant_table = dynamodb.Table('tenant')  # Added for tenant support

def lambda_handler(event, context):
    try:
        # Parse body from API Gateway
        if "body" in event and isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event

        update_type = body.get("type")
        if update_type not in ["vendor", "product", "tenant"]:
            return {
                "statusCode": 400,
                "body": {"error": "Invalid type. Must be 'vendor', 'product', or 'tenant'."}
            }

        # Map table and primary key based on type
        table_map = {
            "vendor": (vendor_table, "vendor_id"),
            "product": (product_table, "product_id"),
            "tenant": (tenant_table, "tenant_id")
        }

        table, key_field = table_map[update_type]

        if key_field not in body:
            return {
                "statusCode": 400,
                "body": {"error": f"Missing required field: {key_field}"}
            }

        # Prepare update expressions
        update_expr = []
        expr_attr_vals = {}
        expr_attr_names = {}

        for k, v in body.items():
            if k not in ["type", key_field]:
                update_expr.append(f"#attr_{k} = :val_{k}")
                expr_attr_names[f"#attr_{k}"] = k
                expr_attr_vals[f":val_{k}"] = v

        if not update_expr:
            return {
                "statusCode": 400,
                "body": {"error": "No fields to update"}
            }

        response = table.update_item(
            Key={key_field: body[key_field]},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_vals,
            ReturnValues="UPDATED_NEW"
        )

        return {
            "statusCode": 200,
            "body": {
                "message": f"{update_type.capitalize()} updated successfully",
                "updated_fields": response.get("Attributes", {})
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
