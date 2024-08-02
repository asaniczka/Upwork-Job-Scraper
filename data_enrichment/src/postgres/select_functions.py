"""module to fetch rows"""


import os

import httpx
from dotenv import load_dotenv
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()

def get_pending_row() -> str | None:
    """"""

    print(f"Getting a new row")
    
    url = os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs"

    querystring = {"did_augment_client_data": "eq.false", "select": "link","limit":1}

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

if __name__ == "__main__":
    link = get_pending_row()
    print(link)
