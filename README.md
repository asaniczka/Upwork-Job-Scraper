# Upwork Job Scraper

Welcome to the Upwork Job Scraper! This is a microservice-based project designed to fetch job postings from Upwork, filter them, and enrich them with additional useful information.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
- [Job Fetcher](#job-fetcher)
- [Data Enricher](#data-enricher)

## Overview

The Upwork Job Scraper consists of two main modules: Job Fetcher and Data Enricher. The Job Fetcher is responsible for retrieving job postings from Upwork and storing them in a PostgreSQL database. The Data Enricher module enhances the filtered job data with additional contextual or relevant information, making it more valuable and actionable.

## Architecture

The architecture of the Upwork Job Scraper is designed to be modular and scalable.

- **Job Fetcher**: Runs on AWS Lambda and retrieves job postings from Upwork regularly.
- **Data Enricher**: Executes on a private server using Selenium, fetching and combining data from various sources to enrich the job postings stored in PostgreSQL.

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
                             |
                             |
                             v
                   +-------------------+
                   |   Data Enricher   | <--- Private Server (Selenium)
                   +-------------------+
                             |
                             v
                   +-------------------+
                   | Enriched Job Data  |
                   +-------------------+
```

## Modules

### Job Fetcher

- **Functionality**: This module is responsible for fetching all jobs posted to Upwork.
- **Storage**: The raw job data is stored in a PostgreSQL database.
- **Filtering**: Filters the raw job data according to defined criteria and saves the filtered jobs to a separate table.

### Data Enricher

- **Functionality**: This module pulls the filtered jobs from the PostgreSQL database and enriches them with additional data.
- **Tech Stack**: Utilizes Selenium for data fetching and manipulation.
