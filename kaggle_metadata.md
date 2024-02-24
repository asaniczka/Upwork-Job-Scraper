### Title:

Upwork Job Postings Dataset (50K Records)

### Subtitle:

Real-time data collected over 2 weeks

### Description:

```markdown
## About the Dataset:

Upwork is a popular online job platform where freelancers and businesses connect. This dataset contains 50,000 job postings from Upwork, spanning various categories and countries. With this dataset, you can analyze job trends, pricing strategies, and geographical preferences of Upwork users.

> If you find this dataset helpful, please leave an upvote 😊🚀

## Interesting Task Ideas:

1. Analyze the most in-demand skills across different job categories.
2. Predict the budget range based on job titles and descriptions.
3. Identify countries with the highest number of job postings.
4. Develop a recommendation system for freelancers based on their skillset.
5. Compare hourly rates for different types of jobs.
6. Predict the likelihood of a job being hourly or fixed-price
7. Explore how the number of job postings fluctuates over time.
8. Use Natural Language Processing (NLP) techniques to categorize job descriptions.


```

### File Description:

A comprehensive dataset containing 50,000 Upwork job postings. Includes job title, description, budget details, and more.

### Column descriptions:

#####title

Job title mentioned in the listing. (type:str)

#####link

URL link to the job posting. (type:str)

#####description

Detailed description of the job requirements. (type:str)

#####published_date

Date and time when the job was posted on Upwork. (type:datetime)

#####is_hourly

A boolean value indicating if the job is hourly-based or fixed-price. (type:bool)

#####hourly_low

Lower range of hourly rate for hourly-based jobs. (type:float)

#####hourly_high

Upper range of hourly rate for hourly-based jobs. (type:float)

#####budget

Budget allocated for fixed-price jobs. (type:float)

#####country

Country where the job is located or targeted. (type:str)

### Provenance:

#####sources:

Real-time data collected directly from Upwork

#####Collection Methodology:

Data was collected by scraping job postings every minute from Upwork for over 2 weeks.

---

### Note:

Take caution when scraping data from websites like Upwork, as it may violate the terms of service. Make sure to adhere to Upwork's policies and guidelines when collecting data.
