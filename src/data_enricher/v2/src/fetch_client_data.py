"""Module for augmenting client data"""

from datetime import datetime
import os
from urllib.parse import quote
import asyncio
import json
import random

import httpx
from pydantic import BaseModel, Field, AliasChoices, AliasPath, field_validator
from wrapworks.files import dump_json
from dotenv import load_dotenv
from rich import print
import ua_generator

load_dotenv()


class UpworkClient(BaseModel):
    client_country: str | None = Field(
        validation_alias=AliasPath("buyer", "location", "country")
    )
    client_city: str | None = Field(
        validation_alias=AliasPath("buyer", "location", "city")
    )
    client_join_date: datetime | None = Field(
        validation_alias=AliasPath("buyer", "company", "contractDate")
    )
    client_jobs_posted: int | None = Field(
        validation_alias=AliasPath("buyer", "jobs", "postedCount")
    )
    client_open_jobs: int | None = Field(
        validation_alias=AliasPath("buyer", "jobs", "openCount")
    )
    client_total_spent_usd: float | int | None = Field(
        validation_alias=AliasChoices(
            AliasPath("buyer", "stats", "totalCharges", "amount"),
            AliasPath("buyer", "stats", "totalCharges"),
        )
    )
    client_total_hires: int | None = Field(
        validation_alias=AliasPath("buyer", "stats", "totalJobsWithHires")
    )
    client_active_hires: int | None = Field(
        validation_alias=AliasPath("buyer", "stats", "activeAssignmentsCount")
    )
    client_avg_hourly_rate: float | None = Field(
        validation_alias=AliasChoices(
            AliasPath("buyer", "avgHourlyJobsRate", "amount"),
            AliasPath("buyer", "avgHourlyJobsRate"),
        )
    )
    client_total_paid_hours: int | float | None = Field(
        validation_alias=AliasPath("buyer", "stats", "hoursCount"),
    )

    @field_validator(
        "client_total_spent_usd",
        "client_avg_hourly_rate",
        "client_total_paid_hours",
        mode="after",
    )
    @classmethod
    def _float2int(cls, value: float | None | int):

        if value is None:
            return None
        return int(value)


async def update_row(upwork_link: str, client: UpworkClient):
    """"""

    print(f"Updating row {upwork_link}")

    url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"

    payload = {
        "client_city": client.client_city,
        "client_join_data": (
            str(client.client_join_date) if client.client_join_date else None
        ),
        "client_jobs_posted": client.client_jobs_posted,
        "client_open_jobs": client.client_open_jobs,
        "client_total_spent_usd": client.client_total_spent_usd,
        "client_total_hires": client.client_total_hires,
        "client_active_hires": client.client_active_hires,
        "client_avg_hourly_rate": client.client_avg_hourly_rate,
        "client_total_paid_hours": client.client_total_paid_hours,
        "did_augment_client_data": True,
    }
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }
    params = {"link": "eq." + upwork_link}
    print(params)

    response = await httpx.AsyncClient(headers=headers).patch(
        url, json=payload, params=params
    )
    print(response.status_code)
    if response.status_code >= 400:
        print(response.text)


def get_pending_rows() -> list[str] | None:
    """"""

    url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"

    querystring = {"did_augment_client_data": "eq.false", "select": "link", "limit": 50}

    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.get(url, headers=headers, params=querystring)

    rows = response.json()
    if not rows:
        return None
    return [x["link"] for x in rows]


def get_proxy() -> str:
    print("Getting a new proxy")

    proxies = os.getenv("PROXIES")
    proxies = json.loads(proxies)

    return random.choice(proxies)


async def get_details(cipher: str) -> UpworkClient:
    """"""
    url = f"https://www.upwork.com/job-details/jobdetails/visitor/{cipher}/details"

    headers = {
        "User-Agent": ua_generator.generate().text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
    }

    response = await httpx.AsyncClient(headers=headers, proxy=get_proxy()).get(url)
    client = UpworkClient(**response.json())

    return client


def link_to_cipher(link: str) -> str:
    """"""
    return link.split("/")[-1]


async def handle_row(url: str):

    retries = 0
    while retries < 3:
        try:
            details = await get_details(link_to_cipher(url))
            await update_row(url, details)
            break
        except Exception as e:
            print("Exception in a URL", url, type(e).__name__, e)
            retries += 1
    else:
        raise RuntimeError("Unable to process row")


async def async_handler(rows: list[str]):

    print(f"We have {len(rows)} to work on this round")

    tasks = [asyncio.Task(handle_row(x)) for x in rows]
    done, pending = await asyncio.wait(tasks, return_when="ALL_COMPLETED")

    completed = 0
    errors = 0
    for future in done:
        if future.exception():
            errors += 1
        else:
            completed += 1

    print(
        f"Out of {len(rows)} rows, {completed} rows completed successfully while {errors} failed"
    )


def lambda_handler(event, context):

    rows = get_pending_rows()
    if not rows:
        print("No rows available")
        return json.dumps({"status_code": 200, "status": "No rows available"})
    asyncio.run(async_handler(rows))

    return json.dumps({"status_code": 200, "status": "Rows processed sucessfully"})


if __name__ == "__main__":
    lambda_handler(1, 1)
