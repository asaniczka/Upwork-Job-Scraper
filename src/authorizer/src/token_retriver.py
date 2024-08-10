"""Handles retrival of an Auth Token"""

import os
import httpx
from dotenv import load_dotenv
from rich import print
import json

load_dotenv()


def get_cookies() -> list[dict]:
    """"""
    print("Calling Zyte")
    api_response = httpx.post(
        "https://api.zyte.com/v1/extract",
        auth=(os.getenv("ZYTE_KEY"), ""),
        json={
            "url": "https://www.upwork.com/nx/search/jobs/",
            "browserHtml": True,
            "responseCookies": True,
        },
        timeout=60,
    )

    if api_response.status_code != 200:
        print("Failure on Zyte: ", api_response.status_code, api_response.text)
    parsed_res = api_response.json()
    cookies: list[dict] = parsed_res["responseCookies"]
    print(cookies)
    return cookies


def extract_search_token(cookies: list[dict]) -> tuple[str, int]:
    """"""

    print("Extracting Auth Cookie")
    for i in cookies:
        if i["name"] == "UniversalSearchNuxt_vt":
            return i["value"], i["expires"]


def cookie_handler() -> tuple[str, int]:
    """"""
    print("Fetching a token")
    retries = 0
    while retries < 3:
        try:
            cookies = get_cookies()
            search_token, expires = extract_search_token(cookies)
            if not search_token:
                raise ValueError("No token found. Might try again")
            return search_token, expires
        except Exception as e:
            print("Error fetching a token", type(e).__name__, e)
            retries += 1


def publish_token(token: tuple[str, int]):
    """"""

    print("Publishing token")
    url = os.getenv("POSTGREST_URL")
    anon_key = os.getenv("SUPABASE_CLIENT_ANON_KEY")

    payload = {
        "token_name": "UniversalSearch",
        "token_value": token[0],
        "expires": token[1],
    }
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    response = httpx.post(url, json=payload, headers=headers)


def validate_request(event: dict):

    secret = os.getenv("AUTH_SECRET")

    if event["secret"] == secret:
        return True
    raise RuntimeError("Authentication failed")


def lambda_handler(event: dict, context):
    """
    Entrypoint for lambda
    """
    validate_request(event)
    token = cookie_handler()
    if not token:
        raise ValueError("No token found")
    print("Token retrived sucessfully")

    publish_token(token)

    print("All good. Returning token to invoker")
    return json.dumps({"status_code": 200, "token": token[0]})


if __name__ == "__main__":
    data = lambda_handler({"secret": os.getenv("SECRET")}, {})
    print(data)
