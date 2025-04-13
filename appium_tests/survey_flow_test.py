from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import unittest
import sys

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

def test_survey(driver, name, birth_date, education, city, gender, ai_models_with_defects, beneficial_use_case, valid) -> bool:
    WebDriverWait(driver, 20)
    # print(driver.page_source)

    time.sleep(2)

    print("Entering the name!")
    name_field = driver.find_element(By.XPATH, '//android.widget.EditText[@hint="Name-Surname *"]')
    name_field.click()
    time.sleep(2)
    name_field.send_keys(name)
    print("Done!")

    print("Trying the date field!")
    date_field = driver.find_element(By.XPATH, '''//android.view.View[@content-desc="Birth Date *
Select Date"]''')
    date_field.click()
    time.sleep(2)
    choose_date_field = driver.find_element(By.XPATH, f'''//android.widget.Button[@content-desc="{birth_date}"]''')
    choose_date_field.click()
    time.sleep(2)
    ok_date_field = driver.find_element(By.XPATH, f'''//android.widget.Button[@content-desc="OK"]''')
    ok_date_field.click()
    time.sleep(2)
    print("Done!")


    print("Choosing the education level!")
    education_dropdown = driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Education Level *"]')
    education_dropdown.click()
    time.sleep(2)
    education_choice = driver.find_element(By.XPATH, f'''//android.widget.Button[@content-desc="{education}"]''')
    education_choice.click()
    print("Done!")

    time.sleep(2)

    print("Trying the city field!")
    city_field = driver.find_element(By.XPATH, '//android.widget.ScrollView/android.widget.EditText[2]')
    city_field.click()
    time.sleep(2)
    city_field.send_keys(city)
    print("Done!")

    time.sleep(2)

    print("Prefer not to say!")
    gender_field = driver.find_element(By.XPATH, f'//android.widget.RadioButton[@content-desc="{gender}"]')
    gender_field.click()
    print("Done!")

    time.sleep(2)

    print("Swipe!")
    driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=300, duration=800)
    print("Swipe Done!")

    time.sleep(2)

    print("AI Models!")
    count = 1
    for model, defect in ai_models_with_defects.items():
        model_checkbox = driver.find_element(By.XPATH, f'''//android.widget.CheckBox[@content-desc="{model}"]''')
        model_checkbox.click()
        time.sleep(2)
        print("Swipe!")
        driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=300, duration=800)
        print("Swipe Done!")
        time.sleep(2)
        defect_input = driver.find_element(By.XPATH, f'''//android.widget.ScrollView/android.widget.EditText[{str(count)}]''')
        defect_input.click()
        time.sleep(2)
        defect_input.send_keys(defect)
        count += 1

    print("Done!")

    print("Benefits!")
    use_case_field = driver.find_element(By.XPATH,  f'''//android.widget.ScrollView/android.widget.EditText[{str(count)}]''')
    use_case_field.click()
    time.sleep(2)
    use_case_field.send_keys(beneficial_use_case)
    print("Done!")

    time.sleep(2)

    print("Send Button!")
    print("Swipe!")
    driver.swipe(start_x=800, start_y=1800, end_x=800, end_y=800, duration=800)
    print("Swipe Done!")
    submit_exists = True
    try:
        submit_button = driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Send"]')
        submit_button.click()
    except:
        submit_exists = False
    return (valid and submit_exists) == (valid or submit_exists)


