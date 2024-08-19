"""
Module to manually trigger data augmentation
"""

# pylint:disable=wrong-import-position
from rich import print

from src.history_fetcher.fetch_freelancer_history import handle_freelancer_profile
from src.sqlalchemy.update_functions import (
    mark_freelancer_as_scraped,
    update_freelancer_in_db,
)

from src.errors.common_errors import NotLoggedIn


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
