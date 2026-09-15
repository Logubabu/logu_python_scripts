from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import time

# Set up the web driver
# driver = webdriver.Chrome()
chrome_options = Options()
chrome_options.add_argument("log-level=3")  # disable logging
# chrome_options.add_argument("--headless")  # run in headless mode
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--ignore-ssl-errors")

PATH = r"D:/chromedriver.exe"
driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
driver.maximize_window()

# Navigate to YouTube and sign in
driver.get("https://www.youtube.com/")
# driver.get("https://www.youtube.com/feed/channels")

time.sleep(2)
driver.find_element(By.XPATH,"//*[@id='buttons']/ytd-button-renderer/yt-button-shape/a/yt-touch-feedback-shape/div/div[2]").click()
# sign_in_button = driver.find_element_by_xpath("//*[@id='buttons']/ytd-button-renderer/yt-button-shape/a/yt-touch-feedback-shape/div/div[2]")
# sign_in_button.click()
time.sleep(2)
email_input = driver.find_element(By.XPATH,"//input[@type='email']")
email_input.send_keys("pavichithra2121@gmail.com")
email_input.send_keys(Keys.RETURN)
time.sleep(10)
password_input = driver.find_element(By.XPATH,"//input[@type='password']")
password_input.send_keys("Pavi@0*9*9")
password_input.send_keys(Keys.RETURN)
time.sleep(2)
# driver.find_element(By.ID,"identifierId").send_keys("pavichithra2121@gmail.com")
# driver.find_element(By.ID,"identifierNext").click()
# time.sleep(2)  # wait for page to load
# driver.find_element(By.NAME,"password").send_keys("Pavi@0*9*9")
# driver.find_element(By.ID,"passwordNext").click()
# time.sleep(5)  

# Navigate to the subscriptions page
driver.get("https://www.youtube.com/feed/channels")

# Unsubscribe from each channel
while True:
    try:
        unsubscribe_buttons = driver.find_elements(By.XPATH,"//paper-button[@aria-label='Unsubscribe']")
        if len(unsubscribe_buttons) == 0:
            break
        unsubscribe_buttons[0].click()
        time.sleep(1)
        confirm_button = driver.find_element(By.XPATH,"//paper-button[@aria-label='Unsubscribe']")
        confirm_button.click()
        time.sleep(1)
    except:
        break

print("Unsubscribed from all channels.")

# Close the web driver
driver.quit()
