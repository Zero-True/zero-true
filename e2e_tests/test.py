from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

def test_app():
    driver = webdriver.Chrome()
    driver.get("http://localhost:1326")

    # Access the 'app' element
    app_element = driver.find_element(By.ID, 'app')

    # Find all child elements within 'app'
    # You can change By.TAG_NAME to another selector if needed
    child_elements = app_element.find_elements(By.XPATH, ".//*")

    for element in child_elements:
        # Print tag name and other attributes of the child element
        print(f"Tag: {element.tag_name}, ID: {element.get_attribute('id')}")

    driver.quit()

test_app()