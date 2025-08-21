# import json
# import boto3
# import base64
# import re
# from datetime import datetime, timedelta
# from boto3.dynamodb.conditions import Key

# # AWS setup
# s3 = boto3.client('s3')
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('products')
# BUCKET_NAME = 'cms-image-data'

# # Image format signatures
# IMAGE_SIGNATURES = {
#     'jpeg': [b'\xff\xd8'], 'jpg': [b'\xff\xd8'],
#     'png': [b'\x89PNG\r\n\x1a\n'],
#     'gif': [b'GIF87a', b'GIF89a'],
#     'bmp': [b'BM'],
#     'webp': [b'RIFF'],
#     'tiff': [b'II*\x00', b'MM\x00*'],
#     'svg': [b'<?xml', b'<svg']
# }

# CONTENT_TYPE_MAP = {
#     'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
#     'png': 'image/png', 'gif': 'image/gif',
#     'bmp': 'image/bmp', 'webp': 'image/webp',
#     'tiff': 'image/tiff', 'svg': 'image/svg+xml'
# }

# def is_valid_image(ext, data):
#     ext = ext.lower()
#     if ext not in IMAGE_SIGNATURES:
#         return False
#     for sig in IMAGE_SIGNATURES[ext]:
#         if data.startswith(sig):
#             return True
#     return False

# def lambda_handler(event, context):
#     try:
#         # Validate required fields
#         required_fields = ['domain_type', 'product_name', 'price', 'qty', 'tenant_id', 'vendor_id', 'image']
#         for field in required_fields:
#             if field not in event:
#                 return {
#                     'statusCode': 400,
#                     'body': {'message': f"Missing required field: {field}"}
#                 }

#         domain_type = str(event['domain_type'])
#         name = str(event['product_name'])
#         price = str(event['price'])
#         qty = str(event['qty'])
#         tenant_id = str(event['tenant_id'])
#         vendor_id = str(event['vendor_id'])
#         category=str(event['category'])
#         subcategory=str(event['subcategory'])
#         sku=str(event['sku'])
#         unit_type=str(event['unit_type'])

#         # image_info = event['image']
#         # doc_name = image_info.get('doc_name')
#         # doc_body = image_info.get('doc_body')

#         # if not doc_name or not doc_body:
#         #     return {
#         #         'statusCode': 200,
#         #         'body': {'message': "Image 'doc_name' and 'doc_body' are required."}
#         #     }

#         # ✅ Check if product name already exists (Partition Key check)
#         response = table.query(
#             KeyConditionExpression=Key('name').eq(name)
#         )
#         if response['Count'] > 0:
#             return {
#                 'statusCode': 200,
#                 'body': {'message': f"Product with name '{name}' already exists."}
#             }

#         # Decode base64 image
#         ext = doc_name.lower().split('.')[-1]
#         if doc_body.startswith("data:"):
#             doc_body = doc_body.split(",", 1)[1]
#         try:
#             image_bytes = base64.b64decode(doc_body)
#         except Exception:
#             return {
#                 'statusCode': 200,
#                 'body': {'message': "Image body is not a valid base64 string."}
#             }

#         # Validate image type
#         if not is_valid_image(ext, image_bytes):
#             return {
#                 'statusCode': 200,
#                 'body': {'message': f"File '.{ext}' is not a valid image format."}
#             }

#         # Upload to S3
#         content_type = CONTENT_TYPE_MAP.get(ext, 'application/octet-stream')
#         s3_key = f"uploads/{doc_name}"
#         s3.put_object(
#             Bucket=BUCKET_NAME,
#             Key=s3_key,
#             Body=image_bytes,
#             ContentType=content_type
#         )
#         image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

#         # Auto-increment product_id
#         scan_response = table.scan(ProjectionExpression='product_id')
#         items = scan_response.get('Items', [])
#         max_id = 0
#         for item in items:
#             pid = item.get('product_id', '')
#             match = re.search(r'PROD_(\d+)', pid)
#             if match:
#                 max_id = max(max_id, int(match.group(1)))
#         product_id = f"PROD_{max_id + 1:02}"

#         # Final check for product_id (very unlikely to conflict, just in case)
#         for item in items:
#             if item.get('product_id') == product_id:
#                 return {
#                     'statusCode': 200,
#                     'body': {'message': f"Product ID '{product_id}' already exists. Please try again."}
#                 }

#         # IST time
#         ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
#         created_time = ist_time.strftime("%d-%m-%Y,%-I:%M %p")

#         # Build and insert item
#         item = {
#             'name': name,
#             'product_id': product_id,
#             # 'image': image_url,
#             "image": str(event['image']),
#             'price': price,
#             'quantity': qty,
#             'tenant_id': tenant_id,
#             'vendor_id': vendor_id,
#             'created_time': created_time,
#             'domain': domain_type.capitalize(),
#             'category':category.capitalize(),
#             'subcategory':subcategory.capitalize(),
#             'sku':sku,
#             'unit_type':unit_type

            
#         }

#         table.put_item(Item=item)

#         return {
#             'statusCode': 200,
#             'body': {
#                 'message': 'Product stored successfully',
#                 'product_id': product_id,
#                 # 'image_url': image_url
#                 'image_url': str(event['image'])
#             }
#         }

#     except Exception as e:
#         return {
#             'statusCode': 500,
#             'body': {'error': str(e)}
#         }


import json
import boto3
import re
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr

# AWS setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('products')

def lambda_handler(event, context):
    try:
        # Validate required fields
        required_fields = [
            'domain_type', 'product_name', 'price', 'qty',
            'tenant_id', 'vendor_id', 'image',
            'category', 'subcategory', 'sku', 'unit_type'
        ]
        for field in required_fields:
            if field not in event:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'message': f"Missing required field: {field}"})
                }

        name = str(event['product_name'])

        # Check if product already exists using scan
        existing = table.scan(
            FilterExpression=Attr('name').eq(name)
        )
        if existing['Count'] > 0:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f"Product with name '{name}' already exists."})
            }

        image_url = event['image']  # Accept as plain URL string

        # Auto-increment product_id
        scan_response = table.scan(ProjectionExpression='product_id')
        items = scan_response.get('Items', [])
        max_id = 0
        for item in items:
            pid = item.get('product_id', '')
            match = re.search(r'PROD_(\d+)', pid)
            if match:
                max_id = max(max_id, int(match.group(1)))
        product_id = f"PROD_{max_id + 1:02}"

        # IST time
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        created_time = ist_time.strftime("%d-%m-%Y,%-I:%M %p")

        # Insert item into DynamoDB
        item = {
            'product_id': product_id,
            'product_name': name,
            'price': str(event['price']),
            'qty': str(event['qty']),
            'tenant_id': str(event['tenant_id']),
            'vendor_id': str(event['vendor_id']),
            'created_time': created_time,
            'description': str(event['description']),
            'domain': str(event['domain_type']).capitalize(),
            'category': str(event['category']).capitalize(),
            'subcategory': str(event['subcategory']).capitalize(),
            'sku': str(event['sku']),
            'unit_type': str(event['unit_type']),
            'image': image_url
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': {
                'message': 'Product stored successfully',
                'product_id': product_id,
                'image_url': image_url
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
