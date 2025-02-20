import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/message_model.dart';
import 'auth_service.dart';

class PhishingService {
  final AuthService _authService = AuthService();

  Future<List<Message>> getUserMessages() async {
    final userId = await _authService.getUserId();
    if (userId == null) return [];

    final uri = Uri.parse('${ApiConfig.baseUrl}/api/users/$userId/messages');
    final resp = await http.get(uri);

    if (resp.statusCode != 200) {
      print('Failed to fetch messages: ${resp.statusCode}');
      return [];
    }

    final data = jsonDecode(resp.body) as Map<String, dynamic>;
    final list = data['results'] as List<dynamic>? ?? [];
    return list
        .map((j) => Message.fromJson(j as Map<String, dynamic>))
        .toList();
  }

  Future<Message> checkMessage(String message) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/api/phishing/check');
    final resp = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'messages': [message],
      }),
    );

    if (resp.statusCode != 200) {
      throw Exception('Phishing check failed: ${resp.statusCode}');
    }

    final body = jsonDecode(resp.body) as Map<String, dynamic>;
    final results = (body['results'] as List<dynamic>? ?? []);
    if (results.isEmpty) {
      throw Exception('No results returned from phishing check.');
    }

    return Message.fromJson(results[0] as Map<String, dynamic>);
  }

  Future<void> saveMessageToDatabase({
    required String userId,
    required String messageText,
    required double probability,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/api/users/$userId/messages'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': messageText, 'probability': probability}),
      );

      print('Save message response: ${response.statusCode} ${response.body}');
      if (response.statusCode != 201) {
        throw Exception('Failed to save message: ${response.body}');
      }
    } catch (e) {
      print('Error saving message: $e');
      rethrow;
    }
  }

  /// Deletes a specific message for this user.
  Future<void> deleteMessage(int messageId) async {
    final userId = await _authService.getUserId();
    if (userId == null) return;

    final uri = Uri.parse(
      '${ApiConfig.baseUrl}/api/users/$userId/messages/$messageId',
    );
    final resp = await http.delete(uri);

    if (resp.statusCode != 200) {
      print('Failed to delete message: ${resp.statusCode}');
      throw Exception('Delete failed');
    }
  }

  /// Deletes all messages for this user.
  Future<void> deleteAllMessages() async {
    final userId = await _authService.getUserId();
    if (userId == null) return;

    final uri = Uri.parse('${ApiConfig.baseUrl}/api/users/$userId/messages');
    final resp = await http.delete(uri);

    if (resp.statusCode != 200) {
      print('Failed to delete all messages: ${resp.statusCode}');
      throw Exception('Bulk delete failed');
    }
  }
}
