import 'package:flutter/material.dart';

// Message class to represent pishing results
class Message {
  final int messageId;
  final String text;
  final double probability;
  final RiskLevel risk;
  final DateTime timestamp;

  Message({
    required this.messageId,
    required this.text,
    required this.probability,
    DateTime? timestamp,
    RiskLevel? risk,
  }) : risk = risk ?? calculateRisk(probability),
       timestamp = timestamp ?? DateTime.now();
  //Extract result and use null checker if missing
  factory Message.fromJson(Map<String, dynamic> json) {
    final text = json['message']?.toString() ?? 'Unknown message';
    final prob = (json['probability'] as num?)?.toDouble() ?? 0.0;

    final riskJson = json['risk'] as Map<String, dynamic>? ?? {};
    final level = riskJson['level']?.toString() ?? 'low';
    final color = RiskLevel.getRiskColor(level);
    final displayText = RiskLevel.getRiskDisplayText(level);

    return Message(
      messageId: json['message_id'] ?? 0,
      text: text,
      probability: prob,
      risk: RiskLevel(level: level, color: color, displayText: displayText),
      timestamp: DateTime.now(),
    );
  }

  //Static method to represent risks reuslts with color, levels and text to dispplay
  static RiskLevel calculateRisk(double probability) {
    if (probability > 15) {
      return RiskLevel(
        level: 'high',
        color: Colors.red,
        displayText: 'Phishing',
      );
    }
    if (probability > 10) {
      return RiskLevel(
        level: 'medium',
        color: const Color.fromARGB(144, 152, 129, 2),
        displayText: 'Possible Phishing',
      );
    }
    return RiskLevel(level: 'low', color: Colors.green, displayText: 'Safe');
  }
}

class RiskLevel {
  final String level;
  final Color color;
  final String displayText;

  RiskLevel({
    required this.level,
    required this.color,
    required this.displayText,
  });

  static Color getRiskColor(String level) {
    switch (level.toLowerCase()) {
      case 'high':
        return Colors.red;
      case 'medium':
        return const Color.fromARGB(144, 132, 112, 1);
      default:
        return Colors.green;
    }
  }

  static String getRiskDisplayText(String level) {
    switch (level.toLowerCase()) {
      case 'high':
        return 'Phishing';
      case 'medium':
        return 'Possible Phishing';
      default:
        return 'Safe';
    }
  }
}
