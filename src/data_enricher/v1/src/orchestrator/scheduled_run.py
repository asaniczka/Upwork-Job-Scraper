"""Runs the manual orchestrator on a schedule"""

# pylint:disable=wrong-import-position

import time
import random

from wrapworks import cwdtoenv
from dotenv import load_dotenv

cwdtoenv()
load_dotenv()

from src.orchestrator.manual_run import (
    client_data_executor,
    hire_history_executor,
    freelancer_history_executor,
)
from src.upwork_accounts.browser_handlers import do_login


def executor():
    """"""

    do_login()

    while True:
        try:
            client_data_executor()
            hire_history_executor()
            freelancer_history_executor()
        except Exception as e:
            print(e)
        print("Sleeping 15")
        time.sleep(15 * 60)


if __name__ == "__main__":
    executor()