class AISurveyTests(unittest.TestCase):

    def setUp(self):
        self.driver = login_with_email("john@example.com", "pass123")
        self.assertTrue(self.driver is not None, "Login failed, cannot proceed with tests")
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_comprehensive_text_fields_validation(self):
        """
        TC1: Comprehensive Text Fields Validation

        This test validates all text-based fields (Name-Surname, City, and Beneficial Use Case)
        under multiple conditions to ensure proper validation behavior.
        """
        print("\n======= RUNNING TEST CASE 1: Comprehensive Text Fields Validation =======")
        print("\nStep 1: Testing empty name with all other fields valid")

        result1 = test_survey(
            self.driver,
            name="",  # Empty name should trigger validation
            birth_date="15, Monday, January 15, 1990",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=False  # We expect form validation to fail
        )
        self.assertTrue(result1, "Empty name validation failed")

        print("\nLogging out for next step")
        logout_success = logout_from_survey_page(self.driver, self.wait)
        self.assertTrue(logout_success, "Failed to logout between test steps")
        # Re-login for the next test
        login_with_email("john@example.com", "pass123")

        print("\nStep 2: Testing valid name but empty city")
        result2 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="15, Monday, January 15, 1990",
            education="Bachelor's Degree",
            city="",  # Empty city should trigger validation
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=False  # We expect form validation to fail
        )
        self.assertTrue(result2, "Empty city validation failed")

        print("\nLogging out for next step")
        logout_success = logout_from_survey_page(self.driver, self.wait)
        self.assertTrue(logout_success, "Failed to logout between test steps")
        # Re-login for the next test
        login_with_email("john@example.com", "pass123")

        print("\nStep 3: Testing empty beneficial use case")
        result3 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="",  # Empty use case should trigger validation
            valid=False  # We expect form validation to fail
        )
        self.assertTrue(result3, "Empty beneficial use case validation failed")

        print("\nLogging out for final step")
        logout_success = logout_from_survey_page(self.driver, self.wait)
        self.assertTrue(logout_success, "Failed to logout between test steps")
        # Re-login for the next test
        login_with_email("john@example.com", "pass123")

        print("\nStep 4: Testing all valid text fields")
        result4 = test_survey(
            self.driver,
            name="Jane Doe",  # Valid name
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",  # Valid city
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="AI helps me with tasks",  # Valid use case
            valid=True  # We expect form to be valid
        )
        self.assertTrue(result4, "Valid text fields test failed")

    def test_birth_date_selection_validation(self):
        """
        TC2: Birth Date Selection and Format Validation

        This test validates the birth date field functionality, including
        selection behaviors and validation for past dates and future dates.
        """
        print("\n======= RUNNING TEST CASE 2: Birth Date Selection and Format Validation =======")

        print("\nStep 1: Testing with a valid past birth date")
        result1 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="15, Monday, January 15, 1990",  # Valid past date
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result1, "Valid past birth date test failed")

        print("\nLogging out for next step")
        logout_success = logout_from_survey_page(self.driver, self.wait)
        self.assertTrue(logout_success, "Failed to logout between test steps")
        # Re-login for the next test
        login_with_email("john@example.com", "pass123")

        print("\nStep 2: Testing with a future date (should be invalid)")
        result2 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",  # Future date - should be invalid
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=False  # Expecting validation to fail with future date
        )
        self.assertTrue(result2, "Future birth date validation test failed")

        # Note: To actually implement this test case properly, the survey app would need to
        # validate dates and prevent future dates from being selected

    def test_dropdown_radio_button_validation(self):
        """
        TC3: Dropdown and Radio Button (Education & Gender) Validation

        This test verifies the functionality of both the Education Level dropdown
        and the Gender radio button selections.
        """
        print("\n======= RUNNING TEST CASE 3: Dropdown and Radio Button Validation =======")

        print("\nStep 1: Testing with valid education but different gender selection")
        result1 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Male",  # Testing different gender selection
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result1, "Valid gender selection test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 2: Testing with different education level")
        result2 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Master's Degree",  # Different education level
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result2, "Alternative education selection test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 3: Testing with 'Prefer not to say' gender option")
        result3 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Prefer not to say",  # Testing third gender option
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result3, "'Prefer not to say' gender option test failed")

    def test_ai_models_defect_validation(self):
        """
        TC4: AI Models Multi-Selection and Dependent Defect Entry Validation

        This test verifies the AI model selection functionality and associated
        defect entry fields, ensuring proper dependency validation.
        """
        print("\n======= RUNNING TEST CASE 4: AI Models and Defect Validation =======")

        print("\nStep 1: Testing with single AI model selection")
        result1 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",  # Single model
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result1, "Single AI model test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 2: Testing with multiple AI model selections")
        result2 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
                "Copilot": "Overwrites code unexpectedly",
                "Claude": "Occasionally lacks context awareness"
            },  # Multiple models
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result2, "Multiple AI models test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 3: Testing with empty defect for a selected model")
        result3 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "",  # Empty defect should trigger validation
                "Copilot": "Overwrites code unexpectedly"
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=False
        )
        self.assertTrue(result3, "Empty defect validation failed")

    def test_end_to_end_combinations(self):
        """
        TC5: End-to-End Parameterized Multi-Field Submission Test

        This test executes an end-to-end validation with different combinations
        of inputs to verify form validation in a comprehensive manner.
        """
        print("\n======= RUNNING TEST CASE 5: End-to-End Input Combinations =======")

        print("\nStep 1: Testing with all valid fields (complete submission)")
        result1 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
                "Copilot": "Overwrites code unexpectedly"
            },
            beneficial_use_case="I use AI to summarize news articles and enhance productivity.",
            valid=True
        )
        self.assertTrue(result1, "Complete valid submission test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 2: Testing with minimal valid data")
        result2 = test_survey(
            self.driver,
            name="J",  # Minimal name
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="A",  # Minimal city
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Limited"  # Minimal defect description
            },
            beneficial_use_case="Helps",  # Minimal use case
            valid=True
        )
        self.assertTrue(result2, "Minimal valid data test failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 3: Testing with exceptionally long text inputs")
        long_text = "A" * 1000  # Very long string
        result3 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Normal defect",
            },
            beneficial_use_case=long_text,  # Extremely long use case
            valid=True  # Most forms should handle this, but could fail if there's a max length
        )
        self.assertTrue(result3, "Long text input test failed")

        print("\nRefreshing for final step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        print("\nStep 4: Testing with special characters in text fields")
        special_chars = "!@#$%^&*()_+<>?:\"{}|[];',./`~"
        result4 = test_survey(
            self.driver,
            name="Jane" + special_chars,
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara" + special_chars,
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Defect " + special_chars,
            },
            beneficial_use_case="Use case " + special_chars,
            valid=True  # Most forms should accept special chars, but some may validate against them
        )
        self.assertTrue(result4, "Special characters test failed")

    def test_form_interconnected_validations(self):
        """
        TC6: Form Interconnected Field Validations

        This test examines how changes in one field affect the validation state
        of other fields, focusing on interdependencies in the form.
        """
        print("\n======= RUNNING TEST CASE 6: Form Interconnected Field Validations =======")

        print("\nStep 1: Testing valid form then modifying it to invalid state")
        # First create a valid form state
        result1 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                "ChatGPT": "Sometimes gives outdated info",
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=True
        )
        self.assertTrue(result1, "Initial valid form state failed")

        print("\nRefreshing for next step")
        self.driver.quit()
        self.driver = login_with_email("john@example.com", "pass123")

        # Now test if turning off the AI model selection affects validation
        print("\nStep 2: Testing AI model dependencies with beneficial use case")
        result2 = test_survey(
            self.driver,
            name="Jane Doe",
            birth_date="4, Friday, April 4, 2025",
            education="Bachelor's Degree",
            city="Ankara",
            gender="Female",
            ai_models_with_defects={
                # Empty dict - no AI models selected
            },
            beneficial_use_case="I use AI to summarize news articles.",
            valid=False  # Form should be invalid with no AI models selected
        )
        self.assertTrue(result2, "AI model dependency validation failed")


# Run the tests
if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)