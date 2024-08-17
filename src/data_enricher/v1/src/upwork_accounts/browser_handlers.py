import time

from bs4 import BeautifulSoup
from rich import print


from src.upwork_accounts.browser_worker import (
    save_cookies,
    get_cookies,
    get_driver,
    login,
)


def get_page(url: str) -> str | None:
    """
    ### Description:
        - Loads a webpage using Selenium and returns the text
          content of the page.
        - Automatically refreshes the page with saved cookies.

    ### Args:
        - `url`: str
            The URL of the page to load.

    ### Returns:
        - `str | None`
            The text content of the page, or None if the page
            could not be loaded.
    """

    print(f"Getting page {url}")

    driver = get_driver()
    driver.get(url)

    cookies = get_cookies()
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()
    time.sleep(10)

    source = driver.page_source
    save_cookies(driver.get_cookies())
    driver.close()

    soup = BeautifulSoup(source, "html.parser")
    return soup.get_text(separator="\n")


def do_login():
    """"""
    login()
