import json
import boto3
import re
import hashlib
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

REGION = "ca-central-1"
TABLE_NAME = "user"
dynamodb = boto3.resource("dynamodb", region_name=REGION)
client = boto3.client("dynamodb", region_name=REGION)

def ensure_table_exists():
    try:
        client.describe_table(TableName=TABLE_NAME)
    except client.exceptions.ResourceNotFoundException:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode='PAY_PER_REQUEST'
        )
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)

def generate_next_user_id(table):
    response = table.scan(ProjectionExpression="user_id")
    user_ids = [item["user_id"] for item in response.get("Items", []) if "user_id" in item]
    max_num = 0
    for uid in user_ids:
        match = re.match(r"USR_(\d+)", uid)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"USR_{max_num + 1:02d}"

def get_ist_time():
    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%d-%m-%Y, %I:%M %p")

def lambda_handler(event, context):
    try:
        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)

        action = body.get("type", "").lower()
        ensure_table_exists()
        table = dynamodb.Table(TABLE_NAME)

        if action == "create":
            required_fields = ["user_name", "phone_number", "password", "gender"]
            missing = [f for f in required_fields if not body.get(f)]
            if missing:
                return {
                    "statusCode": 400,
                    "body": {"error": f"Missing required fields: {', '.join(missing)}"}
                }

            phone = body.get("phone_number", "").strip()
            existing = table.scan(
                FilterExpression=Attr("phone_number").eq(phone),
                ProjectionExpression="user_id"
            )
            if existing.get("Items"):
                return {
                    "statusCode": 200,
                    "body": {"error": "Phone number already exists"}
                }

            user_id = generate_next_user_id(table)
            hashed_password = hashlib.sha256(body["password"].encode()).hexdigest()
            item = {
                "user_id": user_id,
                "user_name": body["user_name"],
                "phone_number": phone,
                "password": hashed_password,
                "email": body.get("email", ""),
                "gender": body["gender"],
                "created_at": get_ist_time()
            }

            if "email" in body and body["email"]:
                item["email"] = body["email"]

            table.put_item(Item=item)

            return {
                "statusCode": 200,
                "body": {
                    "message": "User created successfully",
                    "user_id": user_id
                }
            }

        elif action == "login":
            phone_number = body.get("phone_number", "").strip()
            password = body.get("password", "").strip()
            hashed_password = hashlib.sha256(body["password"].encode()).hexdigest()

            if not phone_number or not password:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing phone_number or password"})
                }

            response = table.scan(
                FilterExpression=Attr("phone_number").eq(phone_number) & Attr("password").eq(hashed_password)
            )
            items = response.get("Items", [])

            if not items:
                return {
                    "statusCode": 200,
                    "body": {"error": "Invalid phone number or password"}
                }

            user = items[0]
            user.pop("password", None)

            return {
                "statusCode": 200,
                "body": {
                    "message": "Login successful",
                    "user": user
                }
            }

        else:
            return {
                "statusCode": 400,
                "body": {"error": "Invalid type. Must be 'create' or 'login'"}
            }

    except ClientError as e:
        return {"statusCode": 500, "body": {"error": str(e)}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": "Internal server error", "details": str(e)}}
