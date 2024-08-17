""""""

# pylint: disable = wrong-import-position
from wrapworks.files import load_json
from wrapworks import cwdtoenv
from rich import print
from dotenv import load_dotenv
import httpx
import ua_generator

load_dotenv()
cwdtoenv()

from src.upwork_accounts.browser_worker import get_cookies
from src.upwork_accounts.browser_worker import login

from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER
from src.models.upwork_models import WorkHistory
from src.models.db_models import DBUpworkContracts
from src.errors.common_errors import NotLoggedIn


def test():
    raw_data = load_json("src/temp/sample.json")
    work_history = WorkHistory(**raw_data)

    with SESSIONMAKER() as session:
        # pylint:disable=not-an-iterable
        for i in work_history.work_history:
            job = i.model_dump()
            job = DBUpworkContracts(**job)
            session.merge(job)

        session.commit()


def save_to_db(work_history: WorkHistory):
    """"""

    if not work_history:
        return

    assert isinstance(
        work_history, WorkHistory
    ), f"Expected WorkHistory, but got type {type(work_history)}"

    print("Adding work history to db")
    with SESSIONMAKER() as session:
        # pylint:disable=not-an-iterable
        for i in work_history.work_history:
            job = i.model_dump()
            job = DBUpworkContracts(**job)
            session.merge(job)

        session.commit()


def get_history(cipher: str) -> dict:

    url = f"https://www.upwork.com/job-details/jobdetails/api/job/{cipher}/details"

    headers = {
        "User-Agent": ua_generator.generate(
            device=("desktop"), browser=("chrome")
        ).text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://www.upwork.com/nx/find-work/details/{cipher}",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "; ".join(
            f"{key}={value}"
            for key, value in get_cookies(make_simple_dict=True).items()
        ),
    }

    response = httpx.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()


def handle_single_client(cipher: str):
    """"""

    print(f"Fetching hire history of {cipher}")

    try:
        res = get_history(cipher)
        if "details" in res and "not authenticated" in res.get("details", ""):
            raise NotLoggedIn()

        work_history = WorkHistory(**res)
        save_to_db(work_history)
    except Exception as e:
        print("Error processing a client", cipher, type(e).__name__, e)


if __name__ == "__main__":
    cipher = "~01d8401788c08f98a3"
    handle_single_client(cipher)
