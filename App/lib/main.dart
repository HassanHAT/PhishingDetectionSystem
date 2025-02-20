import 'package:App/screens/register_screen.dart';
import 'package:flutter/material.dart';
import 'package:App/screens/splash_screen.dart';
import 'package:App/screens/login_screen.dart';
import 'package:App/screens/home_screen.dart';
import 'package:App/screens/check_message_screen.dart';
import 'package:App/services/notification_service.dart';

void main() async {
  runApp(const PhishingDetectorApp());
  // Initialize notifications and request permissions
  await NotificationService.initialize();
}

class PhishingDetectorApp extends StatelessWidget {
  const PhishingDetectorApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    WidgetsFlutterBinding.ensureInitialized();

    return MaterialApp(
      title: 'Phish Guard',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/splash',
      routes: {
        '/splash': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/home': (context) => const HomeScreen(),
        '/check': (context) => const CheckMessageScreen(),
      },
    );
  }
}
