# import json
# import boto3
# from datetime import datetime
# import dateutil.tz

# ddb = boto3.resource('dynamodb')
# TABLE_NAME = 'vendor'

# def lambda_handler(event, context):
#     # Handle Postman (API Gateway) JSON body
#     if isinstance(event.get("body"), str):
#         try:
#             event = json.loads(event["body"])
#         except Exception:
#             return {
#                 "statusCode": 400,
#                 "body": json.dumps({"message": "Invalid JSON format in body"})
#             }

#     table = ddb.Table(TABLE_NAME)

#     try:
#         # Count existing vendors (excluding items that don't match pattern)
#         scan_response = table.scan(
#             ProjectionExpression="vendor_id"
#         )
#         vendor_items = scan_response.get('Items', [])
        
#         # Filter valid vendor_ids like 'TNT_01'
#         vendor_ids = [
#             item['vendor_id'] for item in vendor_items
#             if item.get('vendor_id', '').startswith('VND_')
#         ]
        
#         # Extract numeric part and find max
#         max_num = 0
#         for tid in vendor_ids:
#             try:
#                 num = int(tid.split('_')[1])
#                 if num > max_num:
#                     max_num = num
#             except:
#                 continue
        
#         new_vendor_id = f"VND_{max_num + 1:02d}"

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"message": "Error generating vendor_id", "error": str(e)})
#         }

#     # Current time in IST
#     india_timezone = dateutil.tz.gettz('Asia/Kolkata')
#     now = datetime.now(india_timezone).strftime("%d/%m/%Y, %I:%M %p")
#     print("A", event)
#     item = {
#         "vendor_id": new_vendor_id,
#         "time": now,
#         "vendor_name": event.get("vendor_name", ""),
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
#         "plan_type": event.get("plan_type", ""),
#         "tenant_id":event.get("tenant_id","TNT001")
#     }

#     try:
#         table.put_item(Item=item)
#         return {
#             "statusCode": 200,
#             "body": {
#                 "message": "vendor inserted",
#                 "vendor_id": new_vendor_id
#             }
#         }

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"message": "Failed to insert vendor", "error": str(e)})
#         }

# import json
# import boto3
# import re
# from datetime import datetime
# import dateutil.tz
# from boto3.dynamodb.conditions import Attr

# region = "ca-central-1"
# ddb = boto3.resource('dynamodb', region_name=region)

# VENDOR_TABLE = ddb.Table('vendor')
# METADATA_TABLE = ddb.Table('metadata')
# PRODUCT_TABLE = ddb.Table('products')

# def lambda_handler(event, context):
#     # Handle Postman (API Gateway) JSON body
#     if isinstance(event.get("body"), str):
#         try:
#             event = json.loads(event["body"])
#         except Exception:
#             return {
#                 "statusCode": 400,
#                 "body": json.dumps({"message": "Invalid JSON format in body"})
#             }

#     try:
#         # Generate vendor_id
#         print("A", event)
#         scan_response = VENDOR_TABLE.scan(ProjectionExpression="vendor_id")
#         vendor_items = scan_response.get('Items', [])

#         vendor_ids = [
#             item['vendor_id'] for item in vendor_items
#             if item.get('vendor_id', '').startswith('VND_')
#         ]

#         max_num = 0
#         for vid in vendor_ids:
#             try:
#                 num = int(vid.split('_')[1])
#                 max_num = max(max_num, num)
#             except:
#                 continue

#         new_vendor_id = f"VND_{max_num + 1:02d}"

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"message": "Error generating vendor_id", "error": str(e)})
#         }

#     india_timezone = dateutil.tz.gettz('Asia/Kolkata')
#     now = datetime.now(india_timezone).strftime("%d/%m/%Y, %I:%M %p")

#     vendor_item = {
#         "vendor_id": new_vendor_id,
#         "time": now,
#         "vendor_name": event.get("vendor_name", ""),
#         "app_type": event.get("app_type", ""),
#         "domain_id": event.get("domain_id", ""),
#         "domain": event.get("domain", ""),
#         "address": event.get("address", ""),
#         "email": event.get("email", ""),
#         "phone_number": event.get("phone_number", ""),
#         "primary_color": event.get("primary_color", ""),
#         "vendor_location": event.get("vendor_location", {}),
#         "language": event.get("language", ""),
#         "timezone": event.get("timezone", ""),
#         "status": event.get("status", ""),
#         "plan_type": event.get("plan_type", ""),
#         "tenant_id": event.get("tenant_id", "TNT001")
#     }

#     try:
#         VENDOR_TABLE.put_item(Item=vendor_item)
#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": {"message": "Failed to insert vendor", "error": str(e)}
#         }

#     # ➕ Additional: Fetch from metadata and insert into products
#     try:
#         domain = event.get("domain", "").capitalize()
#         meta_response = METADATA_TABLE.scan(
#             FilterExpression=Attr("domain").eq(domain)
#         )
#         meta_items = meta_response.get('Items', [])

#         # Get current max product_id
#         existing = PRODUCT_TABLE.scan(ProjectionExpression='product_id')
#         existing_ids = [int(re.search(r'PROD_(\d+)', i['product_id']).group(1))
#                         for i in existing.get("Items", []) if re.match(r'PROD_\d+', i.get('product_id', ''))]
#         next_index = max(existing_ids, default=0) + 1

