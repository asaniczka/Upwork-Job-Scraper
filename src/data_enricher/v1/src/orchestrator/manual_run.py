"""
Module to manually trigger data augmentation
"""

# pylint:disable=wrong-import-position

import json
import time

from wrapworks import cwdtoenv
from dotenv import load_dotenv
from rich import print

load_dotenv()
cwdtoenv()

from src.postgres.select_functions import (
    get_pending_enrich_row,
    get_pending_hire_rate_row,
)
from src.postgres.update_functions import (
    update_row,
    update_row_as_done,
    update_hire_history_as_done,
)
from src.upwork_accounts.browser_handlers import get_page, do_login
from src.attribute_extractor.get_attributes import entry_extract_attributes
from src.rate_fetcher.fetch_rates import handle_single_client
from src.formatter.format_cipher import get_cipher
from src.errors.common_errors import NotLoggedIn


def attribute_executor():
    """"""

    while True:
        url = get_pending_enrich_row()
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


def hire_rate_executor():
    """"""
    count = 0
    while True:
        if count // 30 == 0:
            time.sleep(60)

        url = get_pending_hire_rate_row()
        if not url:
            print("No more hire rows left to process")
            break

        try:
            cipher = get_cipher(url)
            handle_single_client(cipher)
            update_hire_history_as_done(url)
            break
        except NotLoggedIn:
            do_login()
            continue
        except Exception as e:
            print("Unable to get hire history: ", url, type(e).__name__, e)
            update_hire_history_as_done(url)


if __name__ == "__main__":
    hire_rate_executor()
