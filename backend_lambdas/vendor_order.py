# import json, os
# import boto3
# from botocore.exceptions import ClientError

# region = os.environ.get("AWS_REGION", "ca-central-1")  # fallback to default region if not set
# endpoint = f"https://data.iot.{region}.amazonaws.com"

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('orders')  # Replace with your table name

# iot_client = boto3.client('iot-data', endpoint_url=endpoint, region_name=region)

# mqtt_topic = "orders/new"

# def publish_to_iot(order_id, message):
#     try:
#         # Fetch order details from DynamoDB
#         response = table.get_item(Key={"order_id": order_id})
#         if 'Item' not in response:
#             print(f"Order ID {order_id} not found in DynamoDB.")
#             return

#         order = response['Item']
#         payload = {
#             "order_id": order_id,
#             "message": message,
#             "time": order.get("time", ""),
#             "user_name": order.get("user_name", ""),
#             "user_address": order.get("user_address", {}),
#             "products": order.get("products", {}),
#             "status": "Order Dispatched"
#         }

#         # Publish to IoT topic
#         iot_client.publish(
#             topic=mqtt_topic,
#             qos=1,
#             payload=json.dumps(payload)
#         )
#         print(f"IoT publish success: {payload}")

#     except ClientError as e:
#         print(f"DynamoDB error: {e}")
#     except Exception as e:
#         print(f"Failed to publish to IoT Core: {e}")

# def lambda_handler(event, context):
#     try:
#         # Parse the input payload
#         body = event if isinstance(event, dict) else json.loads(event)
#         ord_id = body.get('order_id')
#         status = body.get('status')

#         if not ord_id or not status:
#             return {
#                 'statusCode': 400,
#                 'body': json.dumps({'error': 'Missing ord_id or status'})
#             }
#         get_response = table.get_item(
#             Key={'order_id': ord_id}
#         )    
#         if 'Item' not in get_response:
#             return {
#                 'statusCode': 404,
#                 'body': {'error': f'Order with ord_id {ord_id} not found'}
#             }
#         # Update the item in DynamoDB
#         response = table.update_item(
#             Key={
#                 'order_id': ord_id
#             },
#             UpdateExpression='SET #s = :val1',
#             ExpressionAttributeNames={
#                 '#s': 'status'
#             },
#             ExpressionAttributeValues={
#                 ':val1': status
#             },
#             ReturnValues='UPDATED_NEW'
#         )
#         if status.lower() == "order dispatched":
#             publish_to_iot(ord_id, "Order Dispatched successfully")

#         return {
#             'statusCode': 200,
#             'body': {
#                 'message': 'Order status updated successfully'
#             }
#         }

#     except ClientError as e:
#         return {
#             'statusCode': 500,
#             'body': json.dumps({'error': str(e)})
#         }

#     except Exception as e:
#         return {
#             'statusCode': 500,
#             'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
#         }

# import json
# import os
# import boto3
# from botocore.exceptions import ClientError

# # AWS Config
# region = os.environ.get("AWS_REGION", "ca-central-1")
# endpoint = f"https://data.iot.{region}.amazonaws.com"

# # AWS Clients
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('orders')  # Replace with your table name
# iot_client = boto3.client('iot-data', endpoint_url=endpoint, region_name=region)

# mqtt_topic = "orders/new"

# # Mapping of code to full status name
# STATUS_CODE_MAP = {
#     "ORD_PLCD": "Order Placed",
#     "ORD_CFMD": "Order Confirmed",
#     "ORD_DSPS": "Order Dispatched",
#     "ORD_OFD": "Order Out For Delivery",
#     "ORD_DLVRD": "Order Delivered",
#     "ORD_CNCLD": "Order Cancelled",
#     "ORD_FAIL": "Order Failed",
#     "ORD_REFUND": "Order Refunded"
# }
# # Reverse map for returning short codes
# STATUS_NAME_TO_CODE = {v: k for k, v in STATUS_CODE_MAP.items()}

