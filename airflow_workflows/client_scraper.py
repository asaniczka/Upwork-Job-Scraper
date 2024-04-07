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
import asaniczka

# ----------------------------------------
#               MODELS
# ----------------------------------------


class ClientModel(BaseModel):
    """
    pydantic model to store client data
    """

    client_country: str
    client_city: str | None = None
    client_join_date: datetime
    client_jobs_posted: int | None = None
    client_hire_rate: float | None = None
    client_open_jobs: int | None = None
    client_total_spent: int | None = None
    client_total_hires: int | None = None
    client_active_hires: int | None = None
    client_avg_hourly_rate: float | None = None
    client_total_paid_hours: int | None = None


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


# ----------------------------------------
#               WORKERS
# ----------------------------------------


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


def extract_basic_job_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts basic job data
    """
    title = page.select_one("header h4").get_text(strip=True)

    posted_ago = page.select_one("div[data-test=PostedOn] span").get_text(strip=True)
    posted_time_utc = dateparser.parse(
        posted_ago, settings={"TIMEZONE": "+0530", "TO_TIMEZONE": "UTC"}
    )

    description = page.select_one("section div.break.mt-2 p").get_text(
        strip=True, separator="\n\n"
    )

    return {
        "title": title,
        "posted_time": posted_time_utc,
        "description": description,
    }


def extract_fixed_price_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts fixed price data
    """

    try:
        budget = page.select_one("ul.features li:first-child p").get_text(strip=True)
        budget = float(budget.replace("$", ""))
    except Exception as e:
        print(f"Error extracting fixed price for  {url}: {asaniczka.format_error(e)}")
        budget = None

    try:
        freelancer_experince_level = page.select_one(
            "ul.features li:nth-child(2) strong"
        ).get_text(strip=True)
    except Exception as e:
        print(
            f"Error extracting freelancer_experince_level for  {url}: {asaniczka.format_error(e)}"
        )
        freelancer_experince_level = None

    try:
        project_type = page.select_one("ul.features li:nth-child(4) strong").get_text(
            strip=True
        )
    except Exception as e:
        print(f"Error extracting project_type for  {url}: {asaniczka.format_error(e)}")

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
        print(f"Error extracting hourly_low for  {url}: {asaniczka.format_error(e)}")
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
        print(f"Error extracting hourly_high for  {url}: {asaniczka.format_error(e)}")
        hourly_high = None

    try:
        freelancer_experince_level = page\
            .select_one("ul.features li:nth-child(3) strong")\
            .get_text(strip=True)
    except Exception as e:
        print(f"Error extracting freelancer_experince_level for  {url}: {asaniczka.format_error(e)}")
        freelancer_experince_level = None

    try:
        duration = page\
            .select_one("ul.features li:nth-child(2) strong")\
            .get_text(strip=True)
        
        duration_num = re.search(r"(\d+[-\d]*)", duration).group(1).replace("-","")
        duration_months = duration_num[-1]
    except Exception as e:
        print(f"Error extracting duration for  {url}: {asaniczka.format_error(e)}")
        duration_months = None

    try:
        project_type = page.select_one("ul.features li:nth-child(6) strong")\
                            .get_text(strip=True)
    except Exception as e:
        print(f"Error extracting project_type for  {url}: {asaniczka.format_error(e)}")

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

    # fmt: off
    client_activity_items = page.select_one(".client-activity-items")\
                                .get_text(strip=True)
    viewed_by_client_in_dom =  bool("Last viewed by client" in client_activity_items)
    # fmt: on

    if viewed_by_client_in_dom:
        proposal_count = page.select_one(
            ".client-activity-items li:nth-child(1) span.value"
        ).get_text(strip=True)

        proposal_count = re.search(r"(\d+)", proposal_count).group(1)

        interviewing = page.select_one(
            ".client-activity-items li:nth-child(3) div"
        ).get_text(strip=True)

        invites_sent = page.select_one(
            ".client-activity-items li:nth-child(4) div"
        ).get_text(strip=True)

        unanswered_invites = page.select_one(
            ".client-activity-items li:nth-child(5) div"
        ).get_text(strip=True)
    else:
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


