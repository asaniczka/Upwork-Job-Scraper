"""Runs the manual orchestrator on a schedule"""

import time
import random

from src.orchestrator.manual_run import executor as manual_executor


def executor():

    while True:
        try:
            manual_executor()
        except Exception as e:
            print(e)

        time.sleep(random.randint(60 * 60 * 4, 60 * 60 * 6))


if __name__ == "__main__":
    executor()
