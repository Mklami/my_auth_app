from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_driver():
    desired_caps = {
        "platformName": "Android",
        "platformVersion": "16",
        "deviceName": "emulator-5554",
        "appPackage": "com.example.my_auth_app",
        "appActivity": "com.example.my_auth_app.MainActivity",
        "automationName": "UiAutomator2",
        "noReset": True
    }
    options = UiAutomator2Options().load_capabilities(desired_caps)
    return webdriver.Remote("http://127.0.0.1:4723", options=options)

def verify_login_success(wait, driver):
    """Simplified verification that just checks for the survey page"""
    try:
        # Try to find the survey page header
        survey_header = wait.until(
            EC.presence_of_element_located((By.XPATH, '//android.view.View[@content-desc="AI Survey"]'))
        )
        print("✅ Login successful! Found AI Survey page.")
        return True
    except Exception as e:
        print(f"❌ Login verification failed: {e}")
        print("🪵 Page source for debug:")
        print(driver.page_source)
        return False

# ---------- Test Case 1: Test Login Button ----------
driver = create_driver()
wait = WebDriverWait(driver, 20)
try:
    time.sleep(3)
    test_login_button = wait.until(EC.element_to_be_clickable((By.ACCESSIBILITY_ID, "Login as Test User")))
    test_login_button.click()
    print("✅ Test login button clicked!")
    time.sleep(5)  # Wait for transitions
    verify_login_success(wait, driver)
except Exception as e:
    print(f"❌ Test login failed: {e}")
finally:
    driver.quit()