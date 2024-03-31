"""
This module constains the worker responsible for gather client data.

My goal is for this to work on requests. 
So each request will call exectuor with a url to scrape, it will scrape and put the data back into the db
"""

from datetime import datetime

from pydantic import HttpUrl, BaseModel
import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import dateparser


class ClientModel(BaseModel):
    """
    pydantic model to store client data
    """

    client_location: str
    client_join_date: datetime
    client_jobs_posted: int | None = None
    client_hire_rate: float | None = None
    client_total_spent: float | None = None
    client_total_hires: int | None = None
    client_avg_hourly_rate: float | None = None
    client_total_paid_hours: int | None = None
    client_company_size: str | None = None
    client_industry: str | None = None


class JobModel(BaseModel):
    """
    Pydantic model to store job data
    """

    url: HttpUrl
    title: str
    posted_time: datetime
    description: str = ""
    is_hourly: bool | None = None
    hourly_low: int | None = None
    hourly_high: int | None = None
    budget: int | None = None
    duration_months: int = 0
    freelancer_experince_level: str
    project_type: str
    proposals: int = 0
    interviewing: int = 0
    invites_send: int = 0
    unanswered_invites: int = 0


def get_page_pw(url: HttpUrl) -> str | None:
    """
    Loads the page using playwright
    """

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        source = page.content()

    return source if len(source) > 1000 else None


def get_page(url: HttpUrl) -> str | None:
    """
    Gets the page source and returns it
    """

    response = httpx.get(url)

    if response.status_code == 200:
        return response.text

    print(
        f"Unable to load url. Status Code: {response.status_code}, Text: {response.text[:500]}"
    )
    return None


def extract_job_data(page: BeautifulSoup, url: HttpUrl) -> JobModel:
    """
    Main extractor for job data
    """

    title = page.select_one("header h4").get_text(strip=True)

    posted_ago = page.select_one("div[data-test=PostedOn] span").get_text(strip=True)
    posted_time_utc = dateparser.parse(
        posted_ago, settings={"TIMEZONE": "+0530", "TO_TIMEZONE": "UTC"}
    )

    description = page.select_one("section div.break.mt-2 p").get_text(strip=True)

    pricing_determiner = page.select_one(
        "ul.features li:first-child div"
    ).get_attribute_list("data-cy")
    
    if pricing_determiner == "fixed-price":
        is_hourly = False
    else:
        is_hourly = True

    print(pricing_determiner)

    return 1


def handler_parse_page(page: str, url: HttpUrl):
    """
    Cordinates the parsing of the page
    """

    soup = BeautifulSoup(page, "html.parser")

    job_data = extract_job_data(soup, url)


def executor(url: HttpUrl):
    """This is the main entrypoint of the module"""

    page = get_page_pw(url)

    if not page:
        return

    handler_parse_page(page, url)


if __name__ == "__main__":
    URL = "https://www.upwork.com/jobs/Create-200-technical-structural-section-for-small-Architecture-project_%7E01b5acb92967295a3e?source=rss"

    executor(URL)
