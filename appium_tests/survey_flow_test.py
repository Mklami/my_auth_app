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

def login_to_app(driver, wait):
    """Performs login to the app using the provided credentials"""
    try:
        time.sleep(5)  # Wait for app to load fully
        print("App loaded, logging in...")

        # Locate email field by hint text
        email_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your email or phone number"]')
        ))
        email_input.click()
        email_input.clear()
        email_input.send_keys("john@example.com")
        print("✅ Entered email")

        # Locate password field by hint text
        password_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.EditText[@hint="Enter your password"]')
        ))
        password_input.click()
        password_input.clear()
        password_input.send_keys("pass123")
        print("✅ Entered password")

        # Click the Sign in button using content-desc "Sign in"
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

        time.sleep(3)
        if "AI Survey" in driver.page_source:
            print("✅ Login successful! Found AI Survey page.")
            return True
        else:
            print("❌ Not on survey page after login attempt")
            return False
    except Exception as e:
        print(f"❌ Email/password login test failed: {e}")
        return False

def test_survey_form_flow():
    """
    Final version of the survey form flow test.
    • Uses keys (via ACCESSIBILITY_ID) for Name, Education, Gender, and Beneficial Use Case.
    • Uses your working date-selection code.
    • Closes the education dropdown with a back-press if no option is successfully selected.
    """
    driver = create_driver()
    wait = WebDriverWait(driver, 20)
    test_results = []

    try:
        # --- Login ---
        if not login_to_app(driver, wait):
            print("❌ Test failed at login step")
            return False
        print("\n🔍 Starting survey form flow test...")

        # --- Test 1: Name Field ---
        try:
            # Locate by key "nameField"
            name_field = wait.until(EC.presence_of_element_located(
                            (By.XPATH, '//android.widget.ScrollView//android.widget.EditText[1]')
                        ))
            name_field.click()
            name_field.clear()
            name_field.send_keys("John Smith")
            time.sleep(1)
            entered_text = name_field.get_attribute("text")
            if "John Smith" not in entered_text:
                # Alternative: type character-by-character if necessary
                name_field.clear()
                for ch in "John Smith":
                    name_field.send_keys(ch)
                    time.sleep(0.1)
                print("✅ Name field filled using alternative method")
            else:
                print("✅ Name field filled with 'John Smith'")
            test_results.append(True)
        except Exception as e:
            print("❌ Name field error:", e)
            test_results.append(False)

        # --- Test 2: Birth Date Selection ---
        try:
            # Use your working block to find a clickable element that hints at a date field:
            clickable_elements = driver.find_elements(By.XPATH, "//*[@clickable='true']")
            date_candidates = []
            for i, element in enumerate(clickable_elements):
                try:
                    text = element.get_attribute('text') or ''
                    content_desc = element.get_attribute('content-desc') or ''
                    class_name = element.get_attribute('className') or ''
                    if ('date' in text.lower() or 'select' in text.lower() or
                        'date' in content_desc.lower() or 'select' in content_desc.lower()):
                        date_candidates.append(element)
                        print(f"Potential date field {i}: {text} | {content_desc} | {class_name}")
                except:
                    pass
            if date_candidates:
                date_candidates[0].click()
                print("✅ Clicked on potential birth date field")
                time.sleep(2)
                buttons = driver.find_elements(By.CLASS_NAME, "android.widget.Button")
                if buttons:
                    for i, btn in enumerate(buttons):
                        try:
                            print(f"Button {i}: {btn.get_attribute('text')}")
                        except:
                            print(f"Button {i}: <no text>")
                    ok_button = None
                    for btn in buttons:
                        try:
                            btn_text = btn.get_attribute('text') or ''
                            if btn_text.upper() in ['OK', 'DONE', 'SET']:
                                ok_button = btn
                                break
                        except:
                            pass
                    if ok_button:
                        ok_button.click()
                        print("✅ Clicked OK on date picker")
                    else:
                        buttons[-1].click()
                        print("✅ Clicked last button on date picker")
                    time.sleep(1)
                    print("Date selection completed")
                    test_results.append(True)
                else:
                    print("❌ No buttons found in date picker")
                    test_results.append(False)
            else:
                print("❌ No potential date fields found")
                test_results.append(False)
        except Exception as e:
            print(f"❌ Birth date selection failed: {e}")
            test_results.append(False)

        # --- Test 3: Education Dropdown ---
        try:
            # Locate education field by key "educationField"
            education_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.EditText[@hint="Education Level *"]')))
            education_field.click()
            print("✅ Education dropdown clicked")
            time.sleep(2)
            # Attempt to find dropdown options (ideally in a ListView)
            dropdown_options = driver.find_elements(By.XPATH, '//android.widget.ListView//android.widget.TextView')
            if not dropdown_options or len(dropdown_options) == 0:
                # Fallback: find any TextView options
                dropdown_options = driver.find_elements(By.XPATH, '//android.widget.TextView')
            if dropdown_options and len(dropdown_options) > 0:
                print(f"Found {len(dropdown_options)} dropdown option(s):")
                selected = False
                for option in dropdown_options:
                    opt_text = (option.get_attribute("text") or "").strip()
                    print(f"Option: {opt_text}")
                    # Adjust this condition based on the expected option.
                    if opt_text == "Bachelor's Degree":
                        option.click()
                        print(f"✅ Selected education option: {opt_text}")
                        selected = True
                        break
                if not selected:
                    print("❌ No valid education option found; closing dropdown")
                    driver.press_keycode(4)  # Press back to close dropdown
                else:
                    # Wait a moment for dropdown to close after selection
                    time.sleep(1)
                test_results.append(selected)
            else:
                print("❌ No education options found")
                test_results.append(False)
        except Exception as e:
            print("❌ Education dropdown error:", e)
            test_results.append(False)

        # --- Test 4: Gender Option ---
        try:
            # Locate Gender option using key "genderOption_Male"
            gender_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.RadioButton[@content-desc="Female"]')))
            gender_option.click()
            print("✅ Gender option (Female) selected")
            test_results.append(True)
        except Exception as e:
            print("❌ Gender selection error:", e)
            test_results.append(False)

        # --- Test 5: AI Models Selection and Defects ---
        try:
            # Locate AI Models header (for debugging)
            ai_models_header = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//android.view.View[@content-desc="AI Models You\'ve Tried *"]')
            ))
            print("✅ AI Models section located")
            # Select checkboxes using the provided XPATHs
            chatgpt_checkbox = driver.find_element(By.XPATH, '//android.widget.CheckBox[@content-desc="ChatGPT"]')
            bard_checkbox    = driver.find_element(By.XPATH, '//android.widget.CheckBox[@content-desc="Bard"]')
            chatgpt_checkbox.click()
            time.sleep(1)
            bard_checkbox.click()
            time.sleep(1)
            print("✅ Selected ChatGPT and Bard checkboxes")
            # Fill defect field for ChatGPT using provided XPATH pattern
            defect_chatgpt = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@content-desc, "aiModelDefects_ChatGPT")]')
            ))
            defect_chatgpt.send_keys("Occasionally provides inaccurate information")
            print("✅ Filled defects for ChatGPT")
            test_results.append(True)
        except Exception as e:
            print("❌ AI models selection error:", e)
            test_results.append(False)

        # --- Test 6: Beneficial Use Case Field ---
        try:
            # Locate using key "beneficialUseCaseField"
            use_case_field = wait.until(EC.element_to_be_clickable((By.ACCESSIBILITY_ID, "beneficialUseCaseField")))
            use_case_field.clear()
            use_case_field.send_keys("AI automates repetitive tasks and improves productivity")
            print("✅ Beneficial use case field filled")
            test_results.append(True)
        except Exception as e:
            print("❌ Beneficial use case field error:", e)
            test_results.append(False)

        # --- Test 7: Verify Submit/Send Button ---
        try:
            send_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//android.widget.Button[@content-desc="Send"]')
            ))
            if send_button.is_displayed():
                print("✅ Send button located and visible")
                test_results.append(True)
            else:
                print("❌ Send button not visible")
                test_results.append(False)
        except Exception as e:
            print("❌ Send button error:", e)
            test_results.append(False)

        # --- Final Summary ---
        passed = test_results.count(True)
        total = len(test_results)
        print(f"\n📊 Survey Form Flow Test Summary: {passed}/{total} steps passed")
        return passed == total

    except Exception as ex:
        print("❌ Overall test error:", ex)
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starting Survey Form Flow Test...")
    result = test_survey_form_flow()
    if result:
        print("✅ Survey Form Flow Test: PASSED")
    else:
        print("❌ Survey Form Flow Test: FAILED")
