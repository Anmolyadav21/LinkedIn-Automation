from django.core.management.base import BaseCommand
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.utils import timezone

class Command(BaseCommand):
    help = 'Processes accepted LinkedIn connections and sends messages'

    def linkedin_login(self, driver, li_cookie):
        driver.get("https://www.linkedin.com/")
        driver.add_cookie({
            "name": "li_at",
            "value": li_cookie,
            "domain": ".linkedin.com",
            "path": "/"
        })
        driver.refresh()
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/feed/')]"))
            )
            self.stdout.write(self.style.SUCCESS('Login successful'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Login failed: {e}'))
            return False

    def handle(self, *args, **kwargs):
        li_cookie = "your_linkedin_cookie_here"
        input_csv = "profile_urls.csv"  # Your CSV with LinkedIn profile URLs
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            if not self.linkedin_login(driver, li_cookie):
                return

            df = pd.read_csv(input_csv)
            for index, row in df.iterrows():
                profile_url = row["Linkedin_URL"]
                self.stdout.write(self.style.SUCCESS(f"Checking connection: {profile_url}"))
                # Call your function to send message to accepted connections
                self.send_message(driver, profile_url)

        finally:
            driver.quit()

    def send_message(self, driver, profile_url):
        # Add the logic to send a message after connection acceptance
        pass  # Add code here for sending a message
