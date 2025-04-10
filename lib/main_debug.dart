import 'dart:developer';
import 'package:flutter/material.dart';

// Import your regular main.dart imports and main function
import 'main.dart' as app;

void main() {
  // Explicitly enable VM service and set a specific port
  debugger(message: 'Start debugging for Appium');
  app.main();
}