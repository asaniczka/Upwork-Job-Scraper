"""
This module is responsible for fetching jobs from the upwork public job board
It also saves them to a database
This can be configured to run on a schedule
"""

import os
from datetime import datetime
import asyncio
import json

from pydantic import (
    BaseModel,
    Field,
    AliasChoices,
    AliasPath,
    model_validator,
    field_serializer,
    field_validator,
)
import httpx
import ua_generator
import dotenv

dotenv.load_dotenv()


class OntologySkill(BaseModel):
    """Holds and individual skill"""

    prefLabel: str


class Job(BaseModel):
    """Holds data for an individual job"""

    title: str | None = Field(validation_alias=AliasPath("title"))
    link: str = Field(validation_alias=AliasPath("jobTile", "job", "ciphertext"))
    description: str | None = Field(validation_alias=AliasPath("description"))
    skills: list[OntologySkill] | None = Field(
        validation_alias=AliasPath("ontologySkills")
    )
    published_date: datetime = Field(
        validation_alias=AliasPath("jobTile", "job", "publishTime")
    )
    is_hourly: bool = None
    job_type: str = Field(validation_alias=AliasPath("jobTile", "job", "jobType"))
    hourly_low: int | str | None = Field(
        validation_alias=AliasPath("jobTile", "job", "hourlyBudgetMin")
    )
    hourly_high: int | str | None = Field(
        validation_alias=AliasPath("jobTile", "job", "hourlyBudgetMax")
    )
    budget: int | str | None = Field(
        validation_alias=AliasChoices(
            AliasPath("jobTile", "job", "fixedPriceAmount", "amount"),
            AliasPath("jobTile", "job", "fixedPriceAmount"),
        )
    )

    @model_validator(mode="after")
    def _find_hourly(self):
        if self.job_type == "HOURLY":
            self.is_hourly = True
        elif self.job_type == "FIXED":
            self.is_hourly = False
        else:
            self.is_hourly = None

        return self

    @field_validator("hourly_low", "hourly_high", "budget", mode="after")
    @classmethod
    def _str2int(cls, value):

        if value is None:
            return None

        return int(float(value))

    @field_serializer("skills", when_used="always")
    @classmethod
    def _ontology2str(cls, value: list[OntologySkill]):

        if not value:
            return None

        return ", ".join(x.prefLabel for x in value)

    @field_validator("link", mode="after")
    @classmethod
    def _cypher2link(cls, value: str):

        return "https://www.upwork.com/freelance-jobs/apply/" + value


class JobList(BaseModel):
    """Holds a list of job posts"""

    jobs: list[Job] = Field(
        validation_alias=AliasPath(
            "data", "search", "universalSearchNuxt", "visitorJobSearchV1", "results"
        )
    )


def get_auth_token(use_authorizer=False) -> str:
    """"""

    if use_authorizer:
        print("Using authorizer to get a token")
        res = httpx.post(
            os.getenv("AUTHORIZER_URL"),
            json={"secret": os.getenv("AUTH_SECRET")},
            timeout=60,
        )
        if res.status_code != 200:
            raise ValueError("Unable to get token via authorizer")
        return res.json().get("token")

    print("Getting Auth token from postgres")
    anon_key = os.getenv("SUPABASE_CLIENT_ANON_KEY")
    base_url = os.getenv("POSTGREST_URL")
    try:
        url = base_url + "token_tracker"
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        params = {
            "select": "token_value",
            "token_name": "eq.UniversalSearch",
            "order": "created_at.desc",
            "limit": 1,
        }

        response = httpx.get(
            url,
            headers=headers,
            params=params,
            timeout=3,
        )

        return response.json()[0]["token_value"]
    except Exception as error:
        print("Error fetching token from postgres", error)


def collect_jobs(auth_token: str) -> dict | None:
    """"""

    url = "https://www.upwork.com/api/graphql/v1"

    payload = {
        "query": """
            query VisitorJobSearch($requestVariables: VisitorJobSearchV1Request!) {
                search {
                universalSearchNuxt {
                    visitorJobSearchV1(request: $requestVariables) {
                    results {
                        id
                        title
                        description
                        ontologySkills {
                        prefLabel
                        }
                        jobTile {
                        job {
                            id
                            ciphertext: cipherText
                            jobType
                            hourlyBudgetMax
                            hourlyBudgetMin
                            contractorTier
                            publishTime
                            fixedPriceAmount {
                            amount
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
    """,
        "variables": {
            "requestVariables": {
                "sort": "recency",
                "highlight": True,
                "paging": {"offset": 0, "count": 50},
            }
        },
    }
    headers = {
        "User-Agent": str(ua_generator.generate()),
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.upwork.com/nx/search/jobs/",
        "X-Upwork-Accept-Language": "en-US",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + auth_token,
        "Origin": "https://www.upwork.com",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    response = httpx.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print(response.text)

    return response.json()


async def upload_to_db(job: Job, client: httpx.Client):
    """Uploads to db"""

    anon_key = os.getenv("SUPABASE_CLIENT_ANON_KEY")
    base_url = os.getenv("POSTGREST_URL")
    try:
        url = base_url + "upwork_jobs_streaming"
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        response = await client.post(
            url,
            headers=headers,
            data=job.model_dump_json(exclude="job_type"),
            timeout=3,
        )
    except Exception as error:
        print("Error inserting to postgres", error)


async def handle_load(jobs: JobList):
    """handles uploading in parallel"""

    client = httpx.AsyncClient()

    tasks = []
    for job in jobs.jobs:
        tasks.append(upload_to_db(job, client))

    await asyncio.gather(*tasks)


def lambda_handler(event, context):
    """
    handles the process of a single rss feed
    """
    retries = 0
    while retries < 2:
        try:
            use_authorizor = retries > 0
            use_authorizor = True
            auth_token = get_auth_token(use_authorizor)
            raw_feed = collect_jobs(auth_token)
            jobs = JobList(**raw_feed)
            break
        except Exception as e:
            print(
                "Error fetching jobs. Trying again with a new token",
                type(e).__name__,
                {str(e)[:500]},
            )
            retries += 1
    else:
        return {"statusCode": 500, "body": json.dumps("Unable to extract from upwork")}

    asyncio.run(handle_load(jobs))
    return {"statusCode": 200, "body": json.dumps("All Good")}


if __name__ == "__main__":
    lambda_handler(1, 1)
