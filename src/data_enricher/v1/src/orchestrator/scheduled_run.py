"""Runs the manual orchestrator on a schedule"""

import time
import random

from src.orchestrator.manual_run import executor as manual_executor


def executor():
    """
    ### Description:
        - An infinite loop that continuously calls the `manual_executor`
          function, providing error handling for any exceptions that may arise.
        - Introduces a pause of 15 minutes between successive calls to
          the executor to control the execution rate.
    """
    while True:
        try:
            manual_executor()
        except Exception as e:
            print(e)

        time.sleep(15 * 60)


if __name__ == "__main__":
    executor()