# ORDER_FLOW = [
#     "Order Placed",
#     "Order Confirmed",
#     "Order Dispatched",
#     "Order Out For Delivery",
#     "Order Delivered",
#     "Order Cancelled",
#     "Order Failed",
#     "Order Refunded"
# ]

# TERMINAL_STATES = {"Order Cancelled", "Order Failed", "Order Refunded"}

# def is_valid_status_transition(current_status, new_status):
#     if current_status == new_status:
#         return True
#     if new_status in TERMINAL_STATES:
#         return True
#     try:
#         current_index = ORDER_FLOW.index(current_status)
#         new_index = ORDER_FLOW.index(new_status)
#         return new_index == current_index + 1  # Only one step forward allowed
#     except ValueError:
#         return False

# def publish_to_iot(order_id, message):
#     try:
#         response = table.get_item(Key={"order_id": order_id})
#         if 'Item' not in response:
#             print(f"Order ID {order_id} not found in DynamoDB.")
#             return

#         order = response['Item']
#         payload = {
#             "order_id": order_id,
#             "message": message,
#             "time": order.get("time", ""),
#             "user_name": order.get("user_name", ""),
#             "user_address": order.get("user_address", {}),
#             "products": order.get("products", {}),
#             "status": "Order Dispatched"
#         }

#         iot_client.publish(
#             topic=mqtt_topic,
#             qos=1,
#             payload=json.dumps(payload)
#         )
#         print(f"IoT publish success: {payload}")

#     except ClientError as e:
#         print(f"DynamoDB error: {e}")
#     except Exception as e:
#         print(f"Failed to publish to IoT Core: {e}")

# def lambda_handler(event, context):
#     try:
#         body = event if isinstance(event, dict) else json.loads(event)
#         ord_id = body.get('order_id')
#         status_code = body.get('status')

#         if not ord_id or not status_code:
#             return {
#                 'statusCode': 400,
#                 'body': {'error': 'Missing order_id or status'}
#             }

#         new_status = STATUS_CODE_MAP.get(status_code)
#         if not new_status:
#             return {
#                 'statusCode': 400,
#                 'body': {'error': f'Unknown status code: {status_code}'}
#             }

#         get_response = table.get_item(Key={'order_id': ord_id})
#         if 'Item' not in get_response:
#             return {
#                 'statusCode': 404,
#                 'body': {'error': f'Order with ID {ord_id} not found'}
#             }

#         current_code = get_response['Item'].get('status', "")
#         current_status = STATUS_CODE_MAP.get(current_code, current_code)

#         if not is_valid_status_transition(current_status, new_status):
#             expected_status = ORDER_FLOW[ORDER_FLOW.index(current_status) + 1]
#             expected_code = STATUS_NAME_TO_CODE[expected_status]
#             return {
#                 'statusCode': 409,
#                 'body': {
#                     'error': f'Invalid status transition from "{current_code}" to "{status_code}". '
#                              f'Expected: "{expected_code}"'
#                 }
#             }

#         table.update_item(
#             Key={'order_id': ord_id},
#             UpdateExpression='SET #s = :val1',
#             ExpressionAttributeNames={'#s': 'status'},
#             ExpressionAttributeValues={':val1': status_code},
#             ReturnValues='UPDATED_NEW'
#         )

#         if status_code == "ORD_DSPS":
#             publish_to_iot(ord_id, "Order Dispatched successfully")

#         return {
#             'statusCode': 200,
#             'body': {'message': 'Order status updated successfully'}
#         }

#     except ClientError as e:
#         return {
#             'statusCode': 500,
#             'body': {'error': str(e)}
#         }
#     except Exception as e:
#         return {
#             'statusCode': 500,
#             'body': {'error': 'Internal server error', 'details': str(e)}
#         }

# import json
# import os
# import boto3
# from botocore.exceptions import ClientError

# # AWS Config
# region = os.environ.get("AWS_REGION", "ca-central-1")
# endpoint = f"https://data.iot.{region}.amazonaws.com"

