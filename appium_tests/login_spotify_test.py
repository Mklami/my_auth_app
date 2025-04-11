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
        "noReset": True,
        "autoGrantPermissions": True,  # Auto grant permissions for browser redirects
        "chromedriverExecutable": "/path/to/chromedriver"  # Optional: path to chromedriver if needed
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

def handle_webview_auth(driver, wait):
    """Handle Spotify OAuth webview authentication flow"""
    try:
        # Wait for webview to load
        print("Waiting for webview to load...")
        time.sleep(5)

        # Get available contexts
        contexts = driver.contexts
        print(f"Available contexts: {contexts}")

        # Switch to webview context if available
        for context in contexts:
            if "WEBVIEW" in context:
                driver.switch_to.context(context)
                print(f"Switched to context: {context}")

                # Wait for Spotify login elements
                wait.until(EC.presence_of_element_located((By.ID, "login-username")))

                # Enter Spotify credentials (replace with test account)
                driver.find_element(By.ID, "login-username").send_keys("test_spotify_user@example.com")
                driver.find_element(By.ID, "login-password").send_keys("test_password")
                driver.find_element(By.ID, "login-button").click()

                # Wait for authorization page and accept
                try:
                    wait.until(EC.element_to_be_clickable((By.ID, "auth-accept"))).click()
                except:
                    print("No authorization confirmation needed or different element ID")

                # Switch back to native context
                driver.switch_to.context("NATIVE_APP")
                return True

        print("No webview context found, remaining in native context")
        return False

    except Exception as e:
        print(f"⚠️ Webview handling error: {e}")
        # Make sure we're back in native context
        try:
            driver.switch_to.context("NATIVE_APP")
        except:
            pass
        return False

def test_spotify_login():
    """Tests the Spotify login functionality"""
    driver = create_driver()
    wait = WebDriverWait(driver, 20)

    try:
        # Wait for app to load completely
        time.sleep(5)
        print("App loaded, starting Spotify login test...")

        # Find and click the Spotify button
        spotify_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.Button[@content-desc="Continue with Spotify"]')
        ))
        spotify_button.click()
        print("✅ Spotify button clicked!")

        # Handle the webview authentication flow
        webview_handled = handle_webview_auth(driver, wait)

        # Regardless of webview handling success, wait for results
        # Since this is a challenging flow to automate, we'll give it extra time
        time.sleep(10)

        # Check if we've returned to our app and successfully logged in
        # We might land directly at the survey page after OAuth completes
        current_package = driver.current_package
        print(f"Current package: {current_package}")

        if current_package != "com.example.my_auth_app":
            print("⚠️ Not in our app after authentication flow")
            driver.activate_app("com.example.my_auth_app")
            time.sleep(5)

        # Verify login success
        return verify_login_success(wait, driver)

    except Exception as e:
        print(f"❌ Spotify login test failed: {e}")
        print("Page source at failure (if available):")
        try:
            print(driver.page_source)
        except:
            print("Could not get page source")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starting Spotify Login Test...")
    result = test_spotify_login()
    if result:
        print("✅ Spotify Login Test: PASSED")
    else:
        print("❌ Spotify Login Test: FAILED")