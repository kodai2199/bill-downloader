from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import datetime
import os
from pages import StartPage, HomePage, DownloadPage


class BillDownloader:
    def __init__(self):
        options = Options()
        options.add_experimental_option(
            "prefs", {"download.default_directory": f"{'/home/seluser/to_print'}"}
        )
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Remote(
            command_executor=os.environ["webdriverHost"], options=options
        )
        self.pages = []

    def execute_tasks(self):
        for page in self.pages:
            if not page.perform_actions():
                break


if __name__ == "__main__":
    bill_downloader = BillDownloader()
    pages = [
        StartPage(
            bill_downloader.driver,
            "https://aziendaweb.seac.it/",
            os.environ["username"],
            os.environ["password"],
        ),
        HomePage(
            bill_downloader.driver, "https://aziendaweb.seac.it/impresa/dashboard"
        ),
        DownloadPage(bill_downloader.driver, "https://aziendaweb.seac.it/"),
    ]
    bill_downloader.pages = pages

    try:
        bill_downloader.execute_tasks()
    finally:
        bill_downloader.driver.quit()
