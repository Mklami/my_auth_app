import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'login_success_page.dart'; // Import the new success page
import 'package:google_sign_in/google_sign_in.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '/utils/config.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailOrPhoneController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String? _errorMessage;

  @override
  Future<void> _handleGoogleLogin() async {
    try {
      // Show loading indicator
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Signing in with Google...')),
      );

      // Initialize Google Sign-In
      final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();

      if (googleUser == null) {
        // User canceled the sign-in flow
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        return;
      }

      print("Google account selected: ${googleUser.email}");

      // Get authentication details
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // THIS IS THE KEY PART THAT NEEDS TO CHANGE
      // Use the raw provider approach instead of the credential helper
      final AuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Sign in with raw credential
      await FirebaseAuth.instance.signInWithCredential(credential);
      print('✅ Firebase sign-in successful, navigating to success page');

      // Success, navigate to success page instead of survey page
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const LoginSuccessPage()),
        );
      });
    } catch (e) {
      // Fix the substring error by using a safer approach
      String errorMessage = e.toString();
      if (errorMessage.length > 100) {
        errorMessage = errorMessage.substring(0, 100) + '...';
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Google login failed: $errorMessage')),
      );
    }
  }

  Future<void> _handleSpotifyLogin() async {
    const clientId = '78b021d09f2f440abd7cbe6b41b559b5';
    const redirectUri = 'myauthapp://callback';
    const scopes = 'user-read-email';

    final authUrl = Uri.https('accounts.spotify.com', '/authorize', {
      'response_type': 'code',
      'client_id': clientId,
      'redirect_uri': redirectUri,
      'scope': scopes,
      'state': 'secure_random_state',
    });

    try {
      final result = await FlutterWebAuth2.authenticate(
        url: authUrl.toString(),
        callbackUrlScheme: 'myauthapp',
      );

      final code = Uri.parse(result).queryParameters['code'];
      if (code != null) {
        // Navigate to success page instead of survey page
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const LoginSuccessPage()),
        );
      } else {
        throw Exception('Spotify login failed: No code returned');
      }
    } on PlatformException catch (e) {
      if (e.code == 'CANCELED') {
        // User backed out or dismissed the login window
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Spotify login was canceled by the user.'),
          ),
        );
      } else {
        // Other PlatformException
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Spotify login error: ${e.message}')),
        );
      }
    } catch (e) {
      // Any other unexpected errors
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('An unexpected error occurred: $e')),
      );
    }
  }

  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1F2937), // Tailwind gray-900
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Card(
              color: const Color(0xFF1F2937), // Tailwind gray-900
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: 8,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'Welcome Back',
                      style: TextStyle(fontSize: 24, color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Please sign in to continue',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 24),

                    // Google Button
                    ElevatedButton.icon(
                      onPressed: _handleGoogleLogin,
                      icon: const FaIcon(FontAwesomeIcons.google, color: Colors.black),
                      label: const Text('Continue with Google', style: TextStyle(color: Colors.black)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        minimumSize: const Size(double.infinity, 48),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Spotify Button
                    ElevatedButton.icon(
                      onPressed: _handleSpotifyLogin,
                      icon: const FaIcon(FontAwesomeIcons.spotify, color: Colors.white),
                      label: const Text('Continue with Spotify', style: TextStyle(color: Colors.white)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1DB954),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        minimumSize: const Size(double.infinity, 48),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    const SizedBox(height: 24),

                    Row(
                      children: const [
                        Expanded(child: Divider(color: Colors.grey)),
                        Padding(
                          padding: EdgeInsets.symmetric(horizontal: 8.0),
                          child: Text('or', style: TextStyle(color: Colors.grey)),
                        ),
                        Expanded(child: Divider(color: Colors.grey)),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Email / Phone Field
                    const Align(
                      alignment: Alignment.centerLeft,
                      child: Text('Email or Phone Number', style: TextStyle(color: Colors.white70)),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _emailOrPhoneController,
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: const Color(0xFF374151),
                        hintText: 'Enter your email or phone number',
                        hintStyle: const TextStyle(color: Colors.grey),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      style: const TextStyle(color: Colors.white),
                    ),
                    const SizedBox(height: 16),

                    // Password Field
                    const Align(
                      alignment: Alignment.centerLeft,
                      child: Text('Password', style: TextStyle(color: Colors.white70)),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: const Color(0xFF374151),
                        hintText: 'Enter your password',
                        hintStyle: const TextStyle(color: Colors.grey),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      style: const TextStyle(color: Colors.white),
                    ),
                    const SizedBox(height: 16),

                    // Error Placeholder
                    if (_errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12.0),
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(
                            color: Colors.redAccent,
                            fontSize: 14,
                          ),
                        ),
                      ),

                    // Sign In Button
                    ElevatedButton(
                      onPressed: () {
                        final emailOrPhone = _emailOrPhoneController.text.trim();
                        final password = _passwordController.text;

                        // Simulate test users
                        final testAccounts = {
                          'john@example.com': 'pass123',
                          '5315060138': 'pass456',
                          'test@gmail.com': 'test123',
                        };

                        // Normalize phone number (remove spaces)
                        final normalizedInput = emailOrPhone.contains('@')
                            ? emailOrPhone
                            : emailOrPhone.replaceAll(' ', '');

                        if (testAccounts.containsKey(normalizedInput) &&
                            testAccounts[normalizedInput] == password) {
                          // Login successful - navigate to success page
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Login successful!')),
                          );

                          // Navigate to the success page instead of directly to survey
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(builder: (context) => const LoginSuccessPage()),
                          );
                        } else {
                          // Show error
                          setState(() {
                            _errorMessage = 'Invalid email/phone or password';
                          });
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(_errorMessage!)),
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade600,
                        minimumSize: const Size(double.infinity, 48),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: const Text('Sign in'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}