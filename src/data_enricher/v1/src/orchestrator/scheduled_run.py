"""Runs the manual orchestrator on a schedule"""

import time
import random

from src.orchestrator.manual_run import attribute_executor, hire_rate_executor
from src.upwork_accounts.browser_handlers import do_login


def executor():
    """"""

    do_login()

    while True:
        try:
            attribute_executor()
            hire_rate_executor()
        except Exception as e:
            print(e)

        time.sleep(15 * 60)


if __name__ == "__main__":
    executor()
