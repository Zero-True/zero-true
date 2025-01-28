import pytest
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time 
import uuid


notebook_id = str(uuid.uuid4())


# Define the expected Python code for the notebook
notebook_content = f"""
import zero_true as zt
import time

def cell_57fbbd59_8f30_415c_87bf_8caae0374070():
    time.sleep(2)
    slider = zt.Slider(id='slide')
    zt.TextInput(id='text')

notebook = zt.notebook(
    id="{notebook_id}",
    name="Zero True",
    cells=[
        zt.cell(cell_57fbbd59_8f30_415c_87bf_8caae0374070, type="code")
    ]
)
"""

notebook_filename = "notebook.py"

@pytest.fixture(scope="session", autouse=True)
def start_stop_app():
    # Start the application
    with open(notebook_filename,"w") as file:
        file.write(notebook_str)

    app_process = subprocess.Popen(["zero-true", "notebook", "--remote"], cwd=os.getcwd())
    time.sleep(10)
    yield app_process

    # Stop the application
    app_process.terminate()
    app_process.wait()

@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--headless")
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--window-size=1920,1080')  

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def find_element_attributes(driver,element):
    attributes = driver.execute_script(
    'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
    element)
    return attributes

def find_code_cells(driver):
    WebDriverWait(driver, 100).until(
    EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'codeCard')]"))
    )
    code_cells = driver.find_elements(By.XPATH, "//div[contains(@id, 'codeCard')]")
    return code_cells

def find_el_by_id_w_exception(driver,element_id):
    try:
        element = driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        print(element_id + " not found")
        element = None
    return element

def extract_code_cell_info(code_cell, driver,mode='notebook'):
    cell_info = {}
    cell_id = code_cell.get_attribute('id').replace('codeCard', '')
    print('cell_id',cell_id)
    print('mode',mode)
    # Accessing elements inside the code cell
    elements = {
        "run_icon": find_el_by_id_w_exception(driver, f"runCode{cell_id}",),
        "cell_toolbar": find_el_by_id_w_exception(driver, f"cellToolbar{cell_id}"),
        "codemirror": find_el_by_id_w_exception(driver, f"codeMirrorDev{cell_id}"),
        "codemirror_app": find_el_by_id_w_exception(driver, f"codeMirrorApp{cell_id}"),
        "output_container": find_el_by_id_w_exception(driver,f"outputContainer_{cell_id}"),
        "cell_output": find_el_by_id_w_exception(driver, f"cellOutput{cell_id}"),
        "add_cell": find_el_by_id_w_exception(driver, f"addCell{cell_id}"),
        "cell_id": cell_id
    }

    # Retrieve and verify code from CodeMirror
    if mode == 'notebook':
        codemirror = elements['codemirror']
        print(codemirror)
    else:
        codemirror = find_el_by_id_w_exception(driver, f"codeMirrorApp{cell_id}")
        print(find_el_by_id_w_exception(driver, f"codeMirrorApp{cell_id}"))

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
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'codeCard')]")))

def clear_codemirror_and_send_text(driver,codemirror_input,text):
    ActionChains(driver).move_to_element(codemirror_input).click().perform()
    codemirror_input.clear()  # Clear existing text if necessary
    codemirror_input.send_keys(text)
    time.sleep(3)

def wait_for_coderun(driver):
    # Wait for the code run 
    WebDriverWait(driver, 800).until(
        EC.presence_of_element_located((By.ID, "codeRunProgress")))
    WebDriverWait(driver, 800).until(
        EC.invisibility_of_element_located((By.ID, "codeRunProgress")))

def test_notebook_content(driver):
    with open(notebook_filename,"r") as file:
        contents = file.read()

    print(contents)
    print(notebook_str)
    assert contents==notebook_str, 'Notebook not properly saved'

def test_notebook_loading(driver):
    wait_for_load(driver)
    assert driver.find_element(By.ID, "appBar"), "Notebook did not load correctly."

def test_initial_code_cell(driver):
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 1 and code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found."

def test_intial_code_cell_content(driver):
    code_cells = find_code_cells(driver)
    print('code cells',code_cells)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    print(cell_info)
    assert cell_info['code'].strip() == expected_code.strip(), "Code in the cell does not match the expected code."

def test_initial_code_execution_and_output(driver):
    code_cells = find_code_cells(driver)
    code_cells[0].click
    cell_info = extract_code_cell_info(code_cells[0],driver)
    run_icon = cell_info["elements"]["run_icon"]
    run_icon.click()
    wait_for_coderun(driver)
    time.sleep(6)
    cell_info = extract_code_cell_info(code_cells[0],driver)
    assert cell_info["elements"]["output_container"].find_element(By.ID, "slide"), "Element with id 'slide' not found in output."
    assert cell_info["elements"]["output_container"].find_element(By.ID, "text"), "Element with id 'text' not found in output."


def test_adding_new_code_cell(driver):
    # Find initial code cells
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0], driver)
    
    # Find and trigger the add cell button
    activator_area = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#addCell{cell_info['cell_id']}")
    ))
    
    # Make the container visible
    driver.execute_script("""
        arguments[0].style.height = '24px';
        arguments[0].querySelector('.divider-container').style.opacity = '1';
        var btn = arguments[0].querySelector('.divider__btn');
        btn.style.opacity = '1';
        btn.style.visibility = 'visible';
        btn.style.pointerEvents = 'auto';
    """, activator_area)
    
    driver.execute_script("arguments[0].offsetHeight;", activator_area)
    
    add_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#addCell{cell_info['cell_id']} .v-btn.divider__btn"))
    )
    
    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
    driver.execute_script("arguments[0].click();", add_button)
    
    add_code_cell = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, f"addCell_Code_{cell_info['cell_id']}"))
    )
    add_code_cell.click()
    
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 2, "New code cell was not added"
    assert code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found"

