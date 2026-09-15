from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup WebDriver (Chromium-based example)
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")  # Disable notifications during login
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Login to Google account using Selenium
def login_to_google(driver, email, password):
    driver.get("https://accounts.google.com/signin/v2/identifier")
    
    # Wait for the email input field to load and enter the email
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)

    # Wait for the password input field to load and enter the password
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    # Wait for the login process to complete and the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[jsname='KjZuGd']"))  # Just a random check to confirm logged-in page load
    )
    time.sleep(3)  # Wait for a few seconds to ensure everything is loaded properly

# Navigate to Google Contacts and get contact names
def get_contacts(driver):
    driver.get("https://contacts.google.com/")
    time.sleep(5)  # Wait for contacts page to load

    # Assuming the contact names are in a div with class 'XXxk1b' (this may change)
    contact_elements = driver.find_elements(By.CSS_SELECTOR, '.XXxk1b')
    contacts = [contact.text for contact in contact_elements]

    return contacts

# Rename contacts by splitting and joining the names in reverse
def rename_contacts(contacts):
    renamed_contacts = []
    for contact in contacts:
        name_parts = contact.split()
        if len(name_parts) == 2:  # assuming first name and last name
            renamed_contact = " ".join(reversed(name_parts))
        else:
            renamed_contact = contact  # If no space in the name, leave it unchanged
        renamed_contacts.append(renamed_contact)
    return renamed_contacts

# Update contacts (optional, since it's not easily possible to update directly through UI)
def update_contacts(renamed_contacts):
    print("Renamed Contacts:")
    for name in renamed_contacts:
        print(name)

# Main function to orchestrate everything
def main():
    email = "loganathanrbl@gmail.com"  # Replace with your Google account email
    password = "Logu8799"      # Replace with your Google account password

    # Setup driver
    driver = setup_driver()

    try:
        # Step 1: Log in to Google
        login_to_google(driver, email, password)

        # Step 2: Get contacts
        contacts = get_contacts(driver)

        # Step 3: Rename contacts
        renamed_contacts = rename_contacts(contacts)

        # Step 4: Output renamed contacts
        update_contacts(renamed_contacts)

    finally:
        # Close the driver
        driver.quit()

if __name__ == '__main__':
    main()