#         for item in meta_items:
#             product = {}
#             for k, v in item.items():
#                 if k == "product_description":
#                     product["description"] = v
#                 elif k != "metadata_id":
#                     product[k] = v
#             # product = {k: v for k, v in item.items() if k != "metadata_id"}
#             product["product_id"] = f"PROD_{next_index:02d}"
#             product["tenant_id"] = vendor_item["tenant_id"]
#             product["vendor_id"] = new_vendor_id
#             PRODUCT_TABLE.put_item(Item=product)
#             next_index += 1

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": {"message": "Vendor created, but failed to insert products", "error": str(e)}
#         }

#     return {
#         "statusCode": 200,
#         "body": {
#             "message": "Vendor inserted and metadata products added",
#             "vendor_id": new_vendor_id
#         }
#     }

import json, random, string
import boto3
import re, hashlib
from datetime import datetime
import dateutil.tz
from boto3.dynamodb.conditions import Attr, Or

region = "ca-central-1"
ddb = boto3.resource('dynamodb', region_name=region)

VENDOR_TABLE = ddb.Table('vendor')
METADATA_TABLE = ddb.Table('metadata')
PRODUCT_TABLE = ddb.Table('products')

def lambda_handler(event, context):
    if isinstance(event.get("body"), str):
        try:
            event = json.loads(event["body"])
        except Exception:
            return {
                "statusCode": 400,
                "body": {"message": "Invalid JSON format in body"}
            }

    email = event.get("email", "").strip()
    phone = event.get("phone_number", "").strip()

    # ✅ Check for existing vendor with same email or phone_number
    try:
        filter_expr = Attr("email").eq(email) | Attr("phone_number").eq(phone)
        existing = VENDOR_TABLE.scan(
            FilterExpression=filter_expr,
            ProjectionExpression="vendor_id, email, phone_number"
        )
        if existing.get("Items"):
            return {
                "statusCode": 400,
                "body": {"error": "Vendor with the same email or phone number already exists"}
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Error checking duplicates", "error": str(e)}
        }

    # ✅ Generate vendor_id
    try:
        scan_response = VENDOR_TABLE.scan(ProjectionExpression="vendor_id")
        vendor_items = scan_response.get('Items', [])

        vendor_ids = [
            item['vendor_id'] for item in vendor_items
            if item.get('vendor_id', '').startswith('VND_')
        ]

        max_num = 0
        for vid in vendor_ids:
            try:
                num = int(vid.split('_')[1])
                max_num = max(max_num, num)
            except:
                continue

        new_vendor_id = f"VND_{max_num + 1:02d}"

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Error generating vendor_id", "error": str(e)}
        }

    india_timezone = dateutil.tz.gettz('Asia/Kolkata')
    now = datetime.now(india_timezone).strftime("%d/%m/%Y, %I:%M %p")

    chars = string.ascii_letters + string.digits  # a-zA-Z0-9
    password = ''.join(random.choices(chars, k=8))
    static_password = "Vendor@123"
    # hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    vendor_item = {
        "vendor_id": new_vendor_id,
        "time": now,
        "vendor_name": event.get("vendor_name", ""),
        "app_type": event.get("app_type", ""),
        # "password": password,
        "password": static_password,
        # "password": hashed_password,
        # "domain_id": event.get("domain_id", ""),
        "domain": event.get("domain", ""),
        "address": event.get("address", ""),
        "email": email,
        "phone_number": phone,
        "primary_color": event.get("primary_color", ""),
        "vendor_location": event.get("vendor_location", {}),
        "language": event.get("language", ""),
        "timezone": event.get("timezone", ""),
        "status": event.get("status", ""),
        "plan_type": event.get("plan_type", ""),
        "tenant_id": event.get("tenant_id", "TNT001")
    }

    try:
        VENDOR_TABLE.put_item(Item=vendor_item)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Failed to insert vendor", "error": str(e)}
        }

    # ➕ Add metadata products
    try:
        raw_domain = event.get("domain", "").strip().lower()
        domain_for_metadata = "Pharmaceuticals" if raw_domain == "pharma" else event.get("domain", "").capitalize()

        meta_response = METADATA_TABLE.scan(
            FilterExpression=Attr("domain").eq(domain_for_metadata)
        )
        meta_items = meta_response.get('Items', [])

        existing = PRODUCT_TABLE.scan(ProjectionExpression='product_id')
        existing_ids = [int(re.search(r'PROD_(\d+)', i['product_id']).group(1))
                        for i in existing.get("Items", []) if re.match(r'PROD_\d+', i.get('product_id', ''))]
        next_index = max(existing_ids, default=0) + 1

        for item in meta_items:
            product = {}
            for k, v in item.items():
                if k == "product_description":
                    product["description"] = v
                elif k != "metadata_id":
                    product[k] = v
            product["product_id"] = f"PROD_{next_index:02d}"
            product["tenant_id"] = vendor_item["tenant_id"]
            product["vendor_id"] = new_vendor_id
            PRODUCT_TABLE.put_item(Item=product)
            next_index += 1

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": "Vendor created, but failed to insert products", "error": str(e)}
        }

    return {
        "statusCode": 200,
        "body": {
            "message": "Vendor inserted and metadata products added",
            "vendor_id": new_vendor_id
        }
    }
