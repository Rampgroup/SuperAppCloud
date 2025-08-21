



# import json
# import boto3
# from decimal import Decimal
# from datetime import datetime

# dynamodb = boto3.resource("dynamodb", region_name="ca-central-1")  # replace with your region
# products_table = dynamodb.Table("products")
# orders_table = dynamodb.Table("orders")  # ensure this table exists

# def generate_order_id():
#     timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
#     return f"ORD_{timestamp}"

# def lambda_handler(event, context):
#     products = event.get("products", [])
#     user_name = event.get("user_name")
#     user_address = event.get("user_address")

#     if not products or not user_name or not user_address:
#         return {
#             "statusCode": 400,
#             "body": json.dumps("Missing user_name, user_address, or products")
#         }

#     valid_products = []

#     for product in products:
#         product_id = product.get("product_id")
#         product_name = product.get("product_name")
#         requested_qty = int(product.get("qty", 0))

#         # Step 1: Fetch product from DynamoDB
#         try:
#             response = products_table.get_item(Key={"product_id": product_id})
#             db_product = response.get("Item")
#         except Exception as e:
#             return {
#                 "statusCode": 500,
#                 "body": f"Error fetching product {product_id}: {str(e)}"
#             }

#         # Step 2: Validate existence
#         if not db_product:
#             return {
#                 "statusCode": 404,
#                 "body": f"Product ID '{product_id}' not found"
#             }

#         # Step 3: Validate name match
#         if db_product.get("product_name") != product_name:
#             return {
#                 "statusCode": 400,
#                 "body": f"Product name mismatch for ID '{product_id}'. Expected '{db_product.get('product_name')}', got '{product_name}'"
#             }

#         # Step 4: Validate quantity
#         available_qty = int(db_product.get("qty", 0))
#         if requested_qty > available_qty:
#             return {
#                 "statusCode": 400,
#                 "body": f"Out of stock: '{product_id}' only has {available_qty} available"
#             }

#         valid_products.append({
#             "product_id": product_id,
#             "product_name": product_name,
#             "requested_qty": requested_qty,
#             "remaining_qty": available_qty - requested_qty,
#             "price": db_product.get("price", "0"),
#             "vendor_id": db_product.get("vendor_id", ""),
#             "tenant_id": db_product.get("tenant_id", ""),
#             "unit_type": db_product.get("unit_type", ""),
#             "image": db_product.get("image", ""),
#             "category": db_product.get("category", ""),
#             "subcategory": db_product.get("subcategory", ""),
#             "sku": db_product.get("sku", "")
#         })

#     # All products validated, now update qty in products table
#     for p in valid_products:
#         products_table.update_item(
#             Key={"product_id": p["product_id"]},
#             UpdateExpression="SET qty = :q",
#             ExpressionAttributeValues={":q": Decimal(str(p["remaining_qty"]))}
#         )

#     # Generate and save order
#     order_id = generate_order_id()
#     total_price = sum(int(p["price"]) * p["requested_qty"] for p in valid_products)

#     order_item = {
#         "order_id": order_id,
#         "user_name": user_name,
#         "user_address": user_address,
#         "products": valid_products,
#         "total_price": total_price
#     }

#     orders_table.put_item(Item=json.loads(json.dumps(order_item), parse_float=Decimal))

#     return {
#         "statusCode": 200,
#         "body": json.dumps({
#             "message": "Order placed successfully.",
#             "order_id": order_id,
#             "total_price": total_price,
#             "products_updated": [
#                 {
#                     "product_id": p["product_id"],
#                     "new_qty": p["remaining_qty"]
#                 } for p in valid_products
#             ]
#         })
#     }









# import json
# import boto3
# from decimal import Decimal
# import re
# from datetime import datetime, timedelta

# def get_ist_time_formatted():
#     ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
#     return ist_now.strftime("%d-%m-%Y, %I:%M %p")
# dynamodb = boto3.resource("dynamodb", region_name="ca-central-1")  # Replace with your region
# products_table = dynamodb.Table("products")
# orders_table = dynamodb.Table("orders")

