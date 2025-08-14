import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('categories')  # Make sure this matches your table name

def lambda_handler(event, context):
    try:
        category = event.get("category")
        if not category:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'category' in input"}
            }

        # Filter by category value
        response = table.scan(
            FilterExpression=Attr('category').eq(category)
        )

        items = response.get('Items', [])
        if not items:
            return {
                "statusCode": 404,
                "body": {"message": "No subcategories found for given category"}
            }

        # Extract category_id and subcategory
        results = [
            {
                "category_id": item["category_id"],
                "subcategory": item.get("subcategory", ""),
                "subcategory_image":item.get("subcategory_image", "")
            }
            for item in items if "category_id" in item and "subcategory" in item
        ]

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
