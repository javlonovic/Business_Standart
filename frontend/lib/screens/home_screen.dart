import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/services_provider.dart';
import '../widgets/app_bar_widget.dart';
import '../widgets/service_card.dart';
import '../widgets/footer_widget.dart';
import '../widgets/currency_rates_widget.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: const AppBarWidget(),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Hero section
            _buildHeroSection(context),
            
            const SizedBox(height: 80),
            
            // Services section
            _buildServicesSection(context),
            
            const SizedBox(height: 80),
            
            // Currency rates widget
            const CurrencyRatesWidget(),
            
            const SizedBox(height: 80),
            
            // Footer
            const FooterWidget(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeroSection(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 80, horizontal: 24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            children: [
              Text(
                'Профессиональная оценка\nнедвижимости и бизнеса',
                style: Theme.of(context).textTheme.displayLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              Text(
                'Оценочная компания Business Standart предоставляет полный спектр оценочных услуг в Ташкенте',
                style: Theme.of(context).textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              ElevatedButton(
                onPressed: () {
                  // Navigate to calculator
                },
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('Рассчитать стоимость'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildServicesSection(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          Text(
            'Наши услуги',
            style: Theme.of(context).textTheme.displayMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 48),
          Consumer<ServicesProvider>(
            builder: (context, provider, child) {
              if (provider.isLoading) {
                return const Center(
                  child: CircularProgressIndicator(),
                );
              }
              
              if (provider.error != null) {
                return Center(
                  child: Column(
                    children: [
                      Text(
                        'Ошибка загрузки услуг',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: provider.loadServices,
                        child: const Text('Повторить'),
                      ),
                    ],
                  ),
                );
              }
              
              return LayoutBuilder(
                builder: (context, constraints) {
                  int crossAxisCount = 1;
                  if (constraints.maxWidth > 1200) {
                    crossAxisCount = 3;
                  } else if (constraints.maxWidth > 600) {
                    crossAxisCount = 2;
                  }
                  
                  return GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      childAspectRatio: 1.2,
                      crossAxisSpacing: 24,
                      mainAxisSpacing: 24,
                    ),
                    itemCount: provider.services.length,
                    itemBuilder: (context, index) {
                      return ServiceCard(service: provider.services[index]);
                    },
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }
}
