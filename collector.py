"""
This module is responsible for collecting RSS XML feeds every 2 minutes.
"""

import os
import time
import datetime

import asaniczka
from scheduler import Scheduler
import dotenv

dotenv.load_dotenv()
LOOPS = 0


def collect_rss():
    """
    Collects RSS feed and saves it as a file.

    Responsibility:
    - Create a project setup instance
    - Fetch the RSS feed from a specified URL
    - Create a folder for collections within the project data folder
    - Save the fetched RSS feed as a file in the collections folder
    - Increment the "loops" global variable
    - Print the number of completed loops

    """

    global LOOPS

    project = asaniczka.ProjectSetup("Upwork_Jobs")
    collection_folder = project.create_folder(project.data_folder, "collections")

    url = os.getenv("url")

    response = asaniczka.get_request(url, silence_exceptions=True)

    asaniczka.save_file(collection_folder, response, extionsion="rss")

    LOOPS += 1
    print(f"Completed {LOOPS} loops")


schedule = Scheduler()
schedule.cyclic(datetime.timedelta(minutes=2), collect_rss)

while True:
    schedule.exec_jobs()