# # AWS Clients
# dynamodb = boto3.resource('dynamodb')
# orders_table = dynamodb.Table('orders')
# vendors_table = dynamodb.Table('vendor')
# iot_client = boto3.client('iot-data', endpoint_url=endpoint, region_name=region)

# mqtt_topic = "orders/new"

# # Status code maps
# STATUS_CODE_MAP = {
#     "ORD_PLCD": "Order Placed",
#     "ORD_CFMD": "Order Confirmed",
#     "ORD_DSPS": "Order Dispatched",
#     "DRV_ASSND": "Driver Assigned",
#     "ORD_OFD": "Order Out For Delivery",
#     "ORD_DLVRD": "Order Delivered",
#     "ORD_CNCLD": "Order Cancelled",
#     "ORD_FAIL": "Order Failed",
#     "ORD_REFUND": "Order Refunded"
# }
# STATUS_NAME_TO_CODE = {v: k for k, v in STATUS_CODE_MAP.items()}
# # ORDER_FLOW = list(STATUS_NAME_TO_CODE.keys())
# ORDER_FLOW = list(STATUS_CODE_MAP.keys())
# TERMINAL_STATES = {"ORD_CNCLD", "ORD_FAIL", "ORD_REFUND"}

# def is_valid_status_transition(current_status, new_status):
#     if current_status == new_status or new_status in TERMINAL_STATES:
#         return True
#     try:
#         current_index = ORDER_FLOW.index(current_status)
#         new_index = ORDER_FLOW.index(new_status)
#         return new_index == current_index + 1
#     except ValueError:
#         return False

# def get_vendor_location(products):
#     if not products or not isinstance(products, list):
#         return None
#     vendor_id = products[0].get("vendor_id")
#     if not vendor_id:
#         return None
#     try:
#         vendor_resp = vendors_table.get_item(Key={"vendor_id": vendor_id})
#         vendor = vendor_resp.get("Item", {})
#         return {
#             "vendor_id": vendor_id,
#             "vendor_name": vendor.get("vendor_name", ""),
#             "latitude": vendor.get("latitude", ""),
#             "longitude": vendor.get("longitude", "")
#         }
#     except Exception:
#         return None

# def publish_to_iot(order_id, message):
#     try:
#         response = orders_table.get_item(Key={"order_id": order_id})
#         if 'Item' not in response:
#             print(f"Order ID {order_id} not found.")
#             return

#         order = response['Item']
#         products = order.get("products", [])
#         vendor_location = get_vendor_location(products)

#         payload = {
#             "order_id": order_id,
#             "message": message,
#             "time": order.get("time", ""),
#             "user_name": order.get("user_name", ""),
#             "user_address": order.get("user_address", {}),
#             "products": products,
#             "status": "Order Dispatched",
#             "vendor_location": vendor_location
#         }

#         iot_client.publish(
#             topic=mqtt_topic,
#             qos=1,
#             payload=json.dumps(payload)
#         )
#         print(f"IoT publish success: {payload}")

#     except Exception as e:
#         print(f"Failed to publish to IoT Core: {e}")

# def lambda_handler(event, context):
#     try:
#         body = event if isinstance(event, dict) else json.loads(event)
#         ord_id = body.get('order_id')
#         status_code = body.get('status')

#         if not ord_id or not status_code:
#             return {'statusCode': 400, 'body': {'error': 'Missing order_id or status'}}

#         if status_code not in STATUS_CODE_MAP:
#             return {'statusCode': 400, 'body': {'error': f'Unknown status code: {status_code}'}}

#         get_response = orders_table.get_item(Key={'order_id': ord_id})
#         if 'Item' not in get_response:
#             return {'statusCode': 404, 'body': {'error': f'Order with ID {ord_id} not found'}}

#         current_code = get_response['Item'].get('status', "")
#         if not is_valid_status_transition(current_code, status_code):
#             try:
#                 expected_status = ORDER_FLOW[ORDER_FLOW.index(current_code) + 1]
#             except:
#                 expected_status = "UNKNOWN"
#             return {
#                 'statusCode': 409,
#                 'body': {'error': f'Invalid transition from {current_code} to {status_code}. Expected: {expected_status}'}
#             }

