"""
This module is responsible for collecting RSS XML feeds every 2 minutes, transforming the raw data, and loading them into the DB
"""

import os
import datetime
import re
import asyncio
import json

from bs4 import BeautifulSoup
from pydantic import BaseModel
import httpx

# import dotenv
# dotenv.load_dotenv()


class Job(BaseModel):
    """pydantic model to store job data"""

    title: str = None
    link: str = None
    published_date: datetime.datetime = None
    is_hourly: bool = None
    hourly_low: int = None
    hourly_high: int = None
    budget: int = None
    country: str = None


def collect_rss() -> str | None:
    """
    Collects RSS feed and saves it as a file.

    Responsibility:
    - Create a project setup instance
    - Fetch the RSS feed from a specified URL
    - Create a folder for collections within the project data folder
    - Save the fetched RSS feed as a file in the collections folder
    - Increment the "loops" global variable
    - Print the number of completed loops

    """

    url = os.getenv("upwork_rss_url")

    response = httpx.get(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        },
        timeout=2,
    )

    if response.status_code == 200:
        rss_feed = response.text

        return rss_feed

    return None


def process_description(job: Job, description: str):
    """
    Parses the description
    """

    if "<b>Hourly Range</b>" in description:
        # fmt: off
        hourly_low = re.search(
                            r"Hourly Range<\/b>:\s*\$([\d,]+)", 
                            description
                        ).group(1)
        hourly_low = int(hourly_low.replace(",", ""))

        try:
            hourly_high = re.search(
                                r"Hourly Range<\/b>:\s*\$([\d,]+)[\.0]+-\$(\d+)", 
                                description
                            ).group(2)
            hourly_high = int(hourly_high.replace(",", ""))
            
        except AttributeError:
            hourly_high = None

        # fmt: on

        job.is_hourly = True
        job.hourly_low = hourly_low
        job.hourly_high = hourly_high

    if "<b>Budget</b>" in description:

        budget = re.search(r"<b>Budget<\/b>:\s*\$([\d,]+\d*)", description).group(1)
        budget = int(budget.replace(",", ""))

        job.is_hourly = False
        job.budget = budget

    try:
        country = re.search(r"Country</b>:\s(.*)\s<br", description).group(1).strip()
        job.country = country
    except AttributeError:
        pass

    return job


def handle_item(item: BeautifulSoup) -> Job | None:
    """
    Handles processing of the job

    """

    job = Job()

    job.title = item.select_one("title").get_text().replace(" - Upwork", "").strip()
    job.link = item.select_one("link").get_text()
    published_date = item.select_one("pubDate").get_text()

    job.published_date = datetime.datetime.strptime(
        published_date, "%a, %d %b %Y %H:%M:%S %z"
    )

    description = item.select_one("description").get_text(strip=True)

    try:
        job = process_description(job, description)
        return job
    except:
        return None


async def upload_to_db(job: Job, client: httpx.Client):
    """Uploads to db"""

    anon_key = os.getenv("sb_anon_key")

    try:
        url = "https://aklwouiknrlbwnqazyht.supabase.co/rest/v1/upwork_jobs_streaming"
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        response = await client.post(
            url,
            headers=headers,
            data=job.model_dump_json(),
            timeout=3,
        )

        print(response.status_code, response.text)
    except Exception as error:
        print(error)


async def handle_load(jobs: list[Job]):
    """handles uploading in parallel"""

    client = httpx.AsyncClient()

    tasks = []
    for job in jobs:
        tasks.append(upload_to_db(job, client))

    await asyncio.gather(*tasks)


def lambda_handler(event, context):
    """
    handles the process of a single rss feed
    """

    rss_feed = collect_rss()

    if not rss_feed:
        return {"statusCode": 500, "body": json.dumps("Unable to extract from upwork")}

    soup = BeautifulSoup(rss_feed, "xml")

    items = soup.select("item")
    jobs = []

    for item in items:
        job = handle_item(item)
        jobs.append(job)

    asyncio.run(handle_load(jobs))

    return {"statusCode": 200, "body": json.dumps("All Good")}


if __name__ == "__main__":
    lambda_handler(0, 0)
