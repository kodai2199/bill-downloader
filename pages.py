import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class Page:
    def __init__(self, driver, url: str):
        self.driver = driver
        self.url = url

    def load(self):
        self.driver.get(self.url)

    def wait_page_ready(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def perform_actions(self):
        raise NotImplementedError


class StartPage(Page):
    """
    The login page.
    """

    def __init__(self, driver, url: str, username: str, password: str):
        super(StartPage, self).__init__(driver, url)
        self.username = username
        self.password = password

    def perform_actions(self) -> bool:
        """If we are not logged in yet, then the function waits for
        the login fields to appear, and populates them. It then clicks
        on the submit button.

        There should be no need to change the driver URL to the login
        page, as the redirection is automatic.

        Returns:
            bool: Whether the login was successful or not
        """
        self.load()

        if self.logged_in:
            print("Already logged in.")
            return True

        try:
            username_field = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.ID, "userName"))
            )
            password_field = WebDriverWait(self.driver, 1).until(
                expected_conditions.presence_of_element_located((By.ID, "password"))
            )
            submit_button = WebDriverWait(self.driver, 1).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "mat-button-base")
                )
            )
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            submit_button.click()
            print("Login successful.")
            self.wait_page_ready()
            return True
        except TimeoutException:
            print("Could not login.")
            return False

    def wait_page_ready(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "documento-vendita-ricevuto")
            )
        )

    @property
    def logged_in(self):
        if "AziendaOnWeb" in self.driver.title:
            return True
        else:
            return False


class HomePage(Page):
    def __init__(self, driver, url: str):
        super(HomePage, self).__init__(driver, url)

    def perform_actions(self) -> bool:
        if not self.on_home_page:
            self.load()

        if self.is_cookie_banner_visible:
            accepted = self.accept_cookies()
            if not accepted:
                print("Could not accept cookies")
                return False

        # Ensure that the bill cards are loaded, by waiting for one to appear
        try:
            new_bills_card = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, "documento-vendita-ricevuto")
                )
            )

            WebDriverWait(new_bills_card, 5).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.card")
                )
            )
        except TimeoutException:
            print(
                """Could not obtain the bill cards, so there must be no bills available!"""
            )
            return False

        new_bills_link_cards = new_bills_card.find_elements(By.CSS_SELECTOR, "div.card")
        if len(new_bills_link_cards) > 0:
            print("There are some bills that require downloading")
            new_bills_available = True
        else:
            print("No new bills available")
            new_bills_available = False
        return new_bills_available

    @property
    def on_home_page(self):
        if "Impresa - AziendaOnWeb" in self.driver.title:
            return True
        else:
            return False

    def accept_cookies(self):
        if not self.is_cookie_banner_visible:
            return True

        try:
            cookies_accept_button = WebDriverWait(self.driver, 2).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "iubenda-cs-accept-btn")
                )
            )
            cookies_accept_button.click()

            if not self.is_cookie_banner_visible(0.5):
                print("Cookies accepted successfully")
                cookies_accepted = True
            else:
                print("Cookies accepted, but the Iubenda banner is still there.")
                cookies_accepted = False

        except TimeoutException:
            print('Cookies not accepted, because the "Accept" button was not found.')
            if not self.is_cookie_banner_visible(0.5):
                print("However no Iubenda banner was found.")
                cookies_accepted = True
            else:
                print("However, the Iubenda banner is still there.")
                cookies_accepted = False

        return cookies_accepted

    def is_cookie_banner_visible(self, wait_seconds=5):
        try:
            WebDriverWait(self.driver, wait_seconds).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, "iubenda-cs-banner")
                )
            )
            return True
        except TimeoutException:
            return False


class DownloadPage(Page):
    def __init__(self, driver, url: str):
        super(DownloadPage, self).__init__(driver, url)

    def perform_actions(self) -> bool:
        if not self.on_bill_list:
            self.load_bill_list()

        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//a[@title='Scarica PDF']")
                )
            )
        except TimeoutException:
            print("Could not obtain the bill list in time.")
            return False

        download_buttons = self.driver.find_elements(
            By.XPATH, "//a[@title='Scarica PDF']"
        )
        for button in download_buttons:
            print("Found a download button. Downloading.")
            self.download_document(button)
        return True

    def download_document(self, download_button):
        download_button.click()
        download_pdf_dropdowns = self.driver.find_elements(
            By.XPATH,
            "//a[@class='dropdown-item'][contains(text(), 'PDF elettronico')]",
        )
        for pdf_dropdown in download_pdf_dropdowns:
            if pdf_dropdown.text != "PDF elettronico":
                continue
            pdf_dropdown.click()
            # Wait for a popup for additional documents to appear
            # If it does, close it. Otherwise, proceed to the next.
            popup_visible, close_button = self.is_attachments_popup_visible
            if popup_visible:
                print("Attachments popup detected, clicking on 'Close'.")
                ActionChains(self.driver).move_to_element(close_button).click(
                    close_button
                ).perform()

    @property
    def is_attachments_popup_visible(self):
        try:
            attachments_close_button = WebDriverWait(self.driver, 1).until(
                expected_conditions.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='modal-content'][div[@id='modalAllegatiContentId']]//button[@class='close']",
                    )
                )
            )
            return True, attachments_close_button
        except TimeoutException:
            return False, None

    def load_bill_list(self):
        start_date = datetime.datetime.now()
        start_date -= datetime.timedelta(days=30)
        start_date -= datetime.timedelta(days=(start_date.day - 1))
        print(
            f"Loading the list of unread bills since {start_date.strftime('%Y-%m-%d')}"
        )
        self.driver.get(
            f"{self.url}fatturazione/documento-vendita-ricevuto?dataDa={start_date.strftime('%Y-%m-%d')}&statoLettura=2"
        )

        try:
            elements_per_page_select = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "select.seac-dx-page-selector-select")
                )
            )
            Select(elements_per_page_select).select_by_value("1000")
        except NoSuchElementException:
            print(
                "Could not set the bill list to display 1000 elements per page. The system should still work, but older documents might not be getting downloaded."
            )

    @property
    def on_bill_list(self):
        if "documenti" in self.driver.title and "ricevuti" in self.driver.title:
            return True
        else:
            return False
