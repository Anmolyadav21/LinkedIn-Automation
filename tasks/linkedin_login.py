from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

def linkedin_login(driver, email, password):
    try:
        # Open LinkedIn login page
        driver.get("https://www.linkedin.com/login")

        # Wait until the email input is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # Enter email and password in the login form
        email_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        email_field.send_keys(email)
        password_field.send_keys(password)

        # Click the 'Sign in' button
        sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        sign_in_button.click()

        # Wait for the homepage to load (we'll wait for the 'feed' element to load)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/feed/')]"))
        )

        print("Login successful.")
        return True

    except TimeoutException:
        print("Login failed: Timeout. Could not load the page or sign in.")
        return False

    except Exception as e:
        print(f"Login failed: {e}")
        return False