#         # Build UpdateExpression
#         update_expr = 'SET #s = :status'
#         expr_attr_names = {'#s': 'status'}
#         expr_attr_vals = {':status': status_code}

#         if status_code == "DRV_ASSND":
#             for key in ["driver_id", "driver_name", "latitude", "longitude", "phone_number"]:
#                 if key in body:
#                     update_expr += f", {key} = :{key}"
#                     expr_attr_vals[f":{key}"] = body[key]

#         orders_table.update_item(
#             Key={'order_id': ord_id},
#             UpdateExpression=update_expr,
#             ExpressionAttributeNames=expr_attr_names,
#             ExpressionAttributeValues=expr_attr_vals
#         )

#         if status_code == "ORD_DSPS":
#             publish_to_iot(ord_id, "Order Dispatched successfully")

#         return {'statusCode': 200, 'body': {'message': 'Order status updated successfully'}}

#     except ClientError as e:
#         return {'statusCode': 500, 'body': {'error': str(e)}}
#     except Exception as e:
#         return {'statusCode': 500, 'body': {'error': 'Internal server error', 'details': str(e)}}


# import json, time
# import os
# import boto3
# from decimal import Decimal
# from botocore.exceptions import ClientError

# # AWS Config
# region = os.environ.get("AWS_REGION", "ca-central-1")
# endpoint = f"https://data.iot.{region}.amazonaws.com"

# # AWS Clients
# dynamodb = boto3.resource('dynamodb')
# orders_table = dynamodb.Table('orders')
# vendors_table = dynamodb.Table('vendor')
# iot_client = boto3.client('iot-data', endpoint_url=endpoint, region_name=region)

# mqtt_topic = "orders/new"

# # Decimal to JSON encoder
# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj) if obj % 1 else int(obj)
#         return super(DecimalEncoder, self).default(obj)

# # Status code maps
# STATUS_CODE_MAP = {
#     "ORD_PLCD": "Order Placed",
#     "ORD_CFMD": "Order Confirmed",
#     "ORD_DSPS": "Order Dispatched",
#     "DRV_ASSND": "Driver Assigned",
#     "ORD_OFD": "Order Out For Delivery",
#     "ORD_DLVRD": "Order Delivered",
#     "ORD_CNCLD": "Order Cancelled",
#     "ORD_FAIL": "Order Failed",
#     "ORD_REFUND": "Order Refunded"
# }
# STATUS_NAME_TO_CODE = {v: k for k, v in STATUS_CODE_MAP.items()}
# ORDER_FLOW = list(STATUS_CODE_MAP.keys())
# TERMINAL_STATES = {"ORD_CNCLD", "ORD_FAIL", "ORD_REFUND"}

# def is_valid_status_transition(current_status, new_status):
#     if current_status == new_status or new_status in TERMINAL_STATES:
#         return True
#     try:
#         current_index = ORDER_FLOW.index(current_status)
#         new_index = ORDER_FLOW.index(new_status)
#         return new_index == current_index + 1
#     except ValueError:
#         return False

# # def get_vendor_location(products):
# #     if not isinstance(products, dict):
# #         return None
# #     for product in products.values():
# #         vendor_id = product.get("vendor_id")
# #         print("C", vendor_id)
# #         if vendor_id:
# #             try:
# #                 vendor_resp = vendors_table.get_item(Key={"vendor_id": vendor_id})
# #                 vendor = vendor_resp.get("Item", {})
# #                 return {
# #                     "vendor_id": vendor_id,
# #                     "vendor_name": vendor.get("vendor_name", ""),
# #                     "latitude": vendor.get("vendor_location", {}).get("latitude", ""),
# #                     "longitude": vendor.get("vendor_location", {}).get("longitude", ""),
# #                     "vendor_address": vendor.get("vendor_location", {}).get("vendor_address", ""),
# #                     "address_name": vendor.get("vendor_location", {}).get("address_name", "")
# #                 }
# #             except Exception:
# #                 return None
# #     return None

