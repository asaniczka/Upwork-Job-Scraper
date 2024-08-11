"""
Module to connect with Zyte
"""

from base64 import b64decode
import os

import httpx


def zyte_worker(
    url: str,
    render_html=True,
    max_retries=5,
    country: str = "US",
) -> str | None:
    """
    ### Description:
        - Makes a request to the Zyte API to retrieve HTML content
          of a specified URL, with support for JavaScript rendering.
        - Retries the request in case of failure, up to a specified maximum.

    ### Args:
        - `url`: str
            The URL of the page to fetch.
        - `render_html`: bool, optional
            Indicates whether to request the rendered HTML; defaults to True.
        - `max_retries`: int, optional
            The maximum number of retries on failure; defaults to 5.
        - `country`: str, optional
            The country for geographical request; defaults to "US".

    ### Returns:
        - `str | None`
            The rendered HTML content of the page, or None if unsuccessful.
    """
    retries = 0
    while retries < max_retries:
        try:
            # pylint: disable = no-else-return
            if render_html:
                print(f"Getting {url} with JS Rendering")
                api_response = httpx.post(
                    "https://api.zyte.com/v1/extract",
                    auth=(os.getenv("ZYTE_KEY"), ""),
                    json={"url": url, "browserHtml": True, "geolocation": country},
                    timeout=60,
                )

                browser_html: str = api_response.json()["browserHtml"]
                return browser_html

            else:
                print(f"Getting {url} with plain get with Zyte")
                api_response = httpx.post(
                    "https://api.zyte.com/v1/extract",
                    auth=(os.getenv("ZYTE_KEY"), ""),
                    json={"url": url, "browserHtml": True, "geolocation": country},
                    timeout=30,
                )

                if api_response.status_code != 200:
                    raise ValueError(
                        f"Page response is not 200: Status was {api_response.status_code}"
                    )

                browser_html: str = api_response.json()["browserHtml"]

                return browser_html
        except Exception as e:
            print(f"Error fetching a page with zyte: {type(e).__name__}: {e}")
            retries += 1
            continue

    return None


if __name__ == "__main__":
    page = zyte_worker("https://asaniczka.com")
    print(type(page))
