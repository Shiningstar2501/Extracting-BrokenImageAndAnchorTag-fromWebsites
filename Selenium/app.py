from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

# Initialize WebDriver using the Service object
driver = webdriver.Chrome(service=service)

# Open the webpage
driver.get('https://bagmails.com')

# Quit the driver after the task is done
driver.quit()