import pytest
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time 


notebook_str = '''notebookId = "08bdd530-3544-473b-af28-bb04f8646dbd"

[cells.57fbbd59-8f30-415c-87bf-8caae0374070]
cellType = "code"
code = """
import zero_true as zt
slider = zt.Slider(id='slide')
zt.TextInput(id='text')"""
'''

notebook_filename = "notebook.ztnb"

@pytest.fixture(scope="session", autouse=True)
def start_stop_app():
    # Start the application
    with open(notebook_filename,"w") as file:
        file.write(notebook_str)

    app_process = subprocess.Popen(["zero-true", "notebook"], cwd=os.getcwd())
    time.sleep(10)
    yield app_process

    # Stop the application
    app_process.terminate()
    app_process.wait()

@pytest.fixture(scope="session")
def driver():
    chrome_service = Service(ChromeDriverManager().install())

    options = Options()
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--headless")
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(service=chrome_service, options=options)
    yield driver
    driver.quit()


def find_element_attributes(driver,element):
    attributes = driver.execute_script(
    'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
    element)
    return attributes

def find_code_cells(driver):
    code_cells = driver.find_elements(By.XPATH, "//div[contains(@id, 'codeCard')]")
    return code_cells

def extract_code_cell_info(code_cell, driver):
    cell_info = {}

    cell_id = code_cell.get_attribute('id').replace('codeCard', '')

    # Accessing elements inside the code cell
    elements = {
        "run_icon": driver.find_element(By.ID, f"runCode{cell_id}"),
        "delete_icon": driver.find_element(By.ID, f"deleteCell{cell_id}"),
        "codemirror": driver.find_element(By.ID, f"codeMirrorDev{cell_id}"),
        "output_container": driver.find_element(By.ID,f"outputContainer_{cell_id}"),
        "cell_output": driver.find_element(By.ID, f"cellOutput{cell_id}"),
        "add_cell": driver.find_element(By.ID, f"addCell{cell_id}"),
    }

    # Retrieve and verify code from CodeMirror
    codemirror = elements['codemirror']
    attributes = find_element_attributes(driver,codemirror)
    
    code = attributes["code"]

    elements["codemirror_input"] = WebDriverWait(codemirror, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f".cm-content"))
    )

    # Storing information in the dictionary
    cell_info = {
        "cell_id": cell_id,
        "elements": elements,
        "code": code
    }

    return cell_info

def wait_for_load(driver):
    driver.get("http://localhost:1326")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'codeCard')]")))

def clear_codemirror_and_send_text(driver,codemirror_input,text):
    ActionChains(driver).move_to_element(codemirror_input).click().perform()
    codemirror_input.clear()  # Clear existing text if necessary
    codemirror_input.send_keys(text)
    time.sleep(3)

def wait_for_coderun(driver):
    # Wait for the code run 
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "codeRunProgress")))
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "codeRunProgress")))

def test_notebook_content(driver):
    
    print(os.getcwd())
    with open(notebook_filename,"r") as file:
        contents = file.read()

    assert contents==notebook_str, 'Notebook not properly saved'

def test_notebook_loading(driver):
    wait_for_load(driver)
    assert driver.find_element(By.ID, "appBar"), "Notebook did not load correctly."

def test_initial_code_cell(driver):
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 1 and code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found."

def test_intial_code_cell_content(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    expected_code = """
import zero_true as zt
slider = zt.Slider(id='slide')
zt.TextInput(id='text')"""
    assert cell_info['code'].strip() == expected_code.strip(), "Code in the cell does not match the expected code."

def test_initial_code_execution_and_output(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    run_icon = cell_info["elements"]["run_icon"]
    run_icon.click()
    wait_for_coderun(driver)
    assert cell_info["elements"]["output_container"].find_element(By.ID, "slide"), "Element with id 'slide' not found in output."
    assert cell_info["elements"]["output_container"].find_element(By.ID, "text"), "Element with id 'text' not found in output."


def test_adding_new_code_cell(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    add_icon = cell_info["elements"]["add_cell"]
    add_icon.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, f"addCell_Code_{cell_info['cell_id']}")))
    assert driver.find_element(By.ID, f"addCell_Code_{cell_info['cell_id']}"), "Add code cell below not found"
    add_code_cell = driver.find_element(By.ID,f"addCell_Code_{cell_info['cell_id']}")
    add_code_cell.click()
    time.sleep(4)
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 2 and code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found."



def test_execution_of_new_code_cell(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    new_cell_info =  extract_code_cell_info(code_cells[1],driver)
    slider = cell_info["elements"]["output_container"].find_element(By.CLASS_NAME,'v-slider-thumb')
    slider_value = slider.get_attribute("aria-valuenow")
    clear_codemirror_and_send_text(driver, new_cell_info["elements"]["codemirror_input"], "print(slider.value)")
    new_run_icon = new_cell_info["elements"]["run_icon"]
    new_run_icon.click()
    wait_for_coderun(driver)
    new_cell_output = new_cell_info["elements"]["cell_output"]
    assert new_cell_output.text == slider_value, "Output of new cell does not match slider value"


def test_slider_interaction(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    new_cell_info = extract_code_cell_info(code_cells[1],driver)
    slider = cell_info["elements"]["output_container"].find_element(By.CLASS_NAME,'v-slider-thumb')
    slider_value = slider.get_attribute("aria-valuenow")

    # Perform the drag-and-drop action
    if slider_value=='100':
        offset = -250
    else:
        offset = 250
    ActionChains(driver).drag_and_drop_by_offset(slider,offset, 0).release().perform()
    wait_for_coderun(driver)
    #get new output from parent cell 
    new_cell_output = new_cell_info["elements"]["cell_output"]

    slider_value = slider.get_attribute("aria-valuenow")
    time.sleep(2)
    #assert they are equal 
    assert new_cell_output.text == slider_value


def test_deletion_of_new_code_cell(driver):
    code_cells = find_code_cells(driver)
    new_cell_info =  extract_code_cell_info(code_cells[1],driver)
    new_cell_info["elements"]["delete_icon"].click()
    time.sleep(2)
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 1 and code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found."
