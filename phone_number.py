import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user')

def lambda_handler(event, context):
    phone_number = event.get('phone_number')
    
    if not phone_number:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing phone_number in request"})
        }

    try:
        # Using scan instead of query
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('phone_number').eq(phone_number)
        )
        
        items = response.get('Items', [])
        
        if not items:
            return {
                "statusCode": 404,
                "body":{"message": "User not found"}
            }

        user = items[0]

        return {
            "statusCode": 200,
            "body": {
                "user_id": user.get("user_id"),
                "created_at": user.get("created_at"),
                "gender": user.get("gender"),
                #"password": user.get("password"),
                "phone_number": user.get("phone_number"),
                "user_name": user.get("user_name"),
                "email":user.get("email")
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
