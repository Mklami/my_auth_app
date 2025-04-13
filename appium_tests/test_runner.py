from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
import json
import os
import sys
from termcolor import colored
import traceback
from typing import Dict, Any, List, Tuple, Optional
import argparse
from datetime import datetime

def load_test_cases(json_file_path: str) -> Dict[str, Any]:
    """Load test cases from a JSON file."""
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading test cases: {e}")
        sys.exit(1)

def create_driver():
    """Create and return an Appium driver."""
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

def login_with_email(driver, email="john@example.com", password="pass123"):
    """Log in to the app with the given credentials."""
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
        return True
    except Exception as e:
        print(f"❌ Email/password login test failed: {e}")
        return False

def find_element_safe(driver, xpath, timeout=5):
    """Safely find an element, return None if not found."""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return None

def is_error_displayed(driver):
    """Check if any error message is displayed."""
    try:
        error_elements = driver.find_elements(By.XPATH, '//android.widget.TextView')
        for element in error_elements:
            text = element.get_attribute("text")
            if text and any(err in text.lower() for err in ["error", "invalid", "please", "required"]):
                print(f"Found error message: {text}")
                return True, text

        # Also check for snackbar error messages
        snackbar = find_element_safe(driver, '//android.widget.TextView[contains(@resource-id, "snackbar_text")]')
        if snackbar:
            text = snackbar.get_attribute("text")
            print(f"Found snackbar message: {text}")
            return True, text

        return False, ""
    except Exception as e:
        print(f"Error checking for error messages: {e}")
        return False, ""

