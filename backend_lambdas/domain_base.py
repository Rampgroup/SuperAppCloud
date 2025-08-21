import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('categories')

def lambda_handler(event, context):
    try:
        domain = event.get("domain")
        if not domain:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'domain' in payload"})
            }

        # Map 'pharma' to 'Pharmaceuticals', otherwise capitalize
        normalized_domain = "Pharmaceuticals" if domain.lower() == "pharma" else domain.capitalize()

        response = table.scan(
            FilterExpression=Attr('domain').eq(normalized_domain)
        )

        items = response.get('Items', [])

        seen_categories = set()
        unique_results = []

        for item in items:
            category = item.get("category")
            category_id = item.get("category_id")
            if category and category not in seen_categories:
                seen_categories.add(category)
                unique_results.append({
                    "category_id": category_id,
                    "category": category
                })

        return {
            "statusCode": 200,
            "body": unique_results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