# def get_vendor_location(products):
#     if isinstance(products, dict):
#         product_iter = products.values()
#     elif isinstance(products, list):
#         product_iter = [p.get("M", p) for p in products]
#     else:
#         return None

#     for product in product_iter:
#         if not isinstance(product, dict):
#             continue

#         # Flatten DynamoDB style (e.g., {"S": "value"})
#         flat_product = {}
#         for k, v in product.items():
#             if isinstance(v, dict) and len(v) == 1:
#                 flat_product[k] = list(v.values())[0]
#             else:
#                 flat_product[k] = v

#         vendor_id = flat_product.get("vendor_id")
#         if vendor_id:
#             try:
#                 vendor_resp = vendors_table.get_item(Key={"vendor_id": vendor_id})
#                 vendor = vendor_resp.get("Item", {})
#                 return {
#                     "vendor_id": vendor_id,
#                     "vendor_name": vendor.get("vendor_name", ""),
#                     "latitude": vendor.get("vendor_location", {}).get("latitude", ""),
#                     "longitude": vendor.get("vendor_location", {}).get("longitude", ""),
#                     "vendor_address": vendor.get("vendor_location", {}).get("vendor_address", ""),
#                     "address_name": vendor.get("vendor_location", {}).get("address_name", "")
#                 }
#             except Exception as e:
#                 print(f"Error fetching vendor: {e}")
#                 return None
#     return None

# def publish_to_iot(order_id, message):
#     try:
#         response = orders_table.get_item(Key={"order_id": order_id})
#         if 'Item' not in response:
#             print(f"Order ID {order_id} not found.")
#             return

#         order = response['Item']
#         products = order.get("products", {})
#         vendor_location = get_vendor_location(products)
#         print("A", vendor_location)
#         print("B", products)

#         payload = {
#             "order_id": order_id,
#             "message": message,
#             "time": order.get("time", ""),
#             "user_name": order.get("user_name", ""),
#             "user_address": order.get("user_address", {}),
#             "products": products,
#             "status": "Order Dispatched",
#             "vendor_details": vendor_location
#         }

#         iot_client.publish(
#             topic=mqtt_topic,
#             qos=1,
#             payload=json.dumps(payload, cls=DecimalEncoder)
#         )
#         print(f"IoT publish success: {payload}")

#     except Exception as e:
#         print(f"Failed to publish to IoT Core: {e}")

# def lambda_handler(event, context):
#     try:
#         body = event if isinstance(event, dict) else json.loads(event)
#         ord_id = body.get('order_id')
#         status_code = body.get('status')

#         if not ord_id or not status_code:
#             return {'statusCode': 400, 'body': json.dumps({'error': 'Missing order_id or status'})}

#         if status_code not in STATUS_CODE_MAP:
#             return {'statusCode': 400, 'body': json.dumps({'error': f'Unknown status code: {status_code}'})}

#         get_response = orders_table.get_item(Key={'order_id': ord_id})
#         if 'Item' not in get_response:
#             return {'statusCode': 404, 'body': json.dumps({'error': f'Order with ID {ord_id} not found'})}

#         current_code = get_response['Item'].get('status', "")
#         if not is_valid_status_transition(current_code, status_code):
#             try:
#                 expected_status = ORDER_FLOW[ORDER_FLOW.index(current_code) + 1]
#             except:
#                 expected_status = "UNKNOWN"
#             return {
#                 'statusCode': 409,
#                 'body': json.dumps({'error': f'Invalid transition from {current_code} to {status_code}. Expected: {expected_status}'})
#             }

#         update_expr = 'SET #s = :status'
#         expr_attr_names = {'#s': 'status'}
#         expr_attr_vals = {':status': status_code}