def extract_client_posting_stats(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    extracts a clients' upword posting activity
    """

    try:
        client_job_posting_stats = page.select_one(
            "li[data-qa=client-job-posting-stats]"
        )
        jobs_posted_str = client_job_posting_stats.select_one("strong").get_text(
            strip=True
        )
        jobs_posted = re.search(r"(\d+)", jobs_posted_str).group(1)
        jobs_posted = int(jobs_posted)

        hire_rate_str = client_job_posting_stats.select_one("div").get_text(strip=True)

        hire_rate = re.search(r"(\d+)", hire_rate_str.split(", ")[0]).group(1)
        hire_rate = float(hire_rate)

        open_jobs = re.search(r"(\d+)", hire_rate_str.split(", ")[1]).group(1)
        open_jobs = int(open_jobs)
    except AttributeError:
        open_jobs = None
        hire_rate = None
        jobs_posted = None
    except Exception as e:
        print(
            f"error extracting hire_rate,open_jobs or jobs_posted on {url}: {asaniczka.format_error(e)}"
        )
        open_jobs = None
        hire_rate = None
        jobs_posted = None

    return {
        "client_jobs_posted": jobs_posted,
        "client_hire_rate": hire_rate,
        "client_open_jobs": open_jobs,
    }


def extract_client_spending_stats(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts client's spending stats
    """

    try:
        client_spent_str = page.select_one("strong[data-qa=client-spend]").get_text(
            strip=True
        )
        client_spent = re.search(r"(\d+[\.\d]*)", client_spent_str).group(1)
        client_spent = float(client_spent)
        if "K" in client_spent_str:
            client_spent = client_spent * 1000
        client_spent = int(client_spent)

        client_hires_str = page.select_one("div[data-qa=client-hires]").get_text(
            strip=True
        )

        total_hires = re.search(r"(\d+)", client_hires_str.split(", ")[0]).group(1)
        total_hires = int(total_hires)

        active_hires = re.search(r"(\d+)", client_hires_str.split(", ")[1]).group(1)
        active_hires = int(active_hires)
    except AttributeError:
        client_spent = None
        active_hires = None
        total_hires = None
    except Exception as e:
        print(
            f"Error extracting client_spent or active_hires or total_hires for {url}: {asaniczka.format_error(e)}"
        )
        client_spent = None
        active_hires = None
        total_hires = None

    return {
        "client_total_spent": client_spent,
        "client_total_hires": total_hires,
        "client_active_hires": active_hires,
    }


def extract_client_rates(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts a clients historic spending rates
    """

    try:
        client_hourly_rate_str = page.select_one(
            "strong[data-qa=client-hourly-rate]"
        ).get_text(strip=True)
        client_hourly_rate_str = client_hourly_rate_str.split("/hr")[0].strip()
        client_hourly_rate = float(client_hourly_rate_str.replace("$", ""))
    except AttributeError:
        client_hourly_rate = None
    except Exception as e:
        print(
            f"Error extracting client_hourly_rate for {url}: {asaniczka.format_error(e)}"
        )
        client_hourly_rate = None

    try:
        client_total_paid_hrs_str = page.select_one(
            "div[data-qa=client-hours]"
        ).get_text(strip=True)
        client_total_paid_hrs = float(
            client_total_paid_hrs_str.split(" ")[0].replace(",", "")
        )
    except AttributeError:
        client_total_paid_hrs = None
    except Exception as e:
        print(
            f"Error extracting client_total_paid_hrs_str for {url}: {asaniczka.format_error(e)}"
        )
        client_total_paid_hrs = None

    return {
        "client_avg_hourly_rate": client_hourly_rate,
        "client_total_paid_hours": client_total_paid_hrs,
    }


def extract_basic_client_data(page: BeautifulSoup, url: HttpUrl) -> dict:
    """
    Extracts basic client data
    """

    client_country = page.select_one("li[data-qa=client-location] strong").get_text(
        strip=True
    )
    try:
        client_city = page.select_one(
            "li[data-qa=client-location] div span:first-child"
        ).get_text(strip=True)

        if not client_city:
            client_city = None

    except AttributeError:
        client_city = None
    except Exception as e:
        print(f"Error extracting client_city for {url}: {asaniczka.format_error(e)}")

    client_join_date_str = page.select_one(
        "div[data-qa=client-contract-date]"
    ).get_text(strip=True)
    client_join_date_str = client_join_date_str.split("since")[-1]
    client_join_date = dateparser.parse(client_join_date_str, languages=["en"])

    return {
        "client_country": client_country,
        "client_city": client_city,
        "client_join_date": client_join_date,
    }


# ----------------------------------------
#               HANDLERS
# ----------------------------------------


def handler_extract_client_data(page: BeautifulSoup, url: HttpUrl) -> ClientModel:
    """
    Extracts client data from the given job posting
    """

    basic_client_data = extract_basic_client_data(page, url)
    posting_stats = extract_client_posting_stats(page, url)
    spending_stats = extract_client_spending_stats(page, url)
    client_rates = extract_client_rates(page, url)

    client_data = ClientModel(
        **basic_client_data,
        **posting_stats,
        **spending_stats,
        **client_rates,
    )

    return client_data


def handler_extract_job_data(page: BeautifulSoup, url: HttpUrl) -> JobModel:
    """
    Main extractor for job data
    """

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

    basic_job_data = extract_basic_job_data(page, url)
    proposal_data = extract_proposal_data(page, url)

    job_data = JobModel(
        is_hourly=is_hourly,
        url=url,
        **basic_job_data,
        **price_data,
        **proposal_data,
    )

    return job_data


def handler_parse_page(page: str, url: HttpUrl) -> tuple[JobModel, ClientModel]:
    """
    Cordinates the parsing of the page
    """

    soup = BeautifulSoup(page, "html.parser")

    job_data = handler_extract_job_data(soup, url)
    client_data = handler_extract_client_data(soup, url)

    return job_data, client_data


def executor(url: HttpUrl):
    """This is the main entrypoint of the module"""

    page = get_page_pw(url)

    if not page:
        return

    job_data, client_data = handler_parse_page(page, url)


if __name__ == "__main__":
    URL_FIXED = "https://www.upwork.com/jobs/Create-200-technical-structural-section-for-small-Architecture-project_%7E01b5acb92967295a3e?source=rss"

    URL_HOURLY = "https://www.upwork.com/freelance-jobs/apply/English-Speakers-Wanted-Voice-Actor-Vtuber_~0135f3835eb0fa078d"

    TEST_URL = "https://www.upwork.com/jobs/need-Facebook-ads-expert_%7E0123799d103660d647?source=rss"

    URLS = [
        "https://www.upwork.com/jobs/Facebook-specialist_%7E015b3e8992269f6354?source=rss",
        "https://www.upwork.com/jobs/Virtual-Assistance-Germany-German-Deutschland-Deutsch_%7E0101bd8aa02667479f?source=rss",
        "https://www.upwork.com/jobs/Backend-MERN_%7E01854831a04bbcd1ec?source=rss",
        "https://www.upwork.com/jobs/PAN12-Chatlog-Extraction_%7E01f3cd26bc8b761b51?source=rss",
        "https://www.upwork.com/jobs/need-Facebook-ads-expert_%7E0123799d103660d647?source=rss",
    ]

    executor(TEST_URL)

    # for url in URLS:
    #     executor(url)
