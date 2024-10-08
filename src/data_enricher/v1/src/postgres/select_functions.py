"""module to fetch rows"""

import os

import httpx
from dotenv import load_dotenv
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()


def get_pending_client_data_row() -> str | None:
    """
    ### Description:
        - Fetches a single pending row from the database that
          has not yet been augmented with client data.
        - Connects to the Upwork filtered jobs table via a REST API
          call.

    ### Returns:
        - `str | None`
            The URL link of the fetched row, or None if no rows
            are available.
    """

    print("Getting a new row to enrich client data")

    url = os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs"

    querystring = {"did_augment_client_data": "eq.false", "select": "link", "limit": 1}

    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.get(url, headers=headers, params=querystring)

    rows = response.json()
    if not rows:
        return None
    return rows[0]["link"]


def get_pending_hire_history_row(limit: int = 1) -> list[str] | None:
    """"""

    print("Getting a new hire history row")

    url = os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs"

    querystring = {"got_hire_history": "eq.false", "select": "link", "limit": limit}

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


if __name__ == "__main__":
    link = get_pending_client_data_row()
    print(link)
