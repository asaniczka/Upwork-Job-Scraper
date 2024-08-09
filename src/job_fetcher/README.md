# Job Fetcher Module

Welcome to the Job Fetcher module of the Upwork Job Scraper! This module is designed to fetch job postings directly from Upwork’s public job board, store them in a PostgreSQL database, and can be configured to run on a regular schedule.

## Overview

The Job Fetcher retrieves job information, including title, description, skills, published date, and budget, from Upwork's API. The collected job data is then processed and uploaded to a specified database for further use in the enrichment process.

## Key Features

- Fetches job postings from Upwork's public job board using GraphQL API.
- Parses job postings into structured data models.
- Uploads job data to a PostgreSQL database asynchronously.
- Can be invoked as an AWS Lambda function for scheduled execution.

## Architecture

The Job Fetcher is a lightweight microservice that interacts with Upwork’s API and a PostgreSQL database:

```
+-------------------+
|  Upwork Platform  |
+-------------------+
          |
          v
+-------------------+
|    Job Fetcher    | <--- AWS Lambda
+-------------------+
          |
          v
+-------------------+
|   PostgreSQL DB   |
+-------------------+
```
