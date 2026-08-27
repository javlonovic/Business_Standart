import 'package:flutter/material.dart';

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
        const SizedBox(width: 24),
      ],
    );
  }
}
