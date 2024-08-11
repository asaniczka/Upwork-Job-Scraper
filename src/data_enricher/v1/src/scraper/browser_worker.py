"""
### Description:
    - This module handles the retrieval and storage of cookies 
      to maintain a login session when scraping web pages.
    - It uses Selenium to load web pages and BeautifulSoup to 
      parse the content.
"""

import os
from datetime import datetime
import re
import json
import time

from pydantic import HttpUrl, BaseModel
import httpx
from bs4 import BeautifulSoup
import dateparser
from rich import print
from wrapworks import timeit, cwdtoenv
from dotenv import load_dotenv
import undetected_chromedriver as uc
from bs4 import BeautifulSoup


cwdtoenv()
load_dotenv()


def get_cookies():
    """
    ### Description:
        - Retrieves saved cookies from a JSON file to restore
          a previous login session.

    ### Returns:
        - `list[dict]`
            A list of dictionaries representing the cookies.
    """

    with open("src/scraper/temp/cookies.json", "r", encoding="utf-8") as rf:
        cookies = json.load(rf)
        return cookies


def save_cookies(cookies: list[dict]):
    """
    ### Description:
        - Saves the provided cookies to a JSON file for later
          use in restoring the session.

    ### Args:
        - `cookies`: list[dict]
            A list of dictionaries containing cookie data.

    """
    with open("src/scraper/temp/cookies.json", "w", encoding="utf-8") as wf:
        json.dump(cookies, wf)


def get_page(url: str) -> str | None:
    """
    ### Description:
        - Loads a webpage using Selenium and returns the text
          content of the page.
        - Automatically refreshes the page with saved cookies.

    ### Args:
        - `url`: str
            The URL of the page to load.

    ### Returns:
        - `str | None`
            The text content of the page, or None if the page
            could not be loaded.
    """

    print(f"Getting page {url}")

    options = uc.ChromeOptions()
    driver = uc.Chrome(
        options=options,
        user_data_dir=os.getcwd() + "/src/scraper/temp/chrome",
        headless=False,
    )
    driver.get(url)

    cookies = get_cookies()
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()
    time.sleep(10)

    source = driver.page_source
    save_cookies(driver.get_cookies())
    driver.close()

    soup = BeautifulSoup(source, "html.parser")
    return soup.get_text(separator="\n")


if __name__ == "__main__":

    url = "https://www.upwork.com/jobs/Generative-Expert-Needed_%7E01c5cf6fe1d5c72523?source=rss"
    page = get_page(url)

    with open(
        "src/scraper/temp/pages/" + url[-20:] + ".html", "w", encoding="utf-8"
    ) as wf:
        wf.write(page)
