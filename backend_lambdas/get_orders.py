# import json
# import boto3

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('orders')

# def lambda_handler(event, context):
#     tenant_id = event.get("tenant_id", "").strip()
#     vendor_id = event.get("vendor_id", "").strip()

#     if not tenant_id and not vendor_id:
#         return {
#             "statusCode": 400,
#             "body": {"error": "Missing tenant_id and vendor_id"}
#         }

#     try:
#         response = table.scan()
#         items = response.get("Items", [])
#         result = []

#         for item in items:
#             order_id = item.get("order_id")
#             products = item.get("products", {})
#             matched_products = {}

#             if isinstance(products, dict):
#                 product_iterable = products.items()
#             elif isinstance(products, list):
#                 # Handle list of product dicts with assumed product_id field
#                 product_iterable = [(p.get("product_id", f"prod_{i}"), p) for i, p in enumerate(products) if isinstance(p, dict)]
#             else:
#                 product_iterable = []

#             for product_key, product_value in product_iterable:
#                 db_tenant = str(product_value.get("tenant_id", "")).strip()
#                 db_vendor = str(product_value.get("vendor_id", "")).strip()

#                 if db_tenant == tenant_id or db_vendor == vendor_id:
#                     matched_products[product_key] = product_value

#             if matched_products:
#                 sorted_products = dict(sorted(matched_products.items(), key=lambda x: x[0]))
#                 result.append({
#                     "order_id": order_id,
#                     "user_name": item.get("user_name"),
#                     "user_address": item.get("user_address"),
#                     "status": item.get("status"),
#                     "time": item.get("time"),
#                     "products": sorted_products
#                 })
#         sorted_result = sorted(result, key=lambda x: int(x["order_id"].split("_")[1]), reverse=True)
#         return {
#             "statusCode": 200,
#             "body": sorted_result
#         }

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": {"error": f"Internal server error: {str(e)}"}
#         }

import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders')
vendor_table = dynamodb.Table('vendor')

def lambda_handler(event, context):
    tenant_id = event.get("tenant_id", "").strip()
    vendor_id = event.get("vendor_id", "").strip()

    if not tenant_id and not vendor_id:
        return {
            "statusCode": 400,
            "body": {"error": "Missing tenant_id and vendor_id"}
        }

    try:
        vendor_name = ""
        if vendor_id:
            vendor_response = vendor_table.get_item(Key={"vendor_id": vendor_id})
            vendor_item = vendor_response.get("Item")
            # print("vendor_item", vendor_item)
            if not vendor_item:
                return {
                    "statusCode": 404,
                    "body": f"Vendor ID {vendor_id} not found."
                }
            vendor_name = vendor_item.get("vendor_name", "")

        response = table.scan()
        items = response.get("Items", [])
        result = []

        for item in items:
            order_id = item.get("order_id")
            products = item.get("products", {})
            matched_products = {}

            if isinstance(products, dict):
                product_iterable = products.items()
            elif isinstance(products, list):
                product_iterable = [(p.get("product_id", f"prod_{i}"), p) for i, p in enumerate(products) if isinstance(p, dict)]
            else:
                product_iterable = []

            for product_key, product_value in product_iterable:
                db_tenant = str(product_value.get("tenant_id", "")).strip()
                db_vendor = str(product_value.get("vendor_id", "")).strip()

                if (tenant_id and db_tenant == tenant_id) or (vendor_id and db_vendor == vendor_id):
                    matched_products[product_key] = product_value

            if matched_products:
                sorted_products = dict(sorted(matched_products.items(), key=lambda x: x[0]))
                result.append({
                    "order_id": order_id,
                    "user_name": item.get("user_name"),
                    "user_address": item.get("user_address"),
                    "status": item.get("status"),
                    "time": item.get("time"),
                    "products": sorted_products
                })

        sorted_result = sorted(result, key=lambda x: int(x["order_id"].split("_")[1]), reverse=True)
        return {
            "statusCode": 200,
            "body": {"vendor_name": vendor_name, "orders": sorted_result}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": f"Internal server error: {str(e)}"}
        }