#         if status_code == "DRV_ASSND":
#             for key in ["driver_id", "driver_name", "latitude", "longitude", "phone_number"]:
#                 if key in body:
#                     update_expr += f", {key} = :{key}"
#                     expr_attr_vals[f":{key}"] = body[key]

#         orders_table.update_item(
#             Key={'order_id': ord_id},
#             UpdateExpression=update_expr,
#             ExpressionAttributeNames=expr_attr_names,
#             ExpressionAttributeValues=expr_attr_vals
#         )

#         if status_code == "ORD_DSPS":
#             publish_to_iot(ord_id, "Order Dispatched successfully")

#         return {'statusCode': 200, 'body': {'message': 'Order status updated successfully'}}

#     except ClientError as e:
#         return {'statusCode': 500, 'body': {'error': str(e)}}
#     except Exception as e:
#         return {'statusCode': 500, 'body': {'error': 'Internal server error', 'details': str(e)}}

# ==================================================================================================================================

import json, time, os, boto3, math
from decimal import Decimal
from botocore.exceptions import ClientError

# AWS Config
region = os.environ.get("AWS_REGION", "ca-central-1")
endpoint = f"https://data.iot.{region}.amazonaws.com"

# AWS Clients
dynamodb = boto3.resource('dynamodb', region_name=region)
orders_table = dynamodb.Table('orders')
vendors_table = dynamodb.Table('vendor')
driver_table = dynamodb.Table('driver_info')
iot_client = boto3.client('iot-data', endpoint_url=endpoint, region_name=region)

mqtt_topic = "orders/new"

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

# Decimal encoder
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 else int(obj)
        return super().default(obj)

# Status maps
STATUS_CODE_MAP = {
    "ORD_PLCD": "Order Placed",
    "ORD_CFMD": "Order Confirmed",
    "ORD_DSPS": "Order Dispatched",
    "DRV_ASSND": "Driver Assigned",
    "ORD_OFD": "Order Out For Delivery",
    "ORD_DLVRD": "Order Delivered",
    "ORD_CNCLD": "Order Cancelled",
    "ORD_FAIL": "Order Failed",
    "ORD_REFUND": "Order Refunded"
}
ORDER_FLOW = list(STATUS_CODE_MAP.keys())
TERMINAL_STATES = {"ORD_CNCLD", "ORD_FAIL", "ORD_REFUND"}

def is_valid_status_transition(current_status, new_status):
    if current_status == new_status or new_status in TERMINAL_STATES:
        return True
    try:
        current_index = ORDER_FLOW.index(current_status)
        new_index = ORDER_FLOW.index(new_status)
        return new_index == current_index + 1
    except ValueError:
        return False

def get_vendor_location(products):
    if isinstance(products, dict):
        product_iter = products.values()
    elif isinstance(products, list):
        product_iter = [p.get("M", p) for p in products]
    else:
        return None

    for product in product_iter:
        if not isinstance(product, dict):
            continue
        flat_product = {k: list(v.values())[0] if isinstance(v, dict) and len(v) == 1 else v for k, v in product.items()}
        vendor_id = flat_product.get("vendor_id")
        if vendor_id:
            try:
                vendor_resp = vendors_table.get_item(Key={"vendor_id": vendor_id})
                vendor = vendor_resp.get("Item", {})
                return {
                    "vendor_id": vendor_id,
                    "vendor_name": vendor.get("vendor_name", ""),
                    "latitude": vendor.get("vendor_location", {}).get("latitude", ""),
                    "longitude": vendor.get("vendor_location", {}).get("longitude", ""),
                    "vendor_address": vendor.get("vendor_location", {}).get("vendor_address", ""),
                    "address_name": vendor.get("vendor_location", {}).get("address_name", "")
                }
            except:
                return None
    return None

