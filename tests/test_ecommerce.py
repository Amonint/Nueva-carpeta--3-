import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

@pytest.fixture
def driver():
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--headless=new')
        
        # Get the ChromeDriver path and ensure it's the executable
        driver_path = ChromeDriverManager().install()
        driver_dir = os.path.dirname(driver_path)
        driver_exe = os.path.join(driver_dir, 'chromedriver.exe')
        
        if not os.path.exists(driver_exe):
            raise FileNotFoundError(f"ChromeDriver executable not found at {driver_exe}")
            
        print(f"Using ChromeDriver at: {driver_exe}")

        # Setup Chrome driver with specific options
        service = Service(executable_path=driver_exe)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {str(e)}")
        raise
    finally:
        if 'driver' in locals():
            driver.quit()

def test_search_product(driver):
    driver.get("http://localhost:5000")
    
    # Wait for page to load and search input to be present
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search-input"))
    )
    
    # Search for a product
    search_input.clear()
    search_input.send_keys("Laptop")
    
    # Wait for search results - look for card elements (not product-card)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "card"))
    )
    
    # Verify that products are displayed
    cards = driver.find_elements(By.CLASS_NAME, "card")
    assert len(cards) > 0

def test_add_to_cart(driver):
    driver.get("http://localhost:5000")
    
    # Wait for add to cart button and click it
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir al carrito')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(add_button).click().perform()
    
    # Verify cart count updated
    cart_count = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "cart-count"), "1")
    )
    assert cart_count

def test_update_cart_quantity(driver):
    driver.get("http://localhost:5000")
    
    # Add product to cart first
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir al carrito')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(add_button).click().perform()
    
    # Wait for cart to update and increase quantity button to appear
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "cart-count"), "1")
    )
    
    # Wait for increase quantity button and click it
    increase_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '+')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", increase_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(increase_button).click().perform()
    
    # Verify cart count updated to 2
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "cart-count"), "2")
    )

def test_checkout_process(driver):
    driver.get("http://localhost:5000")
    
    # Add product to cart
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir al carrito')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(add_button).click().perform()
    
    # Wait for cart to update
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "cart-count"), "1")
    )
    
    # Click checkout button
    checkout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Completar Compra')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", checkout_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(checkout_button).click().perform()
    
    # Handle the success alert
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    assert "Compra completada con éxito" in alert.text
    alert.accept()
    
    # Verify cart is empty after checkout
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "cart-count"), "0")
    )

def test_empty_cart_checkout(driver):
    driver.get("http://localhost:5000")
    
    # Try to checkout with empty cart
    checkout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Completar Compra')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", checkout_button)
    time.sleep(1)
    ActionChains(driver).move_to_element(checkout_button).click().perform()
    
    # Handle the alert
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    assert alert.text == "El carrito está vacío"
    alert.accept()
    
    # Verify cart count is still 0
    cart_count = driver.find_element(By.ID, "cart-count")
    assert cart_count.text == "0" 