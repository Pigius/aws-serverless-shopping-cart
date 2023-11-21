import json
import os
import boto3
from shared import get_user_claims


from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()

# Load different product lists
with open('database.json', 'r') as database:
    books = json.load(database)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type,Authorization,authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

verified_permissions_client = boto3.client('verifiedpermissions')

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp')

    jwt_token = event["headers"].get("Authorization")
    user_info = {"username": "Unknown", "role": "Unknown", "yearsAsMember": "Unknown", "region": "Unknown"}
    if jwt_token:
        user_info = get_user_claims(jwt_token, source_ip)

    logger.info(f"User info: {user_info}")
    product_list = []

    if user_info["role"] == 'Publisher' and user_info["username"] == 'Dante':
        # Handle batch authorization for publisher Dante
        product_list = handle_batch_is_authorized(user_info)
    else:
        # Construct the authz_request for other scenarios
        authz_request = construct_authz_request(user_info)
        logger.info(f"Authz request: {authz_request}")

        # Make the isAuthorized call
        response = verified_permissions_client.is_authorized(**authz_request)
        logger.info(f"Authorization response: {response}")

        # Determine which product list to return
        product_list = determine_product_list(response, user_info)

    logger.info("Returning product list")
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": product_list}),
    }


def construct_authz_request(user_info):
    entities = [
        {
            "identifier": {
                "entityType": "Bookstore::User",
                "entityId": user_info["username"]
            },
            "attributes": {},
            "parents": [
                {
                    "entityType": "Bookstore::Role",
                    "entityId": user_info["role"]
                }
            ]
        }
    ]

    resource = {
        "entityType": "Bookstore::Book",
        "entityId": "*"
    }

    # For publisher, set the resource to their specific book
    if user_info["role"] == 'Publisher':
        resource["entityId"] = "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
        entities.append(get_publisher_book_entity(user_info["username"]))

    # Determine action ID based on user role and yearsAsMember
    action_id = "View"
    if user_info["role"] == 'Customer':
        years_as_member = user_info.get("yearsAsMember", 0)
        if years_as_member != "Unknown":
            action_id = "ViewPremiumOffers"
            entities[0]["attributes"]["yearsAsMember"] = {"long": int(years_as_member)}

    # Set contextMap ip based on user name
    region = user_info.get('region', 'Unknown')
    context_map = {"region": {"string": region}}


    return {
        "policyStoreId": os.environ.get("POLICY_STORE_ID"),
        "principal": {
            "entityType": "Bookstore::User",
            "entityId": user_info["username"]
        },
        "action": {
            "actionType": "Bookstore::Action",
            "actionId": action_id
        },
        "resource": resource,
        "entities": {"entityList": entities},
        "context": {"contextMap": context_map}
    }


def get_publisher_book_entity(username):
    # This method returns the entity for the publisher's book
    return {
        "identifier": {
            "entityType": "Bookstore::Book",
            "entityId": "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
        },
        "attributes": {
            "owner": {
                "entityIdentifier": {
                    "entityType": "Bookstore::User",
                    "entityId": username
                }
            }
        },
        "parents": []
    }

def determine_product_list(response, user_info):
    if 'decision' in response:
        if response['decision'] == 'ALLOW':
            policy_description = get_policy_description(response)
            if user_info["role"] == 'Publisher' and policy_description == "Allows the publisher to see the books he has published":
                # Return books published by this publisher
                return [book for book in books['books'] if book['publisher'] == user_info['username']]
            # If allowed and not a publisher, return all books including premium offers
            return books['books']
        elif response['decision'] == 'DENY':
            # Handle the deny decision for customers
            if user_info["role"] == 'Customer':
                policy_description = get_policy_description(response)
                if policy_description == "Denies customer with specific yearsAsMember attribute to see premium offers":
                    # Return regular books for customers without premium
                    return [book for book in books['books'] if not book['premiumOffer']]
            return []  # Return an empty list for denied access
    return books['books']  # Return all books if no specific policy applies

def get_policy_description(response):
    # Extract the policy ID from the response
    logger.info(f"response info: {response}")
    policy_id = response.get('determiningPolicies', [{}])[0].get('policyId')
    if policy_id:
        policy_response = verified_permissions_client.get_policy(
            policyStoreId=os.environ.get("POLICY_STORE_ID"),
            policyId=policy_id
        )
        return policy_response.get('definition', {}).get('static', {}).get('description')
    return ""

def filter_books_based_on_policy(response, user_info, withoutPremiumOffers=False):
    policy_description = get_policy_description(response)
    if policy_description == "Allows the publisher to see the books he has published":
        return [book for book in books['books'] if book['publisher'] == user_info['username']]
    elif policy_description == "Allows normal user with specific yearsAsMember attribute to see bestsellers":
        return [book for book in books['books'] if book['premiumOffer']]
    elif policy_description == "Denies customer with specific yearsAsMember attribute to see premium offers" and withoutPremiumOffers:
        # Return regular books for customers without premium
        return [book for book in books['books'] if not book['premiumOffer']]
    elif user_info["role"] == 'Admin':
        # Assuming admin can see all books
        return books['books']
    else:
        return []

def handle_batch_is_authorized(user_info):
    # Construct two authz requests for batch processing
    authz_request_1 = construct_authz_request_for_publisher(user_info, "fn2padaa-c33l-4ea8-ll44-g7n217604p4n", "Dante")
    authz_request_2 = construct_authz_request_for_specific_book(user_info, "em1oadaa-b22k-4ea8-kk33-f6m217604o3m", "William")
    print('authz_request_1', authz_request_1)
    print('authz_request_2', authz_request_2)

    # Call batch_is_authorized with both requests
    responses = verified_permissions_client.batch_is_authorized([authz_request_1, authz_request_2])
    print('responses', responses)

    # Process responses and determine which books to return

def construct_authz_request_for_publisher(user_info, book_id, owner_name):
{
    "policyStoreId": os.environ.get("POLICY_STORE_ID"),
    "principal": {
        "entityType": "Bookstore::User",
        "entityId": user_info.get("username", "")
    },
    "action": {
        "actionType": "Bookstore::Action",
        "actionId": "View"
    },
    "resource": {
        "entityType": "Bookstore::Book",
        "entityId": book_id
    },
    "entities": {
        "entityList": [
        {
            "identifier": {
            "entityType": "Bookstore::User",
            "entityId": "Dante"
            },
            "attributes": {},
            "parents": [
            {
                "entityType": "Bookstore::Role",
                "entityId": "Publisher"
            }
            ]
        },
        {
            "identifier": {
            "entityType": "Bookstore::Book",
            "entityId": book_id
            },
            "attributes": {
            "owner": {
                "entityIdentifier": {
                "entityType": "Bookstore::User",
                "entityId": owner_name
                }
            }
            },
            "parents": []
        }
        ]
    },
    "context": {
        "contextMap": {
        "region": {
            "string": "US"
        }
        }
        }
    }