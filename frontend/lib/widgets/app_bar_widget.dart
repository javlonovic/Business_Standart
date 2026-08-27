import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../core/theme.dart';

class AppBarWidget extends StatelessWidget implements PreferredSizeWidget {
  const AppBarWidget({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(70);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      title: Row(
        children: [
          Text(
            'BUSINESS STANDART',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pushNamed(context, '/'),
          child: const Text('Главная'),
        ),
        TextButton(
          onPressed: () => Navigator.pushNamed(context, '/about'),
          child: const Text('О компании'),
        ),
        TextButton(
          onPressed: () => Navigator.pushNamed(context, '/services'),
          child: const Text('Услуги'),
        ),
        TextButton(
          onPressed: () => Navigator.pushNamed(context, '/calculator'),
          child: const Text('Калькулятор'),
        ),
        TextButton(
          onPressed: () => Navigator.pushNamed(context, '/contacts'),
          child: const Text('Контакты'),
        ),
        const SizedBox(width: 16),
        
        // Auth buttons
        Consumer<AuthProvider>(
          builder: (context, authProvider, _) {
            if (authProvider.isLoading) {
              return const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              );
            }
            
            if (authProvider.isAuthenticated) {
              return Row(
                children: [
                  TextButton.icon(
                    onPressed: () => Navigator.pushNamed(context, '/cabinet'),
                    icon: const Icon(Icons.person),
                    label: Text(
                      authProvider.currentUser?['full_name']?.split(' ')[0] ?? 'Кабинет',
                    ),
                    style: TextButton.styleFrom(
                      foregroundColor: AppTheme.accentColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
              );
            }
            
            return Row(
              children: [
                TextButton(
                  onPressed: () => Navigator.pushNamed(context, '/login'),
                  child: const Text('Войти'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, '/register'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentColor,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Регистрация'),
                ),
                const SizedBox(width: 16),
              ],
            );
          },
        ),
      ],
    );
  }
}
