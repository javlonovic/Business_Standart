import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'providers/auth_provider.dart';
import 'providers/services_provider.dart';
import 'providers/currency_rates_provider.dart';
import 'screens/home_screen.dart';
import 'screens/about_screen.dart';
import 'screens/services_screen.dart';
import 'screens/contacts_screen.dart';
import 'screens/archive_screen.dart';
import 'screens/calculator_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/cabinet_screen.dart';
import 'screens/order_detail_screen.dart';
import 'screens/payment_screen.dart';
import 'core/theme.dart';

void main() {
  runApp(const BusinessStandartApp());
}

class BusinessStandartApp extends StatelessWidget {
  const BusinessStandartApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    
    return MultiProvider(
      providers: [
        Provider.value(value: apiService),
        ChangeNotifierProvider(create: (_) => AuthProvider(apiService)),
        ChangeNotifierProvider(create: (_) => ServicesProvider(apiService)),
        ChangeNotifierProvider(create: (_) => CurrencyRatesProvider(apiService)),
      ],
      child: MaterialApp(
        title: 'Business Standart',
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        initialRoute: '/',
        routes: {
          '/': (context) => const HomeScreen(),
          '/about': (context) => const AboutScreen(),
          '/services': (context) => const ServicesScreen(),
          '/contacts': (context) => const ContactsScreen(),
          '/currency-archive': (context) => const ArchiveScreen(),
          '/calculator': (context) => const CalculatorScreen(),
          '/login': (context) => const LoginScreen(),
          '/register': (context) => const RegisterScreen(),
          '/cabinet': (context) => const CabinetScreen(),
        },
        onGenerateRoute: (settings) {
          // Handle dynamic routes
          if (settings.name == '/order-details') {
            final orderId = settings.arguments as int;
            return MaterialPageRoute(
              builder: (context) => OrderDetailScreen(orderId: orderId),
            );
          }
          
          if (settings.name == '/payment') {
            final args = settings.arguments as Map<String, dynamic>;
            return MaterialPageRoute(
              builder: (context) => PaymentScreen(
                orderId: args['orderId'] as int,
                amount: args['amount'] as double,
              ),
            );
          }
          
          return null;
        },
      ),
    );
  }
}
