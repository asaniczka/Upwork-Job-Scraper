"""
Module to manually trigger data augmentation
"""

# pylint:disable=wrong-import-position

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from wrapworks import cwdtoenv
from dotenv import load_dotenv
from rich import print

load_dotenv()
cwdtoenv()

from src.postgres.select_functions import (
    get_pending_client_data_row,
    get_pending_hire_history_row,
)
from src.postgres.update_functions import (
    update_row,
    update_row_as_done,
    update_hire_history_as_done,
)
from src.upwork_accounts.browser_handlers import get_page, do_login
from src.attribute_extractor.get_attributes import entry_extract_attributes
from src.history_fetcher.fetch_client_history import handle_single_client
from src.history_fetcher.fetch_freelancer_history import handle_freelancer_profile
from src.formatter.format_cipher import get_cipher
from src.sqlalchemy.update_functions import (
    mark_freelancer_as_scraped,
    update_freelancer_in_db,
)
from src.sqlalchemy.select_functions import (
    get_freelancer_from_db,
    get_batch_freelancers_from_db,
)
from src.errors.common_errors import NotLoggedIn


def client_data_executor():
    """"""

    while True:
        url = get_pending_client_data_row()
        if not url:
            print("No more enrich rows left to process")
            break

        page = get_page(url)
        try:
            response, attributes = entry_extract_attributes(page)
            print(attributes)
            update_row(url, attributes)
        except Exception as e:
            print("Unable to extract attributes: ", type(e).__name__, e)
            update_row_as_done(url)


def hire_history_executor():
    """"""
    while True:
        url = get_pending_hire_history_row()
        if not url:
            print("No more hire rows left to process")
            break

        try:
            cipher = get_cipher(url)
            handle_single_client(cipher)
            update_hire_history_as_done(url)
        except NotLoggedIn:
            do_login()
            continue
        except Exception as e:
            print("Unable to get hire history: ", url, type(e).__name__, e)
            update_hire_history_as_done(url)


def handler_freelancer_history_threaded(cipher: str):
    """"""

    try:
        freelancer = handle_freelancer_profile(cipher)
        update_freelancer_in_db(freelancer)
    except NotLoggedIn:
        raise
    except Exception as e:
        print("Unable to get freelancer history: ", cipher, type(e).__name__, e)
        mark_freelancer_as_scraped(cipher)


def freelancer_history_executor():
    """"""
    needs_login = False
    while True:
        if needs_login:
            do_login()
            needs_login = False
        ciphers = get_batch_freelancers_from_db(30)
        if not ciphers:
            print("No more freelancer rows left to process")
            break

        with ThreadPoolExecutor(max_workers=20) as tpe:
            futures = [
                tpe.submit(handler_freelancer_history_threaded, x) for x in ciphers
            ]

            for future in as_completed(futures):
                try:
                    _ = future.result()
                except NotLoggedIn:
                    needs_login = True
                except Exception as e:
                    print("Unknwon Exception in tpe:", type(e).__name__, e)


if __name__ == "__main__":
    freelancer_history_executor()
