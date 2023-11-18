import os
import cognitojwt
from aws_lambda_powertools import Logger

class NotFoundException(Exception):
    pass

logger = Logger()

def get_user_claims(jwt_token: str, source_ip: str) -> dict:
    """
    Validate JWT claims & retrieve user identifier along with additional claims
    """
    try:
        verified_claims = cognitojwt.decode(
            jwt_token, os.environ["AWS_REGION"], os.environ["USERPOOL_ID"]
        )
    except (cognitojwt.CognitoJWTException, ValueError) as e:
        logger.error(f"JWT validation error: {e}")
        return {}

    claims = {
        "username": verified_claims.get("cognito:username"),
        "role":  verified_claims.get("custom:role"),
        "yearsAsMember": verified_claims.get("custom:yearsAsMember"),
        "region": mapIPtoRegion(source_ip, verified_claims.get("cognito:username")),

    }
    logger.info(f"Claims retrieved: {claims}")

    return claims

def mapIPtoRegion(ip_address: str, username: str) -> str:
    """
    Naively maps an IP address to a country code based on the username.
    Returns 'UK' if the username is 'Toby', otherwise defaults to 'US'.
    """
    if username == "Toby":
        return "UK"
    else:
        return "US"
