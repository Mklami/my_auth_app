const wdio = require("webdriverio");
const { byValueKey } = require("appium-flutter-finder");

const opts = {
  path: '/wd/hub',
  port: 4723,
  capabilities: {
    platformName: 'Android',
    deviceName: 'emulator-5554',
    automationName: 'Flutter',
    app: '/Users/mayasalami/my_auth_app/build/app/outputs/flutter-apk/app-debug.apk',
  }
};

async function main() {
  const driver = await wdio.remote(opts);

  try {
    console.log("✅ App launched!");

    const nameField = byValueKey('nameField');
    await driver.execute('flutter:waitFor', nameField);
    await driver.elementSendKeys(nameField, 'Test User');

    // you can add more steps here...

    console.log("✅ Interaction completed!");
  } catch (err) {
    console.error("❌ Test failed:", err);
  } finally {
    await driver.deleteSession();
  }
}

main();
