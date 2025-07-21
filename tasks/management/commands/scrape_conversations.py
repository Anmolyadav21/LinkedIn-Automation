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
import json

class Command(BaseCommand):
    help = 'Scrapes LinkedIn conversations for accepted connections'

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

    def scrape_conversation(self, driver, profile_url):
        try:
            driver.get(profile_url)
            message_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[1]/button/span"))
            )
            message_btn.click()
            time.sleep(2)

            # Wait for messages to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "msg-s-message-list__event"))
            )

            messages = []
            message_blocks = driver.find_elements(By.CLASS_NAME, "msg-s-message-list__event")
            for msg in message_blocks:
                sender = msg.find_element(By.CLASS_NAME, "msg-s-message-group__name").text
                content = msg.find_element(By.CLASS_NAME, "msg-s-event-listitem__body").text
                timestamp = msg.find_element(By.CLASS_NAME, "msg-s-message-group__timestamp").text
                messages.append({
                    "from": sender,
                    "timestamp": timestamp,
                    "message": content
                })

            return {
                "Linkedin_url": profile_url,
                "messages": messages,
                "unread_count": sum(1 for m in messages if m['from'] != "You")
            }
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error scraping {profile_url}: {e}"))
            return None

    def handle(self, *args, **kwargs):
        li_cookie = "your_linkedin_cookie_here"
        input_csv = "profile_urls.csv"
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        all_conversations = []

        try:
            if not self.linkedin_login(driver, li_cookie):
                return

            df = pd.read_csv(input_csv)
            for index, row in df.iterrows():
                profile_url = row["Linkedin_URL"]
                self.stdout.write(self.style.SUCCESS(f"Scraping: {profile_url}"))
                convo = self.scrape_conversation(driver, profile_url)
                if convo:
                    all_conversations.append(convo)
                time.sleep(3)

        finally:
            driver.quit()

        with open("conversations.json", "w") as f:
            json.dump(all_conversations, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Saved {len(all_conversations)} conversations"))
