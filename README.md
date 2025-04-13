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

## Project Structure

```
.
├── android/                   # Android platform-specific files
├── appium_tests/              # Appium test automation suite
│   ├── test_runner.py         # Main test runner script (Python)
│   ├── test_cases.json        # JSON file containing test case definitions
│   ├── *.py                   # Individual test scripts for different login methods/flows
│   └── ...                    # Other test-related files (e.g., JS tests, config)
├── build/                     # Build output directory
├── functions/                 # Firebase Cloud Functions (if any)
├── lib/                       # Main Flutter application source code
│   ├── main.dart              # App entry point (Firebase init, routing)
│   ├── main_debug.dart        # Entry point for debug mode
│   ├── screens/               # UI screens for the application
│   │   ├── login_screen.dart  # Login screen logic
│   │   ├── login_success_page.dart # Transitional page after successful login
│   │   └── survey_page.dart   # Survey form UI and logic
│   ├── utils/                 # Utility functions or classes
│   └── firebase_options.dart  # Firebase configuration options
├── test/                      # Flutter widget/unit tests (if any)
├── .env                       # Environment variables (Spotify credentials, etc.) - **DO NOT COMMIT**
├── appium-config.json         # Configuration for Appium
├── firebase.json              # Firebase project configuration
├── pubspec.yaml               # Flutter project dependencies and metadata
├── README.md                  # This file
└── ...                        # Other configuration files (.gitignore, .metadata, etc.)
```

## Getting Started

### Prerequisites
- Flutter SDK: [Install Flutter](https://flutter.dev/docs/get-started/install)
- An Android Emulator or Physical Device: [Set up an editor](https://flutter.dev/docs/get-started/editor)
- Firebase Project: Set up a Firebase project and configure it for Android. Add the `google-services.json` file to `android/app/`.
- Environment Variables: Create a `.env` file in the project root with your Spotify Client ID and Secret:
  ```
  SPOTIFY_CLIENT_ID=your_spotify_client_id
  SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
  ```

### Running the App
1.  **Install Dependencies:**
    ```bash
    flutter pub get
    ```
2.  **Run the Application:**
    ```bash
    flutter run
    ```
    - To run in debug mode (potentially using `main_debug.dart`):
      ```bash
      flutter run lib/main_debug.dart
      ```

## Test Automation

Automated testing is implemented with **Appium (Python)** and structured using JSON-based test cases.

### Test Setup
1.  **Install Python Dependencies:** Ensure you have Python 3.8+ installed.
    ```bash
    pip install appium-python-client selenium termcolor
    ```
2.  **Start Appium Server:**
    ```bash
    appium server --use-drivers=uiautomator2
    ```
3.  **Connect Android Emulator/Device:** Ensure your target device is listed.
    ```bash
    adb devices
    ```

### Running the Tests
Navigate to the test directory and run the main runner script:

```bash
cd appium_tests
python test_runner.py --json test_cases.json
```

#### Optional Test Execution:
-   **Filter test cases by ID:** Provide a comma-separated list of test case IDs.
    ```bash
    python test_runner.py -j test_cases.json -f TC1,TC2
    ```
-   **Save output results:** Specify an output file for the test results.
    ```bash
    python test_runner.py -j test_cases.json -o my_results.json
    ```

## Dependencies

### Flutter App
- `firebase_core`
- `firebase_auth`
- `cloud_firestore`
- `google_sign_in`
- `flutter_web_auth_2`
- `font_awesome_flutter`
- `flutter_dotenv` (Implied by `.env` usage)

### Testing (Python)
- Python 3.8+
- `appium-python-client`
- `selenium`
- `termcolor`

*Refer to `pubspec.yaml` for Flutter dependencies and `appium_tests/` for potential JS testing dependencies (`package.json`).*

## Contact
For questions or suggestions, reach out to mayasa.naama@gmail.com, or m.lami@bilkent.edu.tr.
