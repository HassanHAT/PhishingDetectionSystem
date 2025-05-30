import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class BottomNavBar extends StatelessWidget {
  final int currentIndex;

  const BottomNavBar({Key? key, required this.currentIndex}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
        BottomNavigationBarItem(
          icon: Icon(Icons.search),
          label: 'Check Message',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.account_circle),
          label: 'Account',
        ),
      ],
      onTap: (index) {
        if (index == currentIndex) return;

        if (index == 0) {
          Navigator.of(context).pushReplacementNamed('/home');
        } else if (index == 1) {
          Navigator.of(context).pushReplacementNamed('/check');
        } else if (index == 2) {
          showAccountDialog(context);
        }
      },
    );
  }

  Future<void> showAccountDialog(BuildContext context) async {
    final AuthService authService = AuthService();
    final String? userEmail = await authService.getUserEmail();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Account'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${userEmail ?? 'Not available'}',
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 20),
              const Text('What would you like to do?'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop();
                final AuthService authService = AuthService();
                await authService.logout();
                Navigator.of(context).pushReplacementNamed('/login');
              },
              child: const Text('Log Out'),
            ),
            TextButton(
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              onPressed: () => confirmDeleteAccount(context),
              child: const Text('Delete Account'),
            ),
          ],
        );
      },
    );
  }

  void confirmDeleteAccount(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Account'),
          content: const Text('Are you sure you want to delete your account?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              onPressed: () async {
                Navigator.of(context).pop();
                final AuthService authService = AuthService();
                final success = await authService.deleteAccount();

                if (success) {
                  // Explicitly clear the user session
                  await authService.logout();

                  // Navigate to login page
                  Navigator.of(context).pushNamedAndRemoveUntil(
                    '/login',
                    (route) => false, // Remove all previous routes
                  );

                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Account deleted successfully'),
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Failed to delete account')),
                  );
                }
              },
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }
}
