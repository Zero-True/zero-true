from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import time 

def test_app():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5173")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'codeCard')]")))

    code_cells = driver.find_elements(By.XPATH, "//div[contains(@id, 'codeCard')]")

    if not code_cells:
        print("No code cells found.")
        return

    for code_cell in code_cells:
        print(code_cell)
        cell_id = code_cell.get_attribute('id').replace('codeCard','')
        print(f"Found code cell with ID: {cell_id}")

        # Accessing elements inside the code cell
        elements = {
            "run_icon": driver.find_element(By.ID, f"runCode{cell_id}"),
            "delete_icon": driver.find_element(By.ID, f"deleteCell{cell_id}"),
            "codemirror": driver.find_element(By.ID, f"codeMirrorDev{cell_id}"),
            "cell_output": driver.find_element(By.ID, f"cellOutput{cell_id}")
            # Add other elements as needed
        }

        # Retrieve and verify code from CodeMirror
        codemirror = elements['codemirror']
        attributes = driver.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
            codemirror)

        print("Attributes of codemirror element:")
        for attr, value in attributes.items():
            print(f"{attr}: {value}")

        codemirror_input = WebDriverWait(codemirror, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f".cm-content"))
        )

        print("Attributes of codemirror CSS element:")
        for attr, value in attributes.items():
            print(f"{attr}: {value}")
        ActionChains(driver).move_to_element(codemirror_input).click().perform()
        print(codemirror_input.get_attribute("value"))
        codemirror_input.clear()  # Clear existing text if necessary
        codemirror_input.send_keys("Your new new complete text here")
        time.sleep(3)
        WebDriverWait(driver, 10,10)

        attributes = driver.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
            driver.find_element(By.ID, f"codeMirrorDev{cell_id}"))

        print("Attributes of codemirror element:")
        for attr, value in attributes.items():
            print(f"{attr}: {value}")


        # Send keys to the CodeMirror input element
        print(codemirror_input)

        #ActionChains(driver).move_to_element(codemirror_textarea).click().perform()


    driver.quit()

test_app()