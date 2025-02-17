import json
import os

from aws_lambda_powertools import Logger, Tracer

from shared import (
    get_user_claims,
)

logger = Logger()
tracer = Tracer()

with open('product_list.json', 'r') as product_list:
    product_list = json.load(product_list)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type,Authorization,authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    print("event", event)
    print("context", context)

    jwt_token = event["headers"].get("Authorization")

    user_info = {"username": "Unknown", "role": "Unknown"}
    if jwt_token:
        print("if jwt_token:", jwt_token)

        user_info = get_user_claims(jwt_token)

    print("User info:", user_info)

    """
    Return list of all products.
    """
    logger.debug("Fetching product list")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }
