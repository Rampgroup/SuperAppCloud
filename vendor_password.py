import boto3
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB table
dynamodb = boto3.resource('dynamodb', region_name="ca-central-1")
vendors_table = dynamodb.Table('vendor')

def lambda_handler(event, context):
    try:
        request_type = event.get("type", "").lower()
        phone_number = event.get("phone_number")
        email = event.get("email")
        password = event.get("password")
        old_password = event.get("old_password")
        new_password = event.get("new_password")
        reenter_password = event.get("reneter_password")

        # Validate request type
        if request_type not in ["update", "login"]:
            return {"statusCode": 400, "message": "Invalid type. Must be 'login' or 'update'."}

        # Identify filter key
        if email:
            filter_expr = Attr("email").eq(email)
        elif phone_number:
            filter_expr = Attr("phone_number").eq(phone_number)
        else:
            return {"statusCode": 400, "message": "Either email or phone_number is required."}

        # Scan the table to find the user
        response = vendors_table.scan(FilterExpression=filter_expr)
        items = response.get("Items", [])
        if not items:
            return {"statusCode": 404, "message": "Vendor not found."}

        vendor = items[0]
        vendor_id = vendor.get("vendor_id")
        tenant_id = vendor.get("tenant_id")
        stored_password = vendor.get("password")

        # Handle login
        if request_type == "login":
            if not password:
                return {"statusCode": 400, "message": "Password is required for login."}
            if password == stored_password:
                return {"statusCode": 200, "message": "Login successful.", "vendor_id": vendor_id, "tenant_id": tenant_id}
            else:
                return {"statusCode": 401, "message": "Invalid password."}

        # Handle update
        elif request_type == "update":
            if not old_password or not new_password or not reenter_password:
                return {"statusCode": 400, "message": "Old, new, and re-enter passwords are required."}
            if new_password != reenter_password:
                return {"statusCode": 400, "message": "New and re-entered passwords do not match."}

            if old_password != stored_password:
                return {"statusCode": 401, "message": "Old password is incorrect."}

            vendors_table.update_item(
                Key={"vendor_id": vendor_id},
                UpdateExpression="SET password = :newpwd",
                ExpressionAttributeValues={":newpwd": new_password}
            )

            return {"statusCode": 200, "message": "Password updated successfully.", "vendor_id": vendor_id, "tenant_id": tenant_id}

    except Exception as e:
        return {"statusCode": 500, "message": "Internal server error", "error": str(e)}
