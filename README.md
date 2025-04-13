# my_auth_app

# AI Feedback Collection App

This project is a Flutter-based native mobile application designed to collect structured user feedback on AI tools. It supports secure login via Google, Spotify, or test credentials, and presents a dynamic, validated survey form. The application is integrated with Firebase for authentication and Firestore for survey data storage.

## Features
- **Authentication Options:**
  - Google Sign-In
  - Spotify OAuth
  - Debug/Test User Mode (Email or Phone)
- **Survey Form:**
  - Name, Birth Date, Education Level, City, Gender
  - Multi-selection of AI models with defect descriptions
  - Open-ended question on beneficial use case
  - Full input validation and error feedback
  - Submits data to Firestore and sends email
- **Survey Validation:**
  - Validates birth date (including age boundaries)
  - Ensures descriptive answers for open-ended questions
  - Requires detailed feedback for each selected AI model

## Test Automation
Automated testing is implemented with **Appium (Python)** and structured JSON-based test cases.

### Test Components
- **Test Runner:** `test_runner.py`
- **Test Data:** `test_cases.json`
- **Driver Setup:** Android emulator with `UiAutomator2`

### Test Categories
- Required Field Validation  
- Birth Date Validation  
- Education & Gender Selection  
- AI Models & Defects  
- Text Input Constraints  
- Edge Cases (e.g., age limits, format errors)

### Running the Tests
1. Start the Appium server:
   ```bash
   appium server --use-drivers=uiautomator2
   ```
2. Connect your Android emulator:
   ```bash
   adb devices
   ```
3. Run the test suite:
   ```bash
   python test_runner.py --json test_cases.json
   ```

#### Optional:
- Filter test cases by ID:
  ```bash
  python test_runner.py -j test_cases.json -f TC1,TC2
  ```
- Save output results to a file:
  ```bash
  python test_runner.py -j test_cases.json -o my_results.json
  ```

## Project Structure
```
lib/
├── main.dart                    # App entry point (Firebase init, routing)
├── screens/
│   ├── login_screen.dart        # Login screen with multiple login methods
│   ├── login_success_page.dart  # Transitional page before survey
│   └── survey_page.dart         # AI survey form and submission logic
test_automation/
├── test_runner.py               # Appium test script for automated form validation
└── test_cases.json              # Structured test case scenarios in JSON format
```

## Dependencies

### Flutter App
- firebase_core
- firebase_auth
- cloud_firestore
- google_sign_in
- flutter_web_auth_2
- font_awesome_flutter

### Testing
- Python 3.8+
- appium
- selenium
- termcolor

Install test dependencies:
```bash
pip install appium-python-client selenium termcolor
```

## Contact
For questions or suggestions, reach out to mayasa.naama@gmail.com, or m.lami@bilkent.edu.tr.
