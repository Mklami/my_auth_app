const { remote } = require('webdriverio');
const { byValueKey } = require('appium-flutter-finder');

const opts = {
  hostname: 'localhost',
  port: 4723,
  logLevel: 'info',
  capabilities: {
    'platformName': 'Android',
    'appium:deviceName': 'emulator-5554',
    'appium:automationName': 'Flutter',
    'appium:app': '/Users/mayasalami/my_auth_app/build/app/outputs/flutter-apk/app-debug.apk',
    'appium:retryBackoffTime': 500,
    'appium:maxRetryCount': 5,
    'appium:dartObservatoryPort': 8888,
    'appium:forwardPort': 8888
  }
};

// Helper function to add delays
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  const driver = await remote(opts);

  try {
    console.log("🔵 Launching Login Test...");

    // Add initial delay to make sure app is fully loaded
    await sleep(5000);
    console.log("App should be loaded, proceeding with test...");

    // Try to get a screenshot or page source to validate connection
    console.log("Checking if app is accessible...");
    try {
      const source = await driver.getPageSource();
      console.log("Successfully connected to app! Source preview:",
                  source.substring(0, 100) + "...");
    } catch (e) {
      console.log("Could not get page source:", e.message);
    }

    // Email field with retry logic
    console.log("Attempting to find email field...");
    const emailField = byValueKey("emailOrPhoneField");

    let attempts = 0;
    const maxAttempts = 3;
    while (attempts < maxAttempts) {
      try {
        await driver.execute("flutter:waitFor", emailField, 5000);
        console.log("Email field found!");
        await driver.execute("flutter:enterText", emailField, "john@example.com");
        console.log("Text entered in email field");
        break;
      } catch (e) {
        attempts++;
        console.log(`Attempt ${attempts} failed: ${e.message}`);
        await sleep(2000);
      }
    }

    // Continue with other fields if email field worked
    await sleep(1000);

    const passwordField = byValueKey("passwordField");
    await driver.execute("flutter:waitFor", passwordField, 5000);
    await driver.execute("flutter:enterText", passwordField, "pass123");
    console.log("Text entered in password field");

    await sleep(1000);

    const loginButton = byValueKey("signInButton");
    await driver.execute("flutter:waitFor", loginButton, 5000);
    await driver.execute("flutter:tap", loginButton);
    console.log("Login button tapped");

    // Wait a bit to see results
    await sleep(3000);

    console.log("✅ Login test completed!");
  } catch (e) {
    console.error("❌ Login test failed:", e);
  } finally {
    await driver.deleteSession();
  }
}

main().catch(console.error);