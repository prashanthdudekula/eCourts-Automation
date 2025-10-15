import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
print("WebDriver initialized successfully.")


stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32",
        webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
print("Stealth settings applied.")

try:

    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/")
    print("Navigated to eCourts website.")
    
    wait = WebDriverWait(driver, 20)
    
    print("Attempting to switch to iFrame 'main_S'...")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main_S")))
    print("Successfully switched to iFrame.")

    print("Attempting to find the state dropdown menu...")
    wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
    print("✅ Success! Found the state dropdown menu.")


except Exception as e:
    print("\n" + "="*50)
    print(f"❌ AN ERROR OCCURRED. Please copy ALL the text below:")
    print(e)
    print("="*50 + "\n")


finally:
    print("Script has ended. The browser will remain open for 5 minutes for debugging.")
    time.sleep(300)
    driver.quit()
    print("5 minutes are up. Browser is now closing.")