# def generate_next_order_id():
#     # Scan existing order_ids and get max
#     response = orders_table.scan(ProjectionExpression="order_id")
#     order_ids = [item["order_id"] for item in response.get("Items", []) if "order_id" in item]

#     max_number = 0
#     for oid in order_ids:
#         match = re.match(r"ORD_(\d+)", oid)
#         if match:
#             num = int(match.group(1))
#             max_number = max(max_number, num)

#     next_number = max_number + 1
#     return f"ORD_{next_number:02d}"

# def lambda_handler(event, context):
#     # products = event.get("products", [])
#     products = event.get("products")
#     user_name = event.get("user_name")
#     user_address = event.get("user_address")

#     if not products or not user_name or not user_address:
#         return {
#             "statusCode": 400,
#             "body": "Missing user_name, user_address, or products"
#         }

#     valid_products = []

#     for product in products:
#         product_id = product.get("product_id")
#         product_name = product.get("product_name")
#         requested_qty = int(product.get("qty", 0))

#         try:
#             response = products_table.get_item(Key={"product_id": product_id})
#             db_product = response.get("Item")
#         except Exception as e:
#             return {
#                 "statusCode": 500,
#                 "body": f"Error fetching product {product_id}: {str(e)}"
#             }

#         if not db_product:
#             return {
#                 "statusCode": 404,
#                 "body": f"Product ID '{product_id}' not found"
#             }

#         if db_product.get("product_name") != product_name:
#             return {
#                 "statusCode": 400,
#                 "body": f"Product name mismatch for ID '{product_id}'. Expected '{db_product.get('product_name')}', got '{product_name}'"
#             }

#         available_qty = int(db_product.get("qty", 0))
#         if requested_qty > available_qty:
#             return {
#                 "statusCode": 400,
#                 "body": f"Out of stock: '{product_id}' only has {available_qty} available"
#             }

#         valid_products.append({
#             **product,
#             "price": db_product.get("price", "0"),
#             "vendor_id": db_product.get("vendor_id", ""),
#             "tenant_id": db_product.get("tenant_id", ""),
#             "unit_type": db_product.get("unit_type", ""),
#             "image": db_product.get("image", ""),
#             "category": db_product.get("category", ""),
#             "subcategory": db_product.get("subcategory", ""),
#             "sku": db_product.get("sku", ""),
#             "subcategory_image": db_product.get("subcategory_image", ""),
#             "description": db_product.get("description", ""),
#             "domain": db_product.get("domain", ""),
#             "product_id": db_product.get("product_id", ""),
#             "product_name": db_product.get("product_name", ""),
#             "qty": db_product.get("qty", ""),
#             "remaining_qty": available_qty - requested_qty
#         })

#     # Update product quantities
#     for item in valid_products:
#         products_table.update_item(
#             Key={"product_id": item["product_id"]},
#             UpdateExpression="SET qty = :new_qty",
#             ExpressionAttributeValues={":new_qty": Decimal(str(item["remaining_qty"]))}
#         )

#     # Generate next order ID
#     order_id = generate_next_order_id()

#     # Calculate total price
#     total_price = sum(int(p["price"]) * int(p["qty"]) for p in valid_products)

#     # Prepare order item
#     order_item = {
#         "order_id": order_id,
#         "user_name": user_name,
#         "time": get_ist_time_formatted(),
#         "user_address": user_address,
#         "products": valid_products,
#         "status":"ORD_PLCD"
#     }

#     # Save to orders table
#     # orders_table.put_item(Item=json.loads(json.dumps(order_item), parse_float=Decimal))

#     # return {
#     #     "statusCode": 200,
#     #     "body": {
#     #         "message": "Order placed successfully",
#     #         "order_id": order_id
#     #     }
#     # }
#     # Save to orders table
#     orders_table.put_item(Item=order_item)

#     return {
#     "statusCode": 200,
#     "body": {
#         "message": "Order placed successfully",
#         "order_id": order_id
#     }
# }


















import json
import boto3
from decimal import Decimal
import re
from datetime import datetime, timedelta

def get_ist_time_formatted():
    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist_now.strftime("%d-%m-%Y, %I:%M %p")
dynamodb = boto3.resource("dynamodb", region_name="ca-central-1")
products_table = dynamodb.Table("products")
orders_table = dynamodb.Table("orders")

def generate_next_order_id():
    response = orders_table.scan(ProjectionExpression="order_id")
    order_ids = [item["order_id"] for item in response.get("Items", []) if "order_id" in item]
    max_number = 0
    for oid in order_ids:
        match = re.match(r"ORD_(\d+)", oid)
        if match:
            num = int(match.group(1))
            max_number = max(max_number, num)
    next_number = max_number + 1
    return f"ORD_{next_number:02d}"

def lambda_handler(event, context):
    products = event.get("products")
    user_name = event.get("user_name")
    user_address = event.get("user_address")

    if not products or not user_name or not user_address:
        return {
            "statusCode": 400,
            "body": "Missing user_name, user_address, or products"
        }

    valid_products = []

    for product in products:
        product_id = product.get("product_id")
        product_name = product.get("product_name")
        requested_qty = int(product.get("qty", 0))

        try:
            response = products_table.get_item(Key={"product_id": product_id})
            db_product = response.get("Item")
        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"Error fetching product {product_id}: {str(e)}"
            }

        if not db_product:
            return {
                "statusCode": 404,
                "body": f"Product ID '{product_id}' not found"
            }

        if db_product.get("product_name") != product_name:
            return {
                "statusCode": 400,
                "body": f"Product name mismatch for ID '{product_id}'. Expected '{db_product.get('product_name')}', got '{product_name}'"
            }

        available_qty = int(db_product.get("qty", 0))

        # ✅ Check out of stock
        if requested_qty > available_qty:
            return {
                "statusCode": 400,
                "body": f"Out of stock: '{product_id}' only has {available_qty} available"
            }

        # ✅ Calculate remaining qty
        remaining_qty = available_qty - requested_qty

        # ✅ Prepare product object for orders table
        valid_products.append({
            "product_id": db_product.get("product_id", ""),
            "product_name": db_product.get("product_name", ""),
            "qty": requested_qty,  # ✅ store payload qty in orders table
            "price": db_product.get("price", "0"),
            "vendor_id": db_product.get("vendor_id", ""),
            "tenant_id": db_product.get("tenant_id", ""),
            "unit_type": db_product.get("unit_type", ""),
            "image": db_product.get("image", ""),
            "category": db_product.get("category", ""),
            "subcategory": db_product.get("subcategory", ""),
            "sku": db_product.get("sku", ""),
            "subcategory_image": db_product.get("subcategory_image", ""),
            "description": db_product.get("description", ""),
            "domain": db_product.get("domain", ""),
            "remaining_qty": remaining_qty  # ✅ included for reference
        })

        # ✅ Update products table: ONLY update 'qty' field
        products_table.update_item(
            Key={"product_id": product_id},
            UpdateExpression="SET qty = :new_qty",
            ExpressionAttributeValues={
                ":new_qty": Decimal(str(remaining_qty))
            }
        )

    # Generate next order ID
    order_id = generate_next_order_id()

    # Calculate total price based on payload qty
    total_price = sum(int(p["price"]) * int(p["qty"]) for p in valid_products)

    # Prepare order item
    order_item = {
        "order_id": order_id,
        "user_name": user_name,
        "time": get_ist_time_formatted(),
        "user_address": user_address,
        "products": valid_products,  # ✅ with payload qty
        "total_price": total_price,
        "status": "ORD_PLCD"
    }

    # Save to orders table
    orders_table.put_item(Item=order_item)

    return {
        "statusCode": 200,
        "body": {
            "message": "Order placed successfully",
            "order_id": order_id,
            "total_price": total_price,
            "products_ordered": valid_products
        }
    }
