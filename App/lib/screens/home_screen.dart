import 'dart:async';
import 'package:flutter/material.dart';
import 'package:another_telephony/telephony.dart';
import '../models/message_model.dart';
import '../services/phishing_service.dart';
import '../services/auth_service.dart';
import '../widgets/bottom_nav_bar.dart';
import '../services/notification_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  HomeScreenState createState() => HomeScreenState();
}

//create instance of every class needed
class HomeScreenState extends State<HomeScreen> {
  final PhishingService phishingService = PhishingService();
  final AuthService authService = AuthService();
  final Telephony telephony = Telephony.instance;

  bool isLoading = false;
  String errorMessage = '';
  List<Message> messages = [];
  //intiallize the page for widget
  @override
  void initState() {
    super.initState();
    requestSmsPermissions();
    startListening();
    loadMessages();
  }

  //Reguest SMS Permission for user when first sign in for application
  Future<void> requestSmsPermissions() async {
    final granted = await telephony.requestPhoneAndSmsPermissions;
    if (granted != true) {
      setState(() => errorMessage = 'SMS permissions are required.');
    }
  }

  //load messages from database for user
  Future<void> loadMessages() async {
    if (!mounted) return;
    setState(() {
      isLoading = true;
      errorMessage = '';
    });

    try {
      final msgs =
          await phishingService.getUserMessages(); //fetch messages for user
      setState(() {
        messages = msgs.where((m) => m.risk.level != 'low').toList();
      });
    } catch (e) {
      setState(() => errorMessage = 'Failed to load messages: $e');
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  //listener for incoming messages
  void startListening() {
    telephony.listenIncomingSms(
      onNewMessage: (SmsMessage sms) async {
        //callback when message is received
        if (sms.body == null) return;
        final body = sms.body!;

        setState(() => isLoading = true);
        try {
          final result = await phishingService.checkMessage(
            body,
          ); //check for phishing

          if (result.risk.level != 'low') {
            //if not low risk save it and notify alert
            await NotificationService.showNotification(
              //show notification from the class if phishing
              'Potential Phishing Detected!',
              '${result.risk.level.toUpperCase()} risk message: ${result.text.substring(0, 30)}...',
            );

            final userId = await authService.getUserId();
            if (userId != null) {
              await phishingService.saveMessageToDatabase(
                //save message to database
                userId: userId,
                messageText: result.text,
                probability: result.probability,
              );
              await loadMessages();
            }
          }
        } catch (e) {
          print('Error processing SMS: $e');
          setState(() => errorMessage = 'Error processing SMS: $e');
        } finally {
          if (mounted) setState(() => isLoading = false);
        }
      },
      listenInBackground: false,
    );
  }

  //ui page build
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PHISH GUARD'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: isLoading ? null : loadMessages,
            tooltip: 'Refresh messages',
          ),
          IconButton(
            icon: const Icon(Icons.delete_forever),
            tooltip: 'Delete all messages',
            onPressed: () async {
              await phishingService
                  .deleteAllMessages(); //icon for delete all messages when pressed
              await loadMessages();
            },
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: const BottomNavBar(currentIndex: 0),
    );
  }

  //build page based on current state
  Widget _buildBody() {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (errorMessage.isNotEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            errorMessage,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    if (messages.isEmpty) {
      return const Center(
        child: Text(
          'No risky messages detected',
          style: TextStyle(fontSize: 18),
        ),
      );
    }
    //lists of messages shown to user
    return ListView.separated(
      padding: const EdgeInsets.all(8),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return Container(
          decoration: BoxDecoration(
            //border in the left indicate the levels of risk for each message
            border: Border(
              left: BorderSide(color: message.risk.color, width: 10),
            ),
          ),
          child: Card(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: ListTile(
              title: Text(
                message.text,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              subtitle: Text(
                'Result: ${message.risk.displayText.toUpperCase()} \nRisk: ${message.risk.level.toUpperCase()}',
                style: TextStyle(color: message.risk.color),
              ),
            ),
          ),
        );
      },
      separatorBuilder: (context, index) => const Divider(),
    );
  }
}
