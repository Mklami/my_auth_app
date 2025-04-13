import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/semantics.dart';

// Extension to make any widget more testable
extension TestableWidgetExtension on Widget {
  Widget withTestSemantics(String testId, {String? label, String? hint, String? value}) {
    return Semantics(
      // Convert the string to a SemanticsTag
      tagForChildren: SemanticsTag(testId),
      label: label,
      hint: hint,
      value: value,
      child: this,
    );
  }
}

class SurveyPage extends StatefulWidget {
  const SurveyPage({Key? key}) : super(key: key);

  @override
  _SurveyPageState createState() => _SurveyPageState();
}

class _SurveyPageState extends State<SurveyPage> {
  final _formKey = GlobalKey<FormState>();

  // Form fields
  String _name = '';
  DateTime? _birthDate;

  // New separate date fields
  String _birthDay = '';
  String _birthMonth = '';
  String _birthYear = '';

  String _educationLevel = '';
  String _city = '';
  String _gender = '';
  Map<String, bool> _aiModels = {
    'ChatGPT': false,
    'Bard': false,
    'Claude': false,
    'Copilot': false,
    'Gemini': false,
  };
  Map<String, String> _aiModelDefects = {};
  String _beneficialUseCase = '';

  // Education level options
  final List<String> _educationLevels = [
    'High School',
    'Associate Degree',
    'Bachelor\'s Degree',
    'Master\'s Degree',
    'Doctorate',
    'Other'
  ];

  // Gender options
  final List<String> _genderOptions = ['Male', 'Female', 'Non-binary', 'Prefer not to say'];

  // Check if all required fields are filled
  bool get _isFormValid {
    // First check if all required fields have values
    bool hasRequiredFields = _name.isNotEmpty &&
        _isValidDateInput() &&
        _educationLevel.isNotEmpty &&
        _city.isNotEmpty &&
        _gender.isNotEmpty &&
        _aiModels.values.any((selected) => selected) &&
        _aiModels.entries.where((entry) => entry.value).every(
                (entry) => _aiModelDefects[entry.key]?.isNotEmpty ?? false) &&
        _beneficialUseCase.isNotEmpty;

    // If basic requirements are met, check detailed validation
    if (hasRequiredFields) {
      // Check if birth date is valid
      bool validBirthDate = _isValidBirthDate(_birthDate);

      // Check if name is valid (returns null if valid)
      bool validName = _validateName(_name) == null;

      // Check if city is valid
      bool validCity = _validateCity(_city) == null;

      // Check if each selected AI model has valid defects
      bool validAIDefects = true;
      for (var entry in _aiModels.entries) {
        if (entry.value) { // If model is selected
          if (_validateAIModelDefects(_aiModelDefects[entry.key], entry.key) != null) {
            validAIDefects = false;
            break;
          }
        }
      }

      // Check if beneficial use case is valid
      bool validUseCase = _validateBeneficialUseCase(_beneficialUseCase) == null;

      // Form is valid only if all validations pass
      return validBirthDate && validName && validCity && validAIDefects && validUseCase;
    }

    return false; // Required fields are missing
  }

  // Method to check if the date input is valid and set _birthDate
  bool _isValidDateInput() {
    if (_birthDay.isEmpty || _birthMonth.isEmpty || _birthYear.isEmpty) {
      return false;
    }

    try {
      int day = int.parse(_birthDay);
      int month = int.parse(_birthMonth);
      int year = int.parse(_birthYear);

      // Check if values are in valid ranges
      if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > DateTime.now().year) {
        return false;
      }

      // Try to create a DateTime object
      _birthDate = DateTime(year, month, day);
      return true;
    } catch (e) {
      // Invalid date format
      return false;
    }
  }

  // Validate the text field input for day
  String? _validateDay(String? value) {
    if (value == null || value.isEmpty) {
      return 'Required';
    }

    try {
      int day = int.parse(value);
      if (day < 1 || day > 31) {
        return 'Invalid';
      }
    } catch (e) {
      return 'Numbers only';
    }

    return null;
  }

  // Validate the text field input for month
  String? _validateMonth(String? value) {
    if (value == null || value.isEmpty) {
      return 'Required';
    }

    try {
      int month = int.parse(value);
      if (month < 1 || month > 12) {
        return 'Invalid';
      }
    } catch (e) {
      return 'Numbers only';
    }

    return null;
  }

  // Validate the text field input for year
  String? _validateYear(String? value) {
    if (value == null || value.isEmpty) {
      return 'Required';
    }

    try {
      int year = int.parse(value);
      if (year < 1900 || year > DateTime.now().year) {
        return 'Invalid';
      }
    } catch (e) {
      return 'Numbers only';
    }

    return null;
  }

  String? _validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your name';
    }

    // Check if name contains at least 2 words (for name and surname)
    final nameWords = value.trim().split(' ').where((word) => word.isNotEmpty).length;
    if (nameWords < 2) {
      return 'Please enter both name and surname';
    }

    // Check for reasonable length
    if (value.trim().length < 5) {
      return 'Name is too short';
    }

    return null;
  }

  bool _isValidBirthDate(DateTime? date) {
    if (date == null) return false;

    // Check if date is not in the future
    if (date.isAfter(DateTime.now())) return false;

    // Check if person is not too old (e.g., older than 120 years)
    final DateTime minReasonableDate = DateTime.now().subtract(const Duration(days: 365 * 120));
    if (date.isBefore(minReasonableDate)) return false;

    // Calculate age
    final DateTime today = DateTime.now();
    int age = today.year - date.year;
    if (today.month < date.month || (today.month == date.month && today.day < date.day)) {
      age--;
    }

    // Check if person meets minimum age requirement (10 years)
    if (age < 10) return false;

    return true;
  }

  String? _validateCity(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your city';
    }

    // Check for minimum length
    if (value.trim().length < 2) {
      return 'City name is too short';
    }

    // Optional: Validate that city contains only letters, spaces, and hyphens
    final cityRegExp = RegExp(r"^[a-zA-Z\s\-]+$");
    if (!cityRegExp.hasMatch(value)) {
      return 'City can only contain letters, spaces, and hyphens';
    }

    return null;
  }

  String? _validateAIModelDefects(String? value, String modelName) {
    if (value == null || value.isEmpty) {
      return 'Please describe defects for $modelName';
    }

    // Check for minimum length
    if (value.trim().length < 5) {
      return 'Description is too short';
    }

    return null;
  }

  String? _validateBeneficialUseCase(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please describe a beneficial use case';
    }

    // Check for minimum length
    if (value.trim().length < 10) {
      return 'Description is too short (minimum 10 characters)';
    }

    return null;
  }

  void _updateAIModelSelection(String model, bool selected) {
    setState(() {
      _aiModels[model] = selected;
      if (!selected) {
        _aiModelDefects.remove(model);
      } else if (!_aiModelDefects.containsKey(model)) {
        _aiModelDefects[model] = '';
      }
    });
  }

  Future<void> _logoutAndNavigateHome() async {
    await FirebaseAuth.instance.signOut();
    if (context.mounted) {
      Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
    }
  }

  Future<void> _submitSurvey() async {
    // Attempt to create valid birth date from inputs before submission
    if (!_isValidDateInput()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a valid birth date'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // First validate the form
    if (!(_formKey.currentState!.validate() && _isFormValid)) {
      // Show error message if form is not valid
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please fill all required fields correctly'),
          backgroundColor: Colors.red,
        ),
      );
      return;  // Exit the method early
    }

    try {
      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      // Format the data
      final surveyData = {
        'name': _name,
        'birthDate': _birthDate!.toString().split(' ')[0],
        'educationLevel': _educationLevel,
        'city': _city,
        'gender': _gender,
        'aiModels': _aiModels.entries
            .where((entry) => entry.value)
            .map((entry) => {
          'model': entry.key,
          'defects': _aiModelDefects[entry.key],
        })
            .toList(),
        'beneficialUseCase': _beneficialUseCase,
        'timestamp': FieldValue.serverTimestamp(),
        'recipientEmail': 'mayasa.naama@gmail.com', // The email to send the survey to
      };

      // Save to Firestore
      await FirebaseFirestore.instance
          .collection('survey_responses')
          .add(surveyData);

      // Close loading indicator
      Navigator.of(context).pop();

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Survey submitted successfully! Email will be sent shortly.')),
      );

      // Navigate back to login screen after successful submission
      await _logoutAndNavigateHome();
    } catch (e) {
      // Close loading indicator if it's showing
      Navigator.of(context, rootNavigator: true).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error submitting survey: $e')),
      );
    }
  }

  void _resetForm() {
    setState(() {
      _name = '';
      _birthDate = null;
      _birthDay = '';
      _birthMonth = '';
      _birthYear = '';
      _educationLevel = '';
      _city = '';
      _gender = '';
      _aiModels.forEach((key, value) {
        _aiModels[key] = false;
      });
      _aiModelDefects.clear();
      _beneficialUseCase = '';
      _formKey.currentState!.reset();
    });
  }

  @override
  Widget build(BuildContext context) {
    print('🟢 SurveyPage build() called');

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Survey'),
        actions: [
          IconButton(
              key: const Key('logoutButton'),
              tooltip: 'Logout',
              icon: const Icon(Icons.logout),
              onPressed: _logoutAndNavigateHome
          ).withTestSemantics('logoutButton', label: 'Logout Button'),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Name Field - Enhanced with Semantics for testing
              Semantics(
                label: 'Name-Surname Field',
                textField: true,
                value: _name,
                hint: 'Enter your full name',
                child: TextFormField(
                  key: const Key('nameField'),
                  decoration: const InputDecoration(
                    labelText: 'Name-Surname *',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your name';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    setState(() {
                      _name = value;
                    });
                  },
                ),
              ),
              const SizedBox(height: 16),

              // Birth Date Field - Now using separate inputs for day, month, year
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Birth Date *',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      // Day input
                      Expanded(
                        flex: 1,
                        child: Semantics(
                          label: 'Birth Day Field',
                          textField: true,
                          value: _birthDay,
                          hint: 'Enter day (1-31)',
                          child: TextFormField(
                            key: const Key('birthDayField'),
                            decoration: const InputDecoration(
                              labelText: 'Day',
                              border: OutlineInputBorder(),
                              counterText: '',
                            ),
                            keyboardType: TextInputType.number,
                            maxLength: 2,
                            validator: _validateDay,
                            onChanged: (value) {
                              setState(() {
                                _birthDay = value;
                                _isValidDateInput(); // Try to create date object
                              });
                            },
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Month input
                      Expanded(
                        flex: 1,
                        child: Semantics(
                          label: 'Birth Month Field',
                          textField: true,
                          value: _birthMonth,
                          hint: 'Enter month (1-12)',
                          child: TextFormField(
                            key: const Key('birthMonthField'),
                            decoration: const InputDecoration(
                              labelText: 'Month',
                              border: OutlineInputBorder(),
                              counterText: '',
                            ),
                            keyboardType: TextInputType.number,
                            maxLength: 2,
                            validator: _validateMonth,
                            onChanged: (value) {
                              setState(() {
                                _birthMonth = value;
                                _isValidDateInput(); // Try to create date object
                              });
                            },
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Year input
                      Expanded(
                        flex: 2,
                        child: Semantics(
                          label: 'Birth Year Field',
                          textField: true,
                          value: _birthYear,
                          hint: 'Enter year (e.g., 1990)',
                          child: TextFormField(
                            key: const Key('birthYearField'),
                            decoration: const InputDecoration(
                              labelText: 'Year',
                              border: OutlineInputBorder(),
                              counterText: '',
                            ),
                            keyboardType: TextInputType.number,
                            maxLength: 4,
                            validator: _validateYear,
                            onChanged: (value) {
                              setState(() {
                                _birthYear = value;
                                _isValidDateInput(); // Try to create date object
                              });
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (_birthDay.isNotEmpty && _birthMonth.isNotEmpty && _birthYear.isNotEmpty && !_isValidDateInput())
                    const Padding(
                      padding: EdgeInsets.only(top: 8.0),
                      child: Text(
                        'Please enter a valid date',
                        style: TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 16),

              // Education Level Field - Enhanced for testability
              Semantics(
                label: 'Education Level Dropdown',
                button: true,
                value: _educationLevel.isEmpty ? 'No selection' : _educationLevel,
                hint: 'Tap to select your education level',
                child: DropdownButtonFormField<String>(
                  key: const Key('educationField'),
                  decoration: const InputDecoration(
                    labelText: 'Education Level *',
                    border: OutlineInputBorder(),
                  ),
                  value: _educationLevel.isEmpty ? null : _educationLevel,
                  items: _educationLevels.map((String level) {
                    return DropdownMenuItem<String>(
                      value: level,
                      child: Text(level),
                    );
                  }).toList(),
                  onChanged: (String? newValue) {
                    setState(() {
                      _educationLevel = newValue ?? '';
                    });
                  },
                ),
              ),
              const SizedBox(height: 16),

              // City Field - Enhanced for testability
              Semantics(
                label: 'City Field',
                textField: true,
                value: _city,
                hint: 'Enter your city',
                child: TextFormField(
                  key: const Key('cityField'),
                  decoration: const InputDecoration(
                    labelText: 'City *',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your city';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    setState(() {
                      _city = value;
                    });
                  },
                ),
              ),
              const SizedBox(height: 16),

              // Gender Field - Enhanced for testability
              Semantics(
                label: 'Gender Selection Section',
                explicitChildNodes: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Gender *',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ...List.generate(_genderOptions.length, (index) {
                      return Semantics(
                        label: '${_genderOptions[index]} option',
                        selected: _gender == _genderOptions[index],
                        child: RadioListTile<String>(
                          key: Key('genderOption_${_genderOptions[index]}'),
                          title: Text(_genderOptions[index]),
                          value: _genderOptions[index],
                          groupValue: _gender,
                          onChanged: (String? value) {
                            setState(() {
                              _gender = value ?? '';
                            });
                          },
                        ),
                      );
                    }),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // AI Models Selection - Enhanced for testability
              Semantics(
                label: 'AI Models Section',
                explicitChildNodes: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('AI Models You\'ve Tried *',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ...List.generate(_aiModels.length, (index) {
                      String model = _aiModels.keys.elementAt(index);
                      return Column(
                        children: [
                          Semantics(
                            label: 'AI Model $model checkbox',
                            checked: _aiModels[model] ?? false,
                            child: CheckboxListTile(
                              key: Key('aiModel_$model'),
                              title: Text(model),
                              value: _aiModels[model],
                              onChanged: (bool? value) {
                                _updateAIModelSelection(model, value ?? false);
                              },
                            ),
                          ),
                          if (_aiModels[model] ?? false) ...[
                            const SizedBox(height: 8),
                            Padding(
                              padding: const EdgeInsets.only(left: 32.0, right: 16.0),
                              child: Semantics(
                                label: 'Defects of $model field',
                                textField: true,
                                value: _aiModelDefects[model] ?? '',
                                hint: 'Enter defects or cons of $model',
                                child: TextFormField(
                                  key: Key('aiModelDefects_$model'),
                                  decoration: InputDecoration(
                                    labelText: 'Defects/Cons of $model *',
                                    border: const OutlineInputBorder(),
                                  ),
                                  maxLines: 2,
                                  onChanged: (value) {
                                    setState(() {
                                      _aiModelDefects[model] = value;
                                    });
                                  },
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],
                        ],
                      );
                    }),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Beneficial Use Case Field - Enhanced for testability
              Semantics(
                label: 'Beneficial Use Case Field',
                textField: true,
                multiline: true,
                value: _beneficialUseCase,
                hint: 'Describe a beneficial use case of AI in daily life',
                child: TextFormField(
                  key: const Key('beneficialUseCaseField'),
                  decoration: const InputDecoration(
                    labelText: 'Beneficial Use Case of AI in Daily Life *',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 4,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please describe a beneficial use case';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    setState(() {
                      _beneficialUseCase = value;
                    });
                  },
                ),
              ),
              const SizedBox(height: 24),

              Center(
                child: Semantics(
                  label: 'Send button',
                  button: true,
                  enabled: true,  // Always enabled for UI accessibility
                  hint: 'Submit your survey responses',
                  child: ElevatedButton(
                    key: const Key('submitButton'),
                    onPressed: _submitSurvey,  // This will handle validation inside the method
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32.0,
                        vertical: 12.0,
                      ),
                      // Optionally change the button appearance based on form validity
                      backgroundColor: _isFormValid ? null : Colors.grey[300],
                    ),
                    child: const Text(
                      'Send',
                      style: TextStyle(fontSize: 18),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}