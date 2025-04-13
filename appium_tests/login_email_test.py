from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_driver():
    """Sets up and returns the Appium driver with appropriate capabilities"""
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
    """Verifies login by checking for the AI Survey page"""
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

def dismiss_password_manager(driver):
    """Attempts to dismiss password manager popups"""
    try:
        # Look for the "Never" or "Not now" button on the popup
        never_buttons = driver.find_elements(By.XPATH,
            '//*[@text="Never" or @text="Not now" or @text="Cancel" or @content-desc="Never" or @content-desc="Not now" or @content-desc="Cancel"]')

        if never_buttons:
            never_buttons[0].click()
            print("✅ Dismissed password manager popup")
            time.sleep(1)  # Wait for dismissal animation
            return True
    except Exception as e:
        print(f"Could not dismiss popup: {e}")

    return False

def test_email_login():
    """Tests the email/password login functionality"""
    driver = create_driver()
    wait = WebDriverWait(driver, 20)

    try:
        # Wait longer for app to fully load and stabilize
        time.sleep(5)
        print("App loaded, starting email login test...")


         # Find email input field by hint text
        email_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your email or phone number"]')
        ))
        email_input.click()
        email_input.clear()
        email_input.send_keys("john@example.com")
        print("✅ Entered email")

        # Find password input field by hint text
        password_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your password"]')
        ))
        password_input.click()
        password_input.clear()
        password_input.send_keys("pass123")
        print("✅ Entered password")

        # Ensure app is still in foreground
        #driver.activate_app("com.example.my_auth_app")
        #time.sleep(1)

        # Hide keyboard with back button instead of API call
        #driver.press_keycode(4)  # Back key
        #time.sleep(1)

        # Check if we're still in the app
        if driver.current_activity != ".MainActivity":
            print(f"⚠️ App activity changed to: {driver.current_activity}")
            driver.activate_app("com.example.my_auth_app")
            time.sleep(2)

        # Find and click sign in button with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                sign_in_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//android.widget.Button[@content-desc="Sign in"]')
                ))
                sign_in_button.click()
                print("✅ Sign in button clicked!")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt+1}/{max_retries} clicking sign in button...")
                    driver.activate_app("com.example.my_auth_app")
                    time.sleep(2)
                else:
                    print(f"❌ Failed to click sign in button after {max_retries} attempts: {e}")
                    return False

        # Wait for results
        time.sleep(5)

        # Verify login success
        try:
            if "AI Survey" in driver.page_source:
                print("✅ Login successful! Found AI Survey page.")
                return True
            else:
                print("❌ Not on survey page after login attempt")
                print("Page source:")
                print(driver.page_source)
                return False
        except Exception as e:
            print(f"❌ Error verifying login success: {e}")
            return False

    except Exception as e:
        print(f"❌ Email/password login test failed: {e}")
        try:
            print(driver.page_source)
        except:
            print("Could not get page source")
        return False
    finally:
        driver.quit()

def test_invalid_credentials():
    """Test various incorrect login scenarios with a simplified, robust approach."""
    # Define test cases
    test_cases = [
        {"identifier": "random@example.com", "password": "pass123", "label": "Invalid email"},
        {"identifier": "5333333333", "password": "1231234321", "label": "Invalid phone"},
        {"identifier": "john@example.com", "password": "1231234321", "label": "Wrong password"},
        {"identifier": "", "password": "1231234321", "label": "Empty email/phone"},
        {"identifier": "john@example.com", "password": "", "label": "Empty password"},
        {"identifier": "john-example.com", "password": "pass123", "label": "Malformed email"},
        {"identifier": "53a1234567", "password": "pass123", "label": "Malformed phone"}
    ]

    # Results tracking
    results = []

    email_field = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//android.widget.EditText[@hint="Enter your email or phone number"]')
    ))
    password_field = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//android.widget.EditText[@hint="Enter your password"]')
    ))
    login_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//android.widget.Button[@content-desc="Sign in"]')
    ))

    # Run each test independently
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 TEST {i+1}: {test_case['label']}")

        # Clear & type identifier
        email_field.click()
        time.sleep(0.5)
        email_field.clear()
        email_field.send_keys(test_case["identifier"])
        time.sleep(0.5)

        # Clear & type password
        password_field.click()
        time.sleep(0.5)
        password_field.clear()
        password_field.send_keys(test_case["password"])
        time.sleep(0.5)

        # Submit
        login_button.click()
        print("➡️ Login attempted")
        time.sleep(3)

        # Check if login form is still present (failure expected)
        login_still_there = driver.find_elements(By.XPATH, '//android.widget.Button[@content-desc="Sign in"]')
        if login_still_there:
            print("✅ PASS: Login prevented as expected")
            results.append(True)
        else:
            print("❌ FAIL: Possibly logged in or screen changed")
            results.append(False)

    driver.quit()

    print("\n📊 Summary:")
    for i, result in enumerate(results):
        print(f"Test {i+1}: {'✅ PASS' if result else '❌ FAIL'} - {test_cases[i]['label']}")



def logout_from_survey_page(driver, wait):
    """Clicks the logout button to return to the login screen."""
    try:
        logout_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//android.view.View[@content-desc="Logout Button"]/android.widget.Button'))
        )
        logout_button.click()
        print("🔚 Logged out successfully")
        time.sleep(3)  # Let the login screen load
        return True
    except Exception as e:
        print(f"⚠️ Logout failed: {e}")
        print("🪵 Page source:")
        print(driver.page_source)
        return False


if __name__ == "__main__":
    print("Starting Email/Password Login Test...")
    result = test_email_login()
    if result:
        print("✅ Email/Password Login Test: PASSED")

        driver = create_driver()
        wait = WebDriverWait(driver, 20)

        print("🔄 Attempting to log out...")
        if logout_from_survey_page(driver, wait):
            print("🚪 Proceeding with Invalid Credentials Corner Case Test...")
            test_invalid_credentials()
        else:
            print("❌ Could not log out. Skipping invalid credentials test.")
    else:
        print("❌ Email/Password Login Test: FAILED")