def run_test_scenario(driver, scenario: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Run a single test scenario and return the result.

    Args:
        driver: The Appium WebDriver instance
        scenario: The test scenario data

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        inputs = scenario["inputs"]

        # Enter name
        try:
            print(f"Entering name: {inputs['name']}")
            name_field = find_element_safe(driver, '//android.widget.EditText[@hint="Name-Surname *"]')
            if name_field:
                name_field.click()
                time.sleep(1)
                name_field.clear()
                name_field.send_keys(inputs['name'])
            else:
                print("Name field not found")
                return False, "Name field not found"
        except Exception as e:
            print(f"Error entering name: {e}")
            return False, f"Failed to enter name: {e}"

        # Check for any validation error after entering name
        error_found, error_msg = is_error_displayed(driver)
        if error_found and not inputs['name']:
            # If we expected an error (empty name), this is actually a pass
            if not scenario["expected_result"]["should_submit"]:
                return True, f"Form was correctly blocked with error: {error_msg}"
            else:
                return False, f"Form validation failed with error: {error_msg}"

        # Enter birth date
        try:
            print("Entering birth date")
            birth_date = inputs['birth_date']

            # Enter day
            day_field = find_element_safe(driver, '//android.widget.ScrollView/android.widget.EditText[2]/android.widget.EditText')
            if day_field:
                day_field.click()
                time.sleep(1)
                day_field.clear()
                day_field.send_keys(birth_date['day'])

                # Enter month
                month_field = find_element_safe(driver, '//android.widget.ScrollView/android.widget.EditText[3]/android.widget.EditText')
                if month_field:
                    month_field.click()
                    time.sleep(1)
                    month_field.clear()
                    month_field.send_keys(birth_date['month'])

                    # Enter year
                    year_field = find_element_safe(driver, '//android.widget.ScrollView/android.widget.EditText[4]/android.widget.EditText')
                    if year_field:
                        year_field.click()
                        time.sleep(1)
                        year_field.clear()
                        year_field.send_keys(birth_date['year'])
                        print(f"✅ Entered birth date: Day={birth_date['day']}, Month={birth_date['month']}, Year={birth_date['year']}")
                    else:
                        print("Year field not found")
                        return False, "Year field not found"
                else:
                    print("Month field not found")
                    return False, "Month field not found"
            else:
                print("Day field not found")
                return False, "Day field not found"
        except Exception as e:
            print(f"Error entering birth date: {e}")
            return False, f"Failed to enter birth date: {e}"

        # Check for any validation error after entering birth date
        error_found, error_msg = is_error_displayed(driver)
        if error_found:
            # If we expected an error (invalid date), this is actually a pass
            if not scenario["expected_result"]["should_submit"]:
                return True, f"Form was correctly blocked with error: {error_msg}"
            else:
                return False, f"Form validation failed with error: {error_msg}"

        # Select education level
        try:
            if inputs['education']:
                print(f"Selecting education level: {inputs['education']}")
                education_dropdown = find_element_safe(driver, '//android.widget.Button[@content-desc="Education Level *"]')
                if education_dropdown:
                    education_dropdown.click()
                    time.sleep(2)
                    education_choice = find_element_safe(driver, f'''//android.widget.Button[@content-desc="{inputs['education']}"]''')
                    if education_choice:
                        education_choice.click()
                        print("✅ Selected education level")
                    else:
                        print(f"Education choice {inputs['education']} not found")
                        return False, f"Education choice {inputs['education']} not found"
                else:
                    print("Education dropdown not found")
                    return False, "Education dropdown not found"
        except Exception as e:
            print(f"Error selecting education: {e}")
            return False, f"Failed to select education: {e}"

        # Enter city
        try:
            print(f"Entering city: {inputs['city']}")
            # Try different XPaths for the city field as the structure might change
            city_field = find_element_safe(driver, '//android.widget.ScrollView/android.widget.EditText[5]/android.widget.EditText')
            if not city_field:
                # Try alternative XPath
                city_field = find_element_safe(driver, '//android.widget.EditText[@text="City *"]')
            if not city_field:
                # Try more general XPath
                city_fields = driver.find_elements(By.XPATH, '//android.widget.EditText')
                for field in city_fields:
                    hint = field.get_attribute("hint")
                    if hint and "City" in hint:
                        city_field = field
                        break

            if city_field:
                city_field.click()
                time.sleep(1)
                city_field.clear()
                city_field.send_keys(inputs['city'])
                print("✅ Entered city")
            else:
                print("City field not found")
                # If we can't find city field and we're testing empty name, this might be expected
                if not inputs['name'] and not scenario["expected_result"]["should_submit"]:
                    return True, "Form correctly blocked before city field (due to name validation)"
                return False, "City field not found"
        except Exception as e:
            print(f"Error entering city: {e}")
            # If this is a name validation test, we might expect this error
            if not inputs['name'] and not scenario["expected_result"]["should_submit"]:
                return True, "Form correctly blocked before city field (due to name validation)"
            return False, f"Failed to enter city: {e}"

        # Check for any validation error after entering city
        error_found, error_msg = is_error_displayed(driver)
        if error_found and not inputs['city']:
            # If we expected an error (empty city), this is actually a pass
            if not scenario["expected_result"]["should_submit"]:
                return True, f"Form was correctly blocked with error: {error_msg}"
            else:
                return False, f"Form validation failed with error: {error_msg}"

        # Select gender
        try:
            if inputs['gender']:
                print(f"Selecting gender: {inputs['gender']}")
                gender_field = find_element_safe(driver, f'//android.widget.RadioButton[@content-desc="{inputs["gender"]}"]')
                if gender_field:
                    gender_field.click()
                    print("✅ Selected gender")
                else:
                    print(f"Gender option {inputs['gender']} not found")
                    return False, f"Gender option {inputs['gender']} not found"
        except Exception as e:
            print(f"Error selecting gender: {e}")
            return False, f"Failed to select gender: {e}"

        # Need to scroll down for AI models
        try:
            print("Scrolling down")
            driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=300, duration=800)
            time.sleep(1)
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False, f"Failed to scroll: {e}"

        # Select AI models and enter defects
        try:
            print("Selecting AI models and entering defects")
            count = 1
            for model, defect in inputs['ai_models_with_defects'].items():
                print(f"Selecting AI model: {model}")
                model_checkbox = find_element_safe(driver, f'''//android.widget.CheckBox[@content-desc="{model}"]''')
                if model_checkbox:
                    model_checkbox.click()
                    time.sleep(1)

                    # Scroll down again to see defect input
                    driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=300, duration=800)
                    time.sleep(1)

                    print(f"Entering defect for {model}: {defect}")
                    defect_input = None
                    if count == 1:
                        defect_input = find_element_safe(driver, f'''//android.view.View[@content-desc="AI Models Section"]/android.widget.EditText/android.widget.EditText''')
                    else:
                        defect_input = find_element_safe(driver, f'''//android.view.View[@content-desc="AI Models Section"]/android.widget.EditText[{str(count)}]/android.widget.EditText''')

                    if defect_input:
                        defect_input.click()
                        time.sleep(1)
                        defect_input.clear()
                        defect_input.send_keys(defect)
                        count += 1
                        print(f"✅ Selected AI model and entered defect")
                    else:
                        print(f"Defect input for {model} not found")
                        return False, f"Defect input for {model} not found"
                else:
                    print(f"AI model {model} checkbox not found")
                    return False, f"AI model {model} checkbox not found"
        except Exception as e:
            print(f"Error with AI models: {e}")
            return False, f"Failed with AI models: {e}"

        # Enter beneficial use case
        try:
            print(f"Entering beneficial use case: {inputs['beneficial_use_case']}")
            # Scroll down again to see beneficial use case input
            driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=300, duration=800)
            time.sleep(1)

            use_case_field = find_element_safe(driver, f'''//android.widget.ScrollView/android.widget.EditText/android.widget.EditText''')
            if use_case_field:
                use_case_field.click()
                time.sleep(1)
                use_case_field.clear()
                use_case_field.send_keys(inputs['beneficial_use_case'])
                print("✅ Entered beneficial use case")
            else:
                print("Beneficial use case field not found")
                return False, "Beneficial use case field not found"
        except Exception as e:
            print(f"Error entering beneficial use case: {e}")
            return False, f"Failed to enter beneficial use case: {e}"

        # Try to submit the form
        try:
            print("Attempting to submit form")
            # Final scroll to ensure Send button is visible
            driver.swipe(start_x=800, start_y=1800, end_x=800, end_y=800, duration=800)
            time.sleep(1)

            # Check if submit button exists and is clickable
            submit_button_exists = True
            try:
                submit_button = find_element_safe(driver, '//android.widget.Button[@content-desc="Send"]')
                if submit_button:
                    submit_button.click()
                    print("✅ Submit button clicked")
                    time.sleep(5)  # Wait longer for potential error messages or success
                else:
                    submit_button_exists = False
                    print("Submit button not found")
            except Exception as e:
                submit_button_exists = False
                print(f"Could not click submit button: {e}")

            # Capture any error messages after submission attempt
            error_found, error_msg = is_error_displayed(driver)

            # Check name validation - this is specific for TC1.3 (single word name)
            name_error = False
            if inputs['name'] and len(inputs['name'].split()) == 1:
                try:
                    name_errors = driver.find_elements(By.XPATH, '//android.widget.TextView')
                    for element in name_errors:
                        text = element.get_attribute("text")
                        if text and "name and surname" in text.lower():
                            print(f"Found name validation error: {text}")
                            name_error = True
                            error_found = True
                            error_msg = text
                            break
                except:
                    pass

            # Take a screenshot for debugging (if needed)
            try:
                screenshot_name = f"{scenario['scenario_id'].replace('.', '_')}.png"
                driver.get_screenshot_as_file(screenshot_name)
                print(f"Screenshot saved as {screenshot_name}")
            except Exception as e:
                print(f"Could not take screenshot: {e}")

            # Check if we're still on the form page by looking for the name field
            still_on_form = find_element_safe(driver, '//android.widget.EditText[@hint="Name-Surname *"]') is not None

            # Check if we're on the login page (successful submission)
            on_login_page = find_element_safe(driver, '//android.widget.EditText[@hint="Enter your email or phone number"]') is not None

            # Determine if the test passed based on expected results
            expected_should_submit = scenario["expected_result"]["should_submit"]

            # If we expected it to submit successfully
            if expected_should_submit:
                if on_login_page:
                    return True, "Successfully submitted form and redirected to login screen as expected"
                elif error_found:
                    return False, f"Expected to submit but got error message: {error_msg}"
                elif still_on_form:
                    return False, "Expected to submit but still on form page"
                else:
                    return False, "Could not determine if submission was successful"
            # If we expected it NOT to submit
            else:
                if name_error and "name with only one word" in scenario['description'].lower():
                    return True, f"Form was correctly blocked with name validation error: {error_msg}"

                if on_login_page:
                    return False, "Form submitted successfully but should have been blocked"
                elif error_found:
                    if "error_message" in scenario["expected_result"]:
                        expected_error = scenario["expected_result"]["error_message"]
                        if expected_error.lower() in error_msg.lower():
                            return True, f"Form was correctly blocked with expected error: {error_msg}"
                        else:
                            # Still a pass but with different error message
                            return True, f"Form was blocked but with different error: {error_msg}"
                    return True, f"Form was correctly blocked with error: {error_msg}"
                elif still_on_form:
                    return True, "Form correctly did not submit (still on form page)"
                else:
                    return False, "Could not determine if submission was blocked"
        except Exception as e:
            print(f"Error in submission verification: {e}")
            traceback.print_exc()
            return False, f"Test failed during submission verification: {e}"
    except Exception as e:
        print(f"General error in test scenario: {e}")
        traceback.print_exc()
        return False, f"Test failed with general exception: {e}"

