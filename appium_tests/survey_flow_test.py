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

def login_with_email(email, password):
    driver = create_driver()
    wait = WebDriverWait(driver, 20)
    try:
        time.sleep(5)
        print("App loaded, starting email login test...")

        email_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your email or phone number"]')
        ))
        email_input.click()
        email_input.clear()
        email_input.send_keys(email)
        print("✅ Entered email")

        password_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your password"]')
        ))
        password_input.click()
        password_input.clear()
        password_input.send_keys(password)
        print("✅ Entered password")

        # Sign in button
        sign_in_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.Button[@content-desc="Sign in"]')
        ))
        sign_in_button.click()
        print("✅ Sign in button clicked!")

        # Wait for survey page to load
        time.sleep(5)
        return driver

    except Exception as e:
        print(f"❌ Email/password login test failed: {e}")
        try:
            print(driver.page_source)
        except:
            print("Could not get page source")
        driver.quit()
        return None

def test_survey(driver, name, birth_date, education, city, gender, ai_models_with_defects, beneficial_use_case) -> bool:
    wait = WebDriverWait(driver, 20)
    try:
        time.sleep(3)

        name_field = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Name-Surname *"]')
        name_field.click()
        name_field.send_keys(name)

        date_field = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Select Date"]')
        date_field.click()
        time.sleep(1)
        driver.press_keycode(66)

        education_dropdown = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Education Level *"]')
        education_dropdown.click()
        driver.find_element(By.XPATH, f'//android.widget.CheckedTextView[@text="{education}"]').click()

        city_field = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="City *"]')
        city_field.send_keys(city)

        driver.find_element(By.ACCESSIBILITY_ID, f'genderOption_{gender}').click()

        for model, defect in ai_models_with_defects.items():
            model_checkbox = driver.find_element(By.ACCESSIBILITY_ID, f'aiModel_{model}')
            model_checkbox.click()
            defect_input = driver.find_element(By.ACCESSIBILITY_ID, f'aiModelDefects_{model}')
            defect_input.send_keys(defect)

        use_case_field = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Beneficial Use Case of AI in Daily Life *"]')
        use_case_field.send_keys(beneficial_use_case)

        submit_button = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Send *"]')
        submit_button.click()

        time.sleep(2)
        success_snackbar = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//android.widget.TextView[contains(@text, "Survey submitted successfully")]')))
        print("✅ Survey submitted and success message shown")
        return True

    except Exception as e:
        print(f"❌ Survey test failed: {e}")
        try:
            print(driver.page_source)
        except:
            print("Could not get page source")
        return False
    finally:
        driver.quit()

# Run test
if __name__ == "__main__":
    driver = login_with_email("john@example.com", "pass123")
    if driver:
        result = test_survey(
            driver,
            name="Jane Doe",
            birth_date="2000-05-15",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
                "Copilot": "Overwrites code unexpectedly"
            },
            beneficial_use_case="I use AI to summarize news articles and speed up brainstorming."
        )

        if result:
            print("✅ Survey test passed!")
        else:
            print("❌ Survey test failed.")
