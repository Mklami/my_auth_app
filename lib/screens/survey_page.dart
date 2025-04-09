import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:cloud_firestore/cloud_firestore.dart';


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
    return _name.isNotEmpty &&
        _birthDate != null &&
        _educationLevel.isNotEmpty &&
        _city.isNotEmpty &&
        _gender.isNotEmpty &&
        _aiModels.values.any((selected) => selected) &&
        _aiModels.entries.where((entry) => entry.value).every(
                (entry) => _aiModelDefects[entry.key]?.isNotEmpty ?? false) &&
        _beneficialUseCase.isNotEmpty;
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _birthDate ?? DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );

    if (picked != null && picked != _birthDate) {
      setState(() {
        _birthDate = picked;
      });
    }
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

  Future<void> _submitSurvey() async {
    if (_formKey.currentState!.validate() && _isFormValid) {
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

        // Clear form
        _resetForm();
      } catch (e) {
        // Close loading indicator if it's showing
        Navigator.of(context, rootNavigator: true).pop();

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error submitting survey: $e')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all required fields')),
      );
    }
  }

  void _resetForm() {
    setState(() {
      _name = '';
      _birthDate = null;
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
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Name Field
              TextFormField(
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
              const SizedBox(height: 16),

              // Birth Date Field
              InkWell(
                key: const Key('birthDateField'),
                onTap: () => _selectDate(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Birth Date *',
                    border: OutlineInputBorder(),
                  ),
                  child: Text(
                    _birthDate == null
                        ? 'Select Date'
                        : DateFormat('yyyy-MM-dd').format(_birthDate!),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Education Level Field
              DropdownButtonFormField<String>(
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
              const SizedBox(height: 16),

              // City Field
              TextFormField(
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
              const SizedBox(height: 16),

              // Gender Field
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Gender *',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  ...List.generate(_genderOptions.length, (index) {
                    return RadioListTile<String>(
                      key: Key('genderOption_${_genderOptions[index]}'),
                      title: Text(_genderOptions[index]),
                      value: _genderOptions[index],
                      groupValue: _gender,
                      onChanged: (String? value) {
                        setState(() {
                          _gender = value ?? '';
                        });
                      },
                    );
                  }),
                ],
              ),
              const SizedBox(height: 16),

              // AI Models Selection
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('AI Models You\'ve Tried *',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  ...List.generate(_aiModels.length, (index) {
                    String model = _aiModels.keys.elementAt(index);
                    return Column(
                      children: [
                        CheckboxListTile(
                          key: Key('aiModel_$model'),
                          title: Text(model),
                          value: _aiModels[model],
                          onChanged: (bool? value) {
                            _updateAIModelSelection(model, value ?? false);
                          },
                        ),
                        if (_aiModels[model] ?? false) ...[
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.only(left: 32.0, right: 16.0),
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
                          const SizedBox(height: 16),
                        ],
                      ],
                    );
                  }),
                ],
              ),
              const SizedBox(height: 16),

              // Beneficial Use Case Field
              TextFormField(
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
              const SizedBox(height: 24),

              // Submit Button - only appears when all fields are filled
              if (_isFormValid)
                Center(
                  child: ElevatedButton(
                    key: const Key('submitButton'),
                    onPressed: _submitSurvey,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32.0,
                        vertical: 12.0,
                      ),
                    ),
                    child: const Text(
                      'Send',
                      style: TextStyle(fontSize: 18),
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