"""Runs the manual orchestrator on a schedule"""

import time
import random

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

        time.sleep(15 * 60)


if __name__ == "__main__":
    executor()
