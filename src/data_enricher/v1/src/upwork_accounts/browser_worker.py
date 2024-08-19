"""
### Description:
    - This module handles the retrieval and storage of cookies 
      to maintain a login session when scraping web pages.
    - It uses Selenium to load web pages and BeautifulSoup to 
      parse the content.
"""

import os
import json
import time
from pathlib import Path

from rich import print
from wrapworks import timeit, cwdtoenv
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


cwdtoenv()
load_dotenv()


def get_cookies(make_simple_dict: bool = False) -> list[dict] | dict | list:
    """
    ### Description:
        - Retrieves saved cookies from a JSON file to restore
          a previous login session.

    ### Returns:
        - `list[dict]`
            A list of dictionaries representing the cookies.
    """

    print("Getting cookies")
    cwd = Path.cwd()
    folder = Path.joinpath(cwd, "src", "upwork_accounts", "temp")
    folder.mkdir(parents=True, exist_ok=True)
    file = Path.joinpath(folder, "cookies.json")
    if not file.exists():
        return []

    with open(file, "r", encoding="utf-8") as rf:
        cookies = json.load(rf)

    if make_simple_dict:
        all_cookies = {}
        for i in cookies:
            all_cookies[i["name"]] = i["value"]
        cookies = all_cookies

    return cookies


def save_cookies(cookies: list[dict]):
    """
    ### Description:
        - Saves the provided cookies to a JSON file for later
          use in restoring the session.

    ### Args:
        - `cookies`: list[dict]
            A list of dictionaries containing cookie data.

    """
    print("Saving cookies")
    cwd = Path.cwd()
    folder = Path.joinpath(cwd, "src", "upwork_accounts", "temp")
    folder.mkdir(parents=True, exist_ok=True)
    file = Path.joinpath(folder, "cookies.json")
    with open(file, "w", encoding="utf-8") as wf:
        json.dump(cookies, wf)


@timeit()
def get_driver() -> Chrome:
    """"""
    cwd = Path.cwd()
    folder = cwd / "src" / "upwork_accounts" / "temp" / "chrome"
    folder.mkdir(parents=True, exist_ok=True)
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(
        options=options,
        user_data_dir=folder,
        headless=False,
    )

    return driver


def login():
    """"""

    driver = get_driver()
    driver.get("https://www.upwork.com/")
    cookies = get_cookies()
    for i in cookies:
        driver.add_cookie(i)
    driver.get("https://www.upwork.com/ab/account-security/login")

    # enter username
    try:
        username_box = driver.find_element(By.CSS_SELECTOR, "input#login_username")
    except NoSuchElementException:
        print("Already logged in")
        driver.get("https://www.upwork.com/nx/search/jobs/?nbs=1&q=backend")

        # save session cookies
        save_cookies(driver.get_cookies())

        time.sleep(10)
        driver.close()
        return

    username_box.send_keys(os.environ["UPWORK_EMAIL"])
    continue_btn = driver.find_element(
        By.CSS_SELECTOR, "button#login_password_continue"
    )
    continue_btn.click()

    # enter password
    password_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input#login_password"))
    )
    password_box.send_keys(os.environ["UPWORK_PASSWORD"])

    # click save me
    save_btn = driver.find_element(By.CSS_SELECTOR, "label.air3-checkbox-label")
    driver.execute_script("arguments[0].click()", save_btn)

    # press continue
    continue_btn = driver.find_element(By.CSS_SELECTOR, "button#login_control_continue")
    continue_btn.click()
    time.sleep(10)

    driver.get("https://www.upwork.com/nx/search/jobs/?nbs=1&q=backend")

    # save session cookies
    save_cookies(driver.get_cookies())

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    login()
