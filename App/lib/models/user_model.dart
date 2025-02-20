class User {
  final int userId;
  final String password;

  User({required this.userId, required this.password});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(userId: json['user_id'], password: json['password']);
  }

  Map<String, dynamic> toJson() {
    return {'user_id': userId, 'password': password};
  }
}
