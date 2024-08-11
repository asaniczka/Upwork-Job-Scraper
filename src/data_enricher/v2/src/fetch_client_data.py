"""Module for augmenting client data"""

import httpx


def get_details(cipher: str):
    url = f"https://www.upwork.com/job-details/jobdetails/visitor/{cipher}/details"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
    }

    response = httpx.get(url, headers=headers)

    print(response.text)


if __name__ == "__main__":
    cipher = "~01d2e8eddce1d29fb8"
    get_details(cipher)
