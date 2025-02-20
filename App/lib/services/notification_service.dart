import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static Future<void> initialize() async {
    // Request notification permission first
    await _requestNotificationPermission();

    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);

    await _notificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (details) {
        // Handle notification tap
      },
    );
  }

  static Future<void> _requestNotificationPermission() async {
    await Permission.notification.request();
  }

  static Future<void> showNotification(String title, String body) async {
    // Check if notifications are enabled
    if (!await Permission.notification.isGranted) {
      await _requestNotificationPermission();
      if (!await Permission.notification.isGranted) return;
    }

    const AndroidNotificationDetails androidNotificationDetails =
        AndroidNotificationDetails(
          'phish_guard_channel',
          'Phishing Alerts',
          importance: Importance.max,
          priority: Priority.high,
          showWhen: true,
          enableVibration: true,
          playSound: true,
        );

    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidNotificationDetails,
    );

    await _notificationsPlugin.show(
      0,
      title,
      body,
      notificationDetails,
      payload: 'phishing_alert',
    );
  }
}
