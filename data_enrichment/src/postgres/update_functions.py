"""module to update rows"""

import os

import httpx

from src.models.upwork_models import PostingAttributes


def update_row(link: str, attributes: PostingAttributes):
    """"""

    url = os.getenv("POSTGREST_URL")+"/upwork_filtered_jobs"

    querystring = {"link": link}

    payload = {
        "full_description": attributes.job.full_description,
        "client_city": attributes.client.client_city,
        "client_join_data": attributes.client.client_join_date,
        "client_jobs_posted": attributes.client.client_jobs_posted,
        "client_hire_rate": attributes.client.client_hire_rate,
        "client_open_jobs": attributes.client.client_open_jobs,
        "client_total_spent_usd": attributes.client.client_total_spent_usd,
        "client_total_hires": attributes.client.client_total_hires,
        "client_active_hires": attributes.client.client_active_hires,
        "client_avg_hourly_rate": attributes.client.client_avg_hourly_rate,
        "client_total_paid_hours": attributes.client.client_total_paid_hours,
        "did_augment_client_data": True,
    }
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv("SUPABASE_CLIENT_ANON_KEY")}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    response = httpx.patch(url, json=payload, headers=headers, params=querystring)

    print(response.text)
