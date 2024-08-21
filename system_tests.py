import os
from the_operator.client import SyncClient  # type: ignore
import uuid
import httpx
from uuid import UUID 
import json
import base64

CURRENT_ENV = os.environ.get("SYS_TEST_ENV", "PR_ENV?")

print(f"SYS TEST FOR ENV: {CURRENT_ENV}")

def get_flash_id_token(
    username: str,
    flash_auth_env: str,
    flash_auth_domain: str | None = None,
) -> str:
    """
    Function that gets a flash is token from flash-auth

    username can either be:
    - an email in the form es::<env>::email@email.com
    - the flash user uuid which MUST contain dashes
    """

    flash_auth_client = SyncClient(
        service="flash-auth", env=flash_auth_env, domain_name=flash_auth_domain
    )

    resp = flash_auth_client.get(
        f"/internal/auth-users/{username}/get-jwt-tokens", timeout=10
    )
    resp_data = resp.json()

    flash_id_token: str = resp_data["IdToken"]
    return flash_id_token

def get_flash_user_uuid_from_bearer_token(token: str) -> UUID:
    token = token.replace("Bearer ", "")

    _, payload, _ = token.split(".")

    # b64decode() requires the length of input to be a multiple of 4
    padded_payload = payload + "=" * (4 - len(payload) % 4)
    decoded_payload = base64.b64decode(padded_payload).decode("utf-8")

    payload_json = json.loads(decoded_payload)
    user_id_from_token = UUID(payload_json.get("custom:flash_user_id", ""))

    return user_id_from_token




INT_FLASH_AUTH_ENV = "int"
INT_FLASH_AUTH_DOMAIN = "https://aw7v9rwuxk.execute-api.us-east-1.amazonaws.com/v1/"

PROD_FLASH_AUTH_ENV = "prod"
PROD_FLASH_AUTH_DOMAIN = "https://qkgheyfdq7.execute-api.us-east-1.amazonaws.com/v1/"




if CURRENT_ENV == "prod":
    print("before client init")
    client = SyncClient(service="es-site", env="prod")
    property_uuid = uuid.UUID("a97248b7df384cc789b578f8729fbcde")
    resp = client.get(f"/api/marketplace-internal/property?property_uuid={property_uuid}", timeout=35)
    print("es-site resp")
    print(resp, resp.json())

    marketplace_bff_url = "https://api.marketplace.bff.energysage.com"
    mbff_client = httpx.Client(base_url=marketplace_bff_url, timeout=30)

    staff_token = get_flash_id_token(
        username="es::prod::team-sirmium+staff@energysage.com",
        flash_auth_env=PROD_FLASH_AUTH_ENV,
        flash_auth_domain=PROD_FLASH_AUTH_DOMAIN,
    )

    print(f"\nToken:\n{staff_token}")


    flash_user_id = get_flash_user_uuid_from_bearer_token(f"Bearer {staff_token}")
    print(f"\nFlash user id:\n{flash_user_id}")

    
    resp = client.get(f"/api/accounts-internal/user-profile?flash_profile_id={flash_user_id}", timeout=35)
    print(f"\nes site user info:\n{resp} {resp.json()}")



    quote_uuid = uuid.UUID("bc18e74e91ec4ad69bc8d2876990a3bd")
    resp = client.get(f"/api/marketplace-internal/user-quote-authorization?quote_uuid={quote_uuid}&flash_user_uuid={flash_user_id}", timeout=35)
    print("es-site resp permissions")
    print(resp, resp.json())


    mbff_resp = mbff_client.get(
        f"/v1/property/{property_uuid}",
        headers={"Authorization": f"Bearer {staff_token}"},
        timeout=30
    )
    print(f"\bmbff resp for property\n{mbff_resp.json()}")


    # mbff_resp = mbff_client.get(
    #     f"/v1/aggregated/{quote_uuid}",
    #     headers={"Authorization": f"Bearer {staff_token}"},
    #     timeout=30
    # )
    # print(f"\bmbff resp for aggregated\n{mbff_resp.json()}")


elif CURRENT_ENV == "int":
    print("before client init")
    client = SyncClient(service="es-site", env="int")
    property_uuid = uuid.UUID("000003b4e7e2438e98bdec98708a9658")
    resp = client.get(f"/api/marketplace-internal/property?property_uuid={property_uuid}", timeout=35)
    print("es-site resp")
    print(resp, resp.json())

    marketplace_bff_url = "https://int.api.marketplace.bff.energysage.dev"
    mbff_client = httpx.Client(base_url=marketplace_bff_url, timeout=30)

    staff_token = get_flash_id_token(
        username="es::int::team-sirmium+staff@energysage.com",
        flash_auth_env=INT_FLASH_AUTH_ENV,
        flash_auth_domain=INT_FLASH_AUTH_DOMAIN,
    )

    print(f"\nToken:\n{staff_token}")


    flash_user_id = get_flash_user_uuid_from_bearer_token(f"Bearer {staff_token}")
    print(f"\nFlash user id:\n{flash_user_id}")

    
    resp = client.get(f"/api/accounts-internal/user-profile?flash_profile_id={flash_user_id}", timeout=35)
    print(f"\nes site user info:\n{resp} {resp.json()}")



    quote_uuid = uuid.UUID("69929e01a1424e04801e5c563ff8e735")
    resp = client.get(f"/api/marketplace-internal/user-quote-authorization?quote_uuid={quote_uuid}&flash_user_uuid={flash_user_id}", timeout=35)
    print("es-site resp permissions")
    print(resp, resp.json())


    mbff_resp = mbff_client.get(
        f"/v1/property/{property_uuid}",
        headers={"Authorization": f"Bearer {staff_token}"},
        timeout=30
    )
    print(f"\bmbff resp for property\n{mbff_resp.json()}")


    mbff_resp = mbff_client.get(
        f"/v1/aggregated/{quote_uuid}",
        headers={"Authorization": f"Bearer {staff_token}"},
        timeout=30
    )
    print(f"\bmbff resp for aggregated\n{mbff_resp.json()}")
else:
    print("SIMULATING OPERATOR CLIENT IN PR ENV")
