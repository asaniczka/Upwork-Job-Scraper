"""
Makes a dataset from extracted RSS feeds
"""

import os
import datetime
import re
import csv

import asaniczka
import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel


class Job(BaseModel):
    """pydantic model to store job data"""

    title: str = None
    link: str = None
    description: str = None
    published_date: datetime.date = None
    is_hourly: bool = None
    hourly_low: int = None
    hourly_high: int = None
    budget: int = None
    country: str = None


def process_description(job: Job, description: str):
    """
    Parses the description

    Responsibility:

     - Extract relevant information from the job description and assign it to the corresponding attributes of the Job object.

    Args:
    - `job`: A Job object representing the job to process the description for.
    - `description`: A string containing the job description.

    Returns:
    - `job`: A Job object with updated attributes based on the extracted information.

    """

    if "<b>Hourly Range</b>" in description:
        # fmt: off
        hourly_low = re.search(
                            r"Hourly Range<\/b>:\s*\$([\d,]+)", 
                            description
                        ).group(1)
        hourly_low = int(hourly_low.replace(",", ""))

        try:
            hourly_high = re.search(
                                r"Hourly Range<\/b>:\s*\$([\d,]+)[\.0]+-\$(\d+)", 
                                description
                            ).group(2)
            hourly_high = int(hourly_high.replace(",", ""))
            
        except AttributeError:
            hourly_high = None

        # fmt: on

        job.is_hourly = True
        job.hourly_low = hourly_low
        job.hourly_high = hourly_high

    if "<b>Budget</b>" in description:

        budget = re.search(r"<b>Budget<\/b>:\s*\$([\d,]+\d*)", description).group(1)
        budget = int(budget.replace(",", ""))

        job.is_hourly = False
        job.budget = budget

    try:
        country = re.search(r"Country</b>:\s(.*)\s<br", description).group(1).strip()
        job.country = country
    except AttributeError:
        pass

    html_soup = BeautifulSoup(description, "html.parser")
    job.description = html_soup.get_text(strip=True)

    return job


def handle_item(item: BeautifulSoup, project: asaniczka.ProjectSetup) -> Job:
    """
    Handles processing of the job

    Responsibility:

    - Extracts relevant information from the XML item and creates a Job object with the extracted data.

    Args:
    - `item`: A BeautifulSoup object representing an XML item containing job data.
    - `project`: An asaniczka.ProjectSetup object representing the project setup.

    Returns:
    - `job`: A Job object representing the processed job data.


    """

    job = Job()

    job.title = item.select_one("title").get_text().replace(" - Upwork", "").strip()
    job.link = item.select_one("link").get_text()
    published_date = item.select_one("pubDate").get_text()
    # Tue, 13 Feb 2024 09:31:33 +0000

    job.published_date = datetime.datetime.strptime(
        published_date, "%a, %d %b %Y %H:%M:%S %z"
    )

    description = item.select_one("description").get_text(strip=True)

    try:
        job = process_description(job, description)
    except Exception as error:
        project.logger.warning(
            f"Error parsing description: {asaniczka.format_error(error)} \n {description}"
        )

    return job


def handle_process_file(
    file_path: os.PathLike, project: asaniczka.ProjectSetup
) -> list[Job]:
    """
    handles the process of a single rss feed

    Responsibility:
    - Reads the XML file containing job data, extracts each item, and processes them using the handle_item function.
    - Returns a list of Job objects representing the processed job data.

    Args:
    - `file_path`: A string or os.PathLike object representing the path to the XML file.
    - `project`: An asaniczka.ProjectSetup object representing the project setup.

    Returns:
    - `jobs`: A list of Job objects representing the processed job data.
    """

    with open(file_path, "r", encoding="utf-8") as rf:
        soup = BeautifulSoup(rf.read(), "xml")

    items = soup.select("item")
    jobs = []

    for item in items:
        job = handle_item(item, project)
        jobs.append(job)

    return jobs


def create_dataset(jobs: list[Job]) -> pd.DataFrame:
    """
    creates a pandas dataframe

    Responsibility:
    - Converts the list of Job objects into a pandas DataFrame.
    - Removes duplicate rows based on the 'link' column.
    - Prints information about the DataFrame.
    - Returns the DataFrame.

    Args:
    - `jobs`: A list of Job objects representing the processed job data.

    Returns:
    - `df`: A pandas DataFrame containing the processed job data.
    """

    all_jobs = [job.model_dump() for job in jobs]

    df = pd.DataFrame(all_jobs)
    df.drop_duplicates(["link"], inplace=True)
    print(df.info())

    return df


def executor():
    """
    Main executor of this module

    Responsibility:
    - Sets up the project.
    - Retrieves the list of files in the data folder.
    - Calls the handle_process_file function for each file to process the job data.
    - Calls the create_dataset function to convert the processed job data into a DataFrame.
    - Saves the DataFrame as a CSV file.


    """

    data_folder = "Upwork_Jobs/data/collections"
    project = asaniczka.ProjectSetup("Upwork_Jobs")
    all_files = os.listdir(data_folder)

    all_jobs = []
    for file in all_files:
        file_path = os.path.join(data_folder, file)
        jobs = handle_process_file(file_path, project)
        all_jobs.extend(jobs)

    df = create_dataset(all_jobs)

    df.to_csv(
        os.path.join(
            project.data_folder, f"upwork_jobs_{datetime.datetime.now().date()}.csv"
        ),
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
        encoding="utf-8",
    )


if __name__ == "__main__":
    executor()