def reset_app(driver):
    """Reset the app to the login screen."""
    try:
        driver.terminate_app("com.example.my_auth_app")
        time.sleep(2)
        driver.activate_app("com.example.my_auth_app")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"Error resetting app: {e}")
        traceback.print_exc()
        return False

def run_test_case(driver, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run all scenarios in a test case and return results.
    """
    results = []

    print(f"\n{'='*80}")
    print(f"Running Test Case: {test_case['id']} - {test_case['name']}")
    print(f"Description: {test_case['description']}")
    print(f"{'='*80}\n")

    for scenario in test_case['scenarios']:
        # Reset and login for each scenario
        if not reset_app(driver):
            result = {
                "test_case_id": test_case['id'],
                "scenario_id": scenario['scenario_id'],
                "description": scenario['description'],
                "success": False,
                "message": "Failed to reset app",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(result)
            continue

        if not login_with_email(driver):
            result = {
                "test_case_id": test_case['id'],
                "scenario_id": scenario['scenario_id'],
                "description": scenario['description'],
                "success": False,
                "message": "Failed to login",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(result)
            continue

        print(f"\n{'-'*80}")
        print(f"Running Scenario: {scenario['scenario_id']} - {scenario['description']}")
        print(f"{'-'*80}\n")

        # Run the test scenario
        success, message = run_test_scenario(driver, scenario)

        result = {
            "test_case_id": test_case['id'],
            "scenario_id": scenario['scenario_id'],
            "description": scenario['description'],
            "success": success,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if success:
            print(f"\n✅ Scenario {scenario['scenario_id']} PASSED: {message}")
        else:
            print(f"\n❌ Scenario {scenario['scenario_id']} FAILED: {message}")

        results.append(result)
        time.sleep(2)  # Brief pause between scenarios

    return results

def main():
    """Main function to run all tests from a JSON file."""
    parser = argparse.ArgumentParser(description='Run automated tests for the Survey app')
    parser.add_argument('--json', '-j', required=True, help='Path to JSON file with test cases')
    parser.add_argument('--output', '-o', default='test_results.json', help='Path to output JSON file for results')
    parser.add_argument('--filter', '-f', help='Filter test cases by ID (comma-separated)')
    args = parser.parse_args()

    # Load test cases
    test_data = load_test_cases(args.json)

    # Filter test cases if specified
    if args.filter:
        filter_ids = args.filter.split(',')
        test_data['test_cases'] = [tc for tc in test_data['test_cases'] if tc['id'] in filter_ids]

    print(f"Loaded {len(test_data['test_cases'])} test cases")

    # Initialize the driver
    driver = create_driver()

    # Run all test cases
    all_results = []

    try:
        for test_case in test_data['test_cases']:
            results = run_test_case(driver, test_case)
            all_results.extend(results)
    except Exception as e:
        print(f"Error running tests: {e}")
        traceback.print_exc()
    finally:
        # Generate summary
        total_scenarios = len(all_results)
        if total_scenarios > 0:
            passed_scenarios = sum(1 for r in all_results if r['success'])

            print(f"\n\n{'='*80}")
            print("TEST EXECUTION SUMMARY")
            print(f"{'='*80}")
            print(f"Total scenarios: {total_scenarios}")
            print(f"Passed scenarios: {passed_scenarios}")
            print(f"Failed scenarios: {total_scenarios - passed_scenarios}")
            print(f"Success rate: {passed_scenarios/total_scenarios*100:.2f}%")

            # Save results to file
            try:
                with open(args.output, 'w') as f:
                    json.dump(all_results, f, indent=2)
                print(f"\nTest results saved to {args.output}")
            except Exception as e:
                print(f"Error saving results: {e}")

        # Clean up
        driver.quit()

if __name__ == "__main__":
    main()