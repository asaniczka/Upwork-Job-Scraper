from curl_cffi import requests
from cfscrape import create_scraper

url = "https://www.upwork.com/api/graphql/v1??__cf_chl_tk=row.I__gJbUo5EPPjryrN_rM1xmyo_AB1_JYDnZYY80-1724770094-0.0.1.1-5716"

payload = {
    "query": """
  query VisitorJobSearch($requestVariables: VisitorJobSearchV1Request!) {
    search {
      universalSearchNuxt {
        visitorJobSearchV1(request: $requestVariables) {
          paging {
            total
            offset
            count
          }

    facets {
      jobType
    {
      key
      value
    }

      workload
    {
      key
      value
    }

      clientHires
    {
      key
      value
    }

      durationV3
    {
      key
      value
    }

      amount
    {
      key
      value
    }

      contractorTier
    {
      key
      value
    }

      contractToHire
    {
      key
      value
    }


    }

          results {
            id
            title
            description
            relevanceEncoded
            ontologySkills {
              uid
              parentSkillUid
              prefLabel
              prettyName: prefLabel
              freeText
              highlighted
            }

            jobTile {
              job {
                id
                ciphertext: cipherText
                jobType
                weeklyRetainerBudget
                hourlyBudgetMax
                hourlyBudgetMin
                hourlyEngagementType
                contractorTier
                sourcingTimestamp
                createTime
                publishTime

                hourlyEngagementDuration {
                  rid
                  label
                  weeks
                  mtime
                  ctime
                }
                fixedPriceAmount {
                  isoCurrencyCode
                  amount
                }
                fixedPriceEngagementDuration {
                  id
                  rid
                  label
                  weeks
                  ctime
                  mtime
                }
              }
            }
          }
        }
      }
    }
  }
  """,
    "variables": {
        "requestVariables": {
            "sort": "recency",
            "highlight": True,
            "paging": {"offset": 10, "count": 10},
        }
    },
}
headers = {
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.upwork.com/nx/search/jobs/?page=2",
    "X-Upwork-Accept-Language": "en-US",
    "Content-Type": "application/json",
    "Authorization": "Bearer oauth2v2_48f466dac6fdaf5fd1669cb3d7df40d6",
}


scraper = cfscrape.create_scraper()
response = scraper.post(url, json=payload, headers=headers)

print(response.text)
