import json
import boto3
from boto3.dynamodb.conditions import Attr

REGION = "ca-central-1"
DYNAMODB_TABLE = "products"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    try:
        # Extract input fields
        tenant_id = event.get("tenant_id")
        vendor_id = event.get("vendor_id")
        domain = event.get("domain")
        category = event.get("category")
        subcategory = event.get("subcategory")

        # Validate mandatory fields
        if not tenant_id or not vendor_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "tenant_id and vendor_id are required"
                })
            }

        # Start with base filters
        filter_expr = Attr("tenant_id").eq(tenant_id) & Attr("vendor_id").eq(vendor_id)

        # Add any optional filters present in payload
        if domain:
            filter_expr &= Attr("domain").eq(domain)
        if category:
            filter_expr &= Attr("category").eq(category)
        if subcategory:
            filter_expr &= Attr("subcategory").eq(subcategory)

        # Scan table with constructed filter
        response = table.scan(FilterExpression=filter_expr)
        products = response.get("Items", [])

        return {
            "statusCode": 200,
            "body": {"products": products}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
