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


cwdtoenv()
load_dotenv()


def get_cookies():
    with open("src/scraper/temp/cookies.json", "r", encoding="utf-8") as rf:
        cookies = json.load(rf)
        return cookies


def save_cookies(cookies: list[dict]):
    with open("src/scraper/temp/cookies.json", "w", encoding="utf-8") as wf:
        json.dump(cookies, wf)


def get_page(url: HttpUrl) -> str | None:
    """
    Loads the page using selenium
    """

    with open(
        "src/scraper/temp/pages/90341a983.html", "r", encoding="utf-8"
    ) as rf:
        return rf.read()

    options = uc.ChromeOptions()
    driver = uc.Chrome(
        options=options, user_data_dir=os.getcwd() + "/src/scraper/temp/chrome"
    )
    driver.get(url)
    cookies = get_cookies()
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()
    time.sleep(60)
    source = driver.page_source
    save_cookies(driver.get_cookies())
    driver.close()
    return source


if __name__ == "__main__":

    url = "https://www.upwork.com/jobs/Expert_%7E0118f2d9c90341a983?source=rss"
    page = get_page(url)

    with open(
        "src/scraper/temp/pages/" + url[-20:] + ".html", "w", encoding="utf-8"
    ) as wf:
        wf.write(page)