def test_execution_of_new_code_cell(driver):
    code_cells = find_code_cells(driver)
    cell_info = extract_code_cell_info(code_cells[0], driver)
    new_cell_info = extract_code_cell_info(code_cells[1], driver)
    
    # Get slider value from first cell
    slider = cell_info["elements"]["output_container"].find_element(By.CLASS_NAME, 'v-slider-thumb')
    slider_value = slider.get_attribute("aria-valuenow")
    
    # Prepare the code to execute
    new_code = f"""
time.sleep(2)
print(slider.value)"""
    
    # Focus the new cell to make header visible
    new_cell = code_cells[1]
    driver.execute_script("""
        // Trigger mouseenter event to show header
        var event = new MouseEvent('mouseenter', {
            'view': window,
            'bubbles': true,
            'cancelable': true
        });
        arguments[0].dispatchEvent(event);
    """, new_cell)
    
    # Wait for header to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, f"#codeCard{new_cell_info['cell_id']} .header"))
    )
    
    # Input the code
    clear_codemirror_and_send_text(driver, new_cell_info["elements"]["codemirror_input"], new_code)
    
    # Find and click run button
    run_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"#runCode{new_cell_info['cell_id']}"))
    )
    driver.execute_script("arguments[0].click();", run_button)
    
    # Wait for execution
    wait_for_coderun(driver)
    time.sleep(10)
    
    # Verify output
    new_cell_info = extract_code_cell_info(code_cells[1], driver)
    new_cell_output = new_cell_info["elements"]["cell_output"]
    
    assert new_cell_output.text.strip() == str(slider_value).strip(), (
        f"\nOutput mismatch:"
        f"\nActual output: '{new_cell_output.text}'"
        f"\nExpected output: '{slider_value}'"
    )

def test_slider_interaction(driver):
    code_cells = find_code_cells(driver)
    
    # Click first cell to focus it
    code_cells[0].click()
    time.sleep(2)  # Wait for focus
    
    slider = code_cells[0].find_element(By.CLASS_NAME,'v-slider-thumb')
    slider_value = slider.get_attribute("aria-valuenow")

    # Move slider
    offset = -250 if slider_value == '100' else 250
    ActionChains(driver).drag_and_drop_by_offset(slider, offset, 0).perform()
    
    # Click second cell to focus it
    code_cells[1].click()
    
    time.sleep(6)  # Wait for execution
    
    # Get output
    new_cell_info = extract_code_cell_info(code_cells[1], driver)
    new_cell_output = new_cell_info["elements"]["cell_output"]
    
    # Verify
    assert new_cell_output.text == slider.get_attribute("aria-valuenow")
def test_app_mode(driver):
    #hide the second code cell
    code_cells = find_code_cells(driver)
    code_cells[1].click()
    new_cell_info =  extract_code_cell_info(code_cells[1],driver)
    new_cell_info["elements"]["cell_toolbar"].click()
    WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.ID, f"hideCell{new_cell_info['cell_id']}")))
    hide_btn = driver.find_element(By.ID,f"hideCellSwitch{new_cell_info['cell_id']}")
    hide_btn.click()
    time.sleep(6)

    #find app mode button by id 
    app_mode_btn = driver.find_element(By.ID, "appBtn")
    app_mode_btn.click()
    
    #wait for the app mode to load
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    
    driver.get("http://localhost:1326/app")

    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    #test whether code cell is editable in app mode
    code_cells = find_code_cells(driver)
    code_cells[0].click()

    #assert that there is only cell in app mode because the second cell was hidden

    cell_id_0 = '57fbbd59-8f30-415c-87bf-8caae0374070'

    assert len(code_cells) == 1 and code_cells[0].get_attribute('id') == f'codeCard{cell_id_0}', "Expected code cell not found."

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, f"codeMirrorAppTitle{cell_id_0}")))
    expansion_panel_title = driver.find_element(By.ID, f"codeMirrorAppTitle{cell_id_0}")
    expansion_panel_title.click()
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, f"codeMirrorApp{cell_id_0}")))

    cell_info = extract_code_cell_info(code_cells[0],driver,mode='app')

    

    codemirror_input = cell_info["elements"]["codemirror_input"]
    clear_codemirror_and_send_text(driver, codemirror_input, "print('Hello World')")

    #check that the code has not chenged since before the clear_codemirror_and_send_text call
    #and that it matches the expected code
    code_cells = find_code_cells(driver)
    code_cells[0].click()
    cell_info = extract_code_cell_info(code_cells[0],driver, mode='app')
    assert cell_info['code'].strip() == expected_code.strip(), "Code in the cell does not match the expected code."
    
    #find notebook mode button by id
    dev_mode_btn = driver.find_element(By.ID, "notebookBtn")
    dev_mode_btn.click()

    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "appBar")))

    driver.get("http://localhost:1326")


def test_deletion_of_new_code_cell(driver):
    driver.get("http://localhost:1326")
    code_cells = find_code_cells(driver)
    new_cell_info =  extract_code_cell_info(code_cells[1],driver)
    new_cell_info["elements"]["cell_toolbar"].click()
    WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.ID, f"deleteCell{new_cell_info['cell_id']}")))
    delete_btn = driver.find_element(By.ID,f"deleteCell{new_cell_info['cell_id']}")
    delete_btn.click()
    time.sleep(2)
    code_cells = find_code_cells(driver)
    assert len(code_cells) == 1 and code_cells[0].get_attribute('id') == 'codeCard57fbbd59-8f30-415c-87bf-8caae0374070', "Expected code cell not found."

# test hiding code cell

# test hiding code but not output

# test typing in app mode 

# test different cell types?

