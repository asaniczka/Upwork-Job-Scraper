# Upwork Job Dataset Maker

This project aims to create a large dataset of job postings on Upwork for future analysis.

## Task description

- Fetch RSS feeds from a specified URL every 2 minutes.
- Save the fetched RSS feeds as files in a "collections" folder.
- Parse the XML files and extract job information.
- Process the job descriptions to extract specific details such as hourly rates, budgets, and country.
- Create a pandas dataframe from the extracted job data.
- Remove duplicate job listings based on the job link.
- Save the dataset as a CSV file.

## Key Responsibilities

- Ensure that the RSS feeds are fetched and saved correctly.
- Handle any errors that occur during the parsing or processing of job data.
- Pay attention to the correct extraction of job details from the descriptions.
- Remove duplicate job listings to maintain data integrity.
- Save the dataset in the proper format and location.

## How to Use

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set the URL for the RSS feeds in the `.env` file.
4. Run the `collector.py` script using `python collector.py` to start collecting the RSS feeds.
5. After collecting a sufficient number of XML files, run the `dataset_maker.py` script using `python dataset_maker.py`.
6. The dataframe will be saved as a CSV file in the project's data folder with a timestamp.