def publish_until_drv_assigned(order_id, message):
    while True:
        response = orders_table.get_item(Key={"order_id": order_id})
        order = response.get("Item", {})
        status = order.get("status", "")

        if status == "DRV_ASSND":
            print("✅ Status updated to DRV_ASSND, stopping MQTT publish loop.")
            break

        products = order.get("products", {})
        vendor_location = get_vendor_location(products)

        payload = {
            "order_id": order_id,
            "message": message,
            "time": order.get("time", ""),
            "user_name": order.get("user_name", ""),
            "user_address": order.get("user_address", {}),
            "products": products,
            "status": "Order Dispatched",
            "vendor_details": vendor_location
        }
        vendor_lat = float(vendor_location["latitude"])
        vendor_lon = float(vendor_location["longitude"])

        response = driver_table.scan()
        items = response['Items']

        # Filter drivers within 3 km
        nearby_drivers = []
        driver_dict = {}
        for item in items:
            lat = float(item['location']['latitude'])
            lon = float(item['location']['longitude'])
            distance = haversine_distance(vendor_lat, vendor_lon, lat, lon)
            if distance <= 3 and item.get('available', True):  # Check if driver is available
                nearby_drivers.append(item['captain_id'])
                driver_dict[item['captain_id']] = distance

        print("Captain IDs within 3 km:", nearby_drivers)
        print("Captain dict within 3 km:", driver_dict)

        for captain_id in nearby_drivers:
        # mqtt_topic = mqtt_topic_template.format(captain_id)
            try:
                iot_client.publish(
                    topic=f"orders/new/{captain_id}",
                    qos=1,
                    payload=json.dumps(payload, cls=DecimalEncoder)
                )
                print(f"📡 Published to {mqtt_topic}: {payload}")
            except ClientError as e:
                print(f"❌ Failed to publish to {mqtt_topic}: {str(e)}")

        # try:
        #     iot_client.publish(
        #         topic=mqtt_topic,
        #         qos=1,
        #         payload=json.dumps(payload, cls=DecimalEncoder)
        #     )
        #     print(f"📡 Published to MQTT: {payload}")
        # except ClientError as e:
        #     print(f"❌ MQTT publish failed: {str(e)}")

        time.sleep(1)  # Publish every 1 second

def lambda_handler(event, context):
    try:
        body = event if isinstance(event, dict) else json.loads(event)
        order_id = body.get('order_id')
        status_code = body.get('status')

        if not order_id or not status_code:
            return {'statusCode': 400, 'body': {'error': 'Missing order_id or status'}}

        if status_code not in STATUS_CODE_MAP:
            return {'statusCode': 400, 'body': {'error': f'Unknown status code: {status_code}'}}

        # Fetch current order
        current_order = orders_table.get_item(Key={"order_id": order_id}).get("Item")
        if not current_order:
            return {'statusCode': 404, 'body': {'error': f'Order {order_id} not found'}}

        current_status = current_order.get("status", "")
        if not is_valid_status_transition(current_status, status_code):
            try:
                expected = ORDER_FLOW[ORDER_FLOW.index(current_status) + 1]
            except:
                expected = "UNKNOWN"
            return {
                'statusCode': 409,
                'body': {'error': f'Invalid transition from {current_status} to {status_code}. Expected: {expected}'}
            }

        # Update order status
        update_expr = "SET #s = :status"
        expr_names = {"#s": "status"}
        expr_vals = {":status": status_code}

        if status_code == "DRV_ASSND":
            for key in ["driver_id", "driver_name", "latitude", "longitude", "phone_number"]:
                if key in body:
                    update_expr += f", {key} = :{key}"
                    expr_vals[f":{key}"] = body[key]

        orders_table.update_item(
            Key={"order_id": order_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals
        )

        # Start publish loop if status is ORD_DSPS
        if status_code == "ORD_DSPS":
            # Start MQTT publish loop until status becomes DRV_ASSND
            publish_until_drv_assigned(order_id, "Order Dispatched successfully")

        return {'statusCode': 200, 'body': {'message': 'Order status updated successfully'}}

    except ClientError as e:
        return {'statusCode': 500, 'body': {'error': str(e)}}
    except Exception as e:
        return {'statusCode': 500, 'body': {'error': str(e)}}