from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

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

    # Parse birth_date to extract day, month, and year
    # Expected format: "4, Friday, April 4, 2025"
    try:
        # Parse the date string to get the components
        # This creates a datetime object from the string for easier manipulation
        date_parts = birth_date.split(", ")
        date_string = date_parts[2] + " " + date_parts[0] + ", " + date_parts[3]  # "April 4, 2025"
        date_obj = datetime.datetime.strptime(date_string, "%B %d, %Y")

        day = str(date_obj.day)
        month = str(date_obj.month)
        year = str(date_obj.year)

        print(f"Parsed date: Day={day}, Month={month}, Year={year}")
    except Exception as e:
        print(f"Error parsing date: {e}")
        day = "1"
        month = "1"
        year = "2000"

    print("Entering the birth date fields!")
    # Enter day
    day_field = driver.find_element(By.XPATH, '//android.widget.ScrollView/android.widget.EditText[2]/android.widget.EditText')
    day_field.click()
    time.sleep(1)
    day_field.send_keys(day)
    print("✅ Entered day")

    # Enter month
    month_field = driver.find_element(By.XPATH, '//android.widget.ScrollView/android.widget.EditText[3]/android.widget.EditText')
    month_field.click()
    time.sleep(1)
    month_field.send_keys(month)
    print("✅ Entered month")

    # Enter year
    year_field = driver.find_element(By.XPATH, '//android.widget.ScrollView/android.widget.EditText[4]/android.widget.EditText')
    year_field.click()
    time.sleep(1)
    year_field.send_keys(year)
    print("✅ Entered year")
    print("Done with birth date!")

    print("Choosing the education level!")
    education_dropdown = driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Education Level *"]')
    education_dropdown.click()
    time.sleep(2)
    education_choice = driver.find_element(By.XPATH, f'''//android.widget.Button[@content-desc="{education}"]''')
    education_choice.click()
    print("Done!")

    time.sleep(2)

    print("Trying the city field!")
    city_field = driver.find_element(By.XPATH, '//android.widget.ScrollView/android.widget.EditText[5]/android.widget.EditText')
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
        if count == 1:
            defect_input = driver.find_element(By.XPATH, f'''//android.view.View[@content-desc="AI Models Section"]/android.widget.EditText/android.widget.EditText''')
        else:
            defect_input = driver.find_element(By.XPATH, f'''//android.view.View[@content-desc="AI Models Section"]/android.widget.EditText[{str(count)}]/android.widget.EditText''')
        defect_input.click()
        time.sleep(2)
        defect_input.send_keys(defect)
        count += 1

    print("Done!")

    print("Benefits!")
    use_case_field = driver.find_element(By.XPATH,  f'''//android.widget.ScrollView/android.widget.EditText/android.widget.EditText''')
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


# Run test
if __name__ == "__main__":
    driver = login_with_email("john@example.com", "pass123")

    result = test_survey(
        driver,
        name="Jane Doe",
        birth_date="4, Friday, April 4, 2010",  # Changed year to valid past date
        education="Bachelor's Degree",
        city="Ankara",
        gender="Female",
        ai_models_with_defects={
            "ChatGPT": "Sometimes gives outdated info",
            "Copilot": "Overwrites code unexpectedly"
        },
        beneficial_use_case="I use AI to summarize news articles and speed up brainstorming.",
        valid=True
    )
    test_name = "Test 1.1"

    if result:
        print(f"Test {test_name} Passed! ✅")
    else:
        print(f"Test {test_name} Failed! ❌")

    # Test 2
    result = test_survey(
        driver,
        name="",
        birth_date="4, Friday, April 4, 2010",  # Changed year to valid past date
        education="Bachelor's Degree",
        city="Ankara",
        gender="Female",
        ai_models_with_defects={
            "ChatGPT": "Sometimes gives outdated info",
            "Copilot": "Overwrites code unexpectedly"
        },
        beneficial_use_case="I use AI to summarize news articles and speed up brainstorming.",
        valid=False
    )
    test_name = "Test 1.2"
    if result:
        print(f"Test {test_name} Passed! ✅")
    else:
        print(f"Test {test_name} Failed! ❌")