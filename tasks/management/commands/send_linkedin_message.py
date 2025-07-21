from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class Command(BaseCommand):
    help = 'Log into LinkedIn and send messages to accepted connections'

    def linkedin_login(self, driver, li_cookie):
        driver.get('https://www.linkedin.com/')
        driver.add_cookie({
            "name": "li_at",
            "value": "",
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
        li_cookie = "your_linkedin_cookie_here"  # You should store this securely
        profile_url = "https://www.linkedin.com/in/your-profile-url"
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            if self.linkedin_login(driver, li_cookie):
                # Call your function to send the message
                self.send_message(driver, profile_url)
            else:
                self.stdout.write(self.style.ERROR("Login failed."))
        finally:
            driver.quit()

    def send_message(self, driver, profile_url):
        # Add logic for sending message to a connection
        pass  # Add code here for sending a message
