"""
Module to manually trigger data augmentation
"""

# pylint:disable=wrong-import-position

import json

from wrapworks import cwdtoenv
from dotenv import load_dotenv
from rich import print

load_dotenv()
cwdtoenv()

from src.postgres.select_functions import get_pending_row
from src.postgres.update_functions import update_row, update_row_as_done
from src.scraper.browser_worker import get_page
from src.scraper.get_attributes import entry_extract_attributes


def executor():
    """"""

    while True:
        url = get_pending_row()
        if not url:
            print("No more rows left to process")
            break

        page = get_page(url)
        try:
            response, attributes = entry_extract_attributes(page)
            print(attributes)
            update_row(url, attributes)
        except Exception as e:
            print(f"Unable to extract attributes: {type(e).__name__}: {e}")
            update_row_as_done(url)


if __name__ == "__main__":
    executor()
