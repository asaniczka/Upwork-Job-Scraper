"""
This module constains the worker responsible for gather client data.

My goal is for this to work on requests. 
So each request will call exectuor with a url to scrape, it will scrape and put the data back into the db
"""

from datetime import datetime
import re

from pydantic import HttpUrl, BaseModel
import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import dateparser
from rich import print


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
    duration_months: int | None = None
    freelancer_experince_level: str | None = None
    project_type: str | None = None
    proposals: int = 0
    interviewing: int = 0
    invites_sent: int = 0
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


def extract_fixed_price_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts fixed price data
    """

    try:
        budget = page.select_one("ul.features li:first-child p").get_text(strip=True)
        budget = int(budget)
    except Exception as e:
        print(f"Error extracting fixed price for  {url}: {e}")
        budget = None

    try:
        freelancer_experince_level = page.select_one(
            "ul.features li:nth-child(2) strong"
        ).get_text(strip=True)
    except Exception as e:
        print(f"Error extracting freelancer_experince_level for  {url}: {e}")
        freelancer_experince_level = None

    try:
        project_type = page.select_one("ul.features li:nth-child(4) strong").get_text(
            strip=True
        )
    except Exception as e:
        print(f"Error extracting project_type for  {url}: {e}")

        project_type = None

    return_candidate = {
        "budget": budget,
        "freelancer_experince_level": freelancer_experince_level,
        "project_type": project_type,
    }

    return return_candidate


def extract_hourly_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extract hourly data
    """
    # fmt:off
    try:
        hourly_low = page.select_one("ul.features li:nth-child(4)").get_text(strip=True)
        hourly_low = hourly_low.split("-")[0].replace("$", "").strip()
        hourly_low = float(hourly_low)
    except Exception as e:
        print(f"Error extracting hourly_low for  {url}: {e}")
        hourly_low = None
    try:
        hourly_high = page.select_one("ul.features li:nth-child(4)").get_text(
            strip=True
        )
        hourly_high = hourly_high.split("-")[1]\
                                .replace("$", "")\
                                .replace("Hourly", "")\
                                .strip()
        
        hourly_high = float(hourly_high)
    except Exception as e:
        print(f"Error extracting hourly_high for  {url}: {e}")
        hourly_high = None

    try:
        freelancer_experince_level = page\
            .select_one("ul.features li:nth-child(3) strong")\
            .get_text(strip=True)
    except Exception as e:
        print(f"Error extracting freelancer_experince_level for  {url}: {e}")
        freelancer_experince_level = None

    try:
        duration = page\
            .select_one("ul.features li:nth-child(2) strong")\
            .get_text(strip=True)
        
        duration_num = re.search(r"(\d+)", duration).group(1)
        duration_months = duration_num[-1]
    except Exception as e:
        print(f"Error extracting duration for  {url}: {e}")
        duration_months = None

    try:
        project_type = page.select_one("ul.features li:nth-child(6) strong")\
                            .get_text(strip=True)
    except Exception as e:
        print(f"Error extracting project_type for  {url}: {e}")

        project_type = None
    # fmt:on

    return_candidate = {
        "hourly_low": hourly_low,
        "hourly_high": hourly_high,
        "freelancer_experince_level": freelancer_experince_level,
        "duration_months": duration_months,
        "project_type": project_type,
    }

    return return_candidate


def extract_proposal_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts proposal data from the description
    """

    proposal_count = page.select_one(
        ".client-activity-items li:nth-child(1) span.value"
    ).get_text(strip=True)

    proposal_count = re.search(r"(\d+)", proposal_count).group(1)

    interviewing = page.select_one(
        ".client-activity-items li:nth-child(2) div"
    ).get_text(strip=True)

    invites_sent = page.select_one(
        ".client-activity-items li:nth-child(3) div"
    ).get_text(strip=True)

    unanswered_invites = page.select_one(
        ".client-activity-items li:nth-child(4) div"
    ).get_text(strip=True)

    return_candidate = {
        "proposals": proposal_count,
        "interviewing": interviewing,
        "invites_sent": invites_sent,
        "unanswered_invites": unanswered_invites,
    }

    return return_candidate


def handler_extract_job_data(page: BeautifulSoup, url: HttpUrl) -> JobModel:
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

    if pricing_determiner[0] == "fixed-price":
        is_hourly = False
    else:
        is_hourly = True

    if not is_hourly:
        price_data = extract_fixed_price_data(page, url)
    else:
        price_data = extract_hourly_data(page, url)

    proposal_data = extract_proposal_data(page, url)

    job_data = JobModel(
        title=title,
        posted_time=posted_time_utc,
        description=description,
        is_hourly=is_hourly,
        url=url,
        **price_data,
        **proposal_data,
    )

    print(job_data)
    return 1


def handler_parse_page(page: str, url: HttpUrl):
    """
    Cordinates the parsing of the page
    """

    soup = BeautifulSoup(page, "html.parser")

    job_data = handler_extract_job_data(soup, url)


def executor(url: HttpUrl):
    """This is the main entrypoint of the module"""

    page = get_page_pw(url)

    if not page:
        return

    handler_parse_page(page, url)


if __name__ == "__main__":
    URL_FIXED = "https://www.upwork.com/jobs/Create-200-technical-structural-section-for-small-Architecture-project_%7E01b5acb92967295a3e?source=rss"

    URL_HOURLY = "https://www.upwork.com/jobs/Create-landing-page-through-Shopify_%7E012a0ec9d047034632?source=rss"

    executor(URL_FIXED)
