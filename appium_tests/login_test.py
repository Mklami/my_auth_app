from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. Setup desired capabilities
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
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

# 2. Wait for app to load completely
time.sleep(5)

# 3. Find the login button by content-description
wait = WebDriverWait(driver, 20)
try:
    # In Appium, content-desc maps to the accessibility ID
    test_login_button = wait.until(EC.element_to_be_clickable(
        (By.ACCESSIBILITY_ID, "Login as Test User")))

    # Click the button
    test_login_button.click()
    print("✅ Test login button clicked!")

    # 4. Wait for the success screen to load
    time.sleep(3)

    # 5. Verify successful login
    try:
        success_message = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//android.widget.TextView[contains(@content-desc, "Welcome")]')))
        print("✅ Test login successful!")
    except Exception as e:
        print(f"❌ Login verification failed: {e}")
        print("Current page source:")
        print(driver.page_source)

except Exception as e:
    print(f"❌ Error finding or clicking login button: {e}")
    print("Current page source:")
    print(driver.page_source)

# 6. Quit driver
finally:
    driver.quit()