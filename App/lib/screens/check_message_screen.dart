import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/message_model.dart';
import '../services/phishing_service.dart';
import '../widgets/bottom_nav_bar.dart';

class CheckMessageScreen extends StatefulWidget {
  const CheckMessageScreen({Key? key}) : super(key: key);

  @override
  _CheckMessageScreenState createState() => _CheckMessageScreenState();
}

class _CheckMessageScreenState extends State<CheckMessageScreen> {
  final formKey = GlobalKey<FormState>();
  final TextEditingController messageController =
      TextEditingController(); //controller editor for text
  final PhishingService phishingService = PhishingService();
  //track if api is in progress requesting and updating page
  bool isLoading = false;
  bool hasResult = false;
  late Message _result;
  String errorMessage = '';

  Future<void> _checkMessage() async {
    if (!formKey.currentState!.validate()) return;

    setState(() {
      isLoading = true;
      hasResult = false;
      errorMessage = '';
    });

    try {
      final message = messageController.text;
      final result = await phishingService.checkMessage(message);
      //update interface to show loading
      setState(() {
        _result = result;
        hasResult = true;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'Failed to check message: ${e.toString()}';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Check Message')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Form(
              key: formKey,
              child: TextFormField(
                controller: messageController,
                keyboardType: TextInputType.multiline,
                maxLines: null,
                minLines: 5,
                decoration: const InputDecoration(
                  labelText: 'Enter a message to check',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: isLoading ? null : _checkMessage,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
              ),
              child:
                  isLoading
                      ? const CircularProgressIndicator(
                        color: Color.fromARGB(255, 178, 178, 178),
                      )
                      : const Text('Check Message'),
            ),
            const SizedBox(height: 24),
            if (errorMessage.isNotEmpty)
              Text(errorMessage, style: const TextStyle(color: Colors.red)),
            if (hasResult) ...[
              const SizedBox(height: 16),
              const Text(
                'Phishing Message Prediction:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Text(
                            'Result: ${_result.risk.displayText.toUpperCase()} \nRisk: ${_result.risk.level.toUpperCase()}',
                            style: TextStyle(
                              color: _result.risk.color,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Text(
                        'Detected on: ${DateFormat('MMM dd, yyyy HH:mm').format(_result.timestamp)}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color.fromARGB(255, 0, 0, 0),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 1),
    );
  }
}
