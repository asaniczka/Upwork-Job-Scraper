"""Handles retrival of an Auth Token"""

import os
import httpx
from dotenv import load_dotenv
from rich import print

load_dotenv()


def get_cookies() -> list[dict]:
    """"""

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

    parsed_res = api_response.json()
    cookies: list[dict] = parsed_res["responseCookies"]
    return cookies


def extract_search_token(cookies: list[dict]) -> tuple[str, int]:
    """"""

    for i in cookies:
        if i["name"] == "UniversalSearchNuxt_vt":
            return i["value"], i["expires"]


def cookie_handler() -> tuple[str, int]:
    """"""

    retries = 0
    while retries < 3:
        try:
            cookies = get_cookies()
            search_token, expires = extract_search_token(cookies)
            if not search_token:
                raise ValueError("No token found. Might try again")
            return search_token, expires
        except Exception as e:
            print(type(e).__name__, e)
            retries += 1


def publish_token(token: tuple[str, int]):
    """"""

    url = os.getenv("POSTGREST_URL")
    anon_key = os.getenv("SUPABASE_CLIENT_ANON_KEY")

    payload = {
        "token_name": "UniversalSearchNuxt_vt",
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


def executor():
    """"""

    token = cookie_handler()
    if not token:
        raise ValueError("No token found")

    publish_token(token)


if __name__ == "__main__":
    executor()
