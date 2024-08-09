# Data Enricher Module

Welcome to the Data Enricher module of the Upwork Job Scraper! This module is responsible for enriching the fetched job postings with additional contextual data and client information from Upwork. It processes the job descriptions, extracts relevant attributes, and updates the corresponding database entries.

## Overview

The Data Enricher collects job postings that have already been filtered and adds value by retrieving additional information using web scraping techniques and integrating responses from OpenAI's models. The enriched data enhances the insight and usability of the listings, making it easier for users to analyze job opportunities.

## Key Features

- Fetches job postings using Selenium to simulate user browsing and preserve session data with cookies.
- Uses OpenAI API to extract detailed job attributes from the job description, aligning it with a predefined schema.
- Updates the PostgreSQL database with additional enrichment data, including client attributes.
- Implements error handling and retry logic to ensure robust data extraction.

## Architecture

The Data Enricher functions in a modular fashion to facilitate the enrichment process:

```lua
+-------------------+
|   Data Enricher   |
+-------------------+
          |
          v
+-------------------+
|  Job Attributes   | <--- Web Scraping (Selenium)
+-------------------+
          |
          v
+-------------------+
|  OpenAI API       | <--- Data Enhancement
+-------------------+
          |
          v
+-------------------+
|   PostgreSQL DB   | <--- Updated Data
+-------------------+
```
