# Data Enricher

## Overview

This package is designed to enrich job postings from Upwork by augmenting job data with additional client information. It provides two versions of the data enrichment process, each with its own methods, advantages, and drawbacks.

- **Version 1** relies on a local deployment that requires a logged-in Upwork account to fetch client data, supplemented by OpenAI for extracting attributes.
- **Version 2** utilizes AWS Lambda, allowing for a serverless architecture that is more scalable and cost-effective, while being designed to run on a schedule or on-demand.

<!-- -->

## Responsibilities

The primary responsibilities of the data enrichment system include:

1. **Data Fetching**: Collect job postings from the Upwork API.
2. **Data Augmentation**: Enrich the job postings with client statistics and attributes.
3. **Database Storage**: Save the enriched data into a PostgreSQL database for further use or analysis.
4. **Handling Cloudflare**: The local deployment in Version 1 must bypass Cloudflare's Turnstile, which adds complexity.

<!-- -->

## Pros and Cons

| Feature                 | Version 1                                    | Version 2                                    |
| ----------------------- | -------------------------------------------- | -------------------------------------------- |
| **Deployment Method**   | Local (requires Upwork account)              | Cloud (AWS Lambda)                           |
| **Reliability**         | 100% reliable                                | Approx. 75% reliability due to accessibility |
| **Cost**                | Higher due to OpenAI usage                   | Lower due to serverless architecture         |
| **Scalability**         | Limited (depends on local resources)         | Highly scalable (can run multiple instances) |
| **Cloudflare Handling** | Requires bypassing Cloudflare Turnstile      | No need for bypassing                        |
| **Setup Complexity**    | More cumbersome (local setup, cookies, etc.) | Easier setup with lambda                     |

## Architecture Diagrams

### Version 1 Architecture Diagram (Local Deployment)

```plaintext
+-----------------------+
|   Local Machine       |
|  (Logged-in Session)  |
+-----------+-----------+
            |
            v
+-----------------------+
|     Selenium/Web      |
|       Scraping        |
|      (Bypassing       |
|      Cloudflare)      |
+-----------+-----------+
            |
            v
+-----------------------+
|        OpenAI         |
|     (Extracting       |
|      Attributes)      |
+-----------+-----------+
            |
            v
+-----------------------+
|      PostgreSQL       |
|     (Job Storage)     |
+-----------------------+
```

### Version 2 Architecture Diagram (Cloud Deployment)

```plaintext
+-----------------------+
|   Client Application   |
+-----------+-----------+
            |
            v
+-----------------------+
|     AWS Lambda        |
|   Data Enrichment     |
|(Scheduled & On-Demand)|
+-----------+-----------+
            |
            v
+-----------------------+
|      Upwork API       |
+-----------------------+
            |
            v
+-----------------------+
|       PostgREST       |
|  (Enriched Job Data)  |
|   + PostgreSQL DB     |
+-----------------------+
```

This package provides a flexible and robust solution for enriching job data, allowing for the choice of deployment based on specific needs and circumstances. Whether for reliable local processing or a scalable cloud-based approach, both versions offer valuable capabilities to enhance Upwork job postings with additional client insights.
