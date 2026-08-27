import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/currency_rate.dart';
import '../providers/currency_rates_provider.dart';

/// Виджет курсов валют для главной страницы.
/// Отображает 5 валют с курсом, изменением и датой.
/// Автоматически обновляется каждые 10 минут.
class CurrencyRatesWidget extends StatefulWidget {
  const CurrencyRatesWidget({super.key});

  @override
  State<CurrencyRatesWidget> createState() => _CurrencyRatesWidgetState();
}

class _CurrencyRatesWidgetState extends State<CurrencyRatesWidget> {
  @override
  void initState() {
    super.initState();
    // Загружаем данные при первом показе
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CurrencyRatesProvider>().loadWidgetRates();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 24),
      color: AppTheme.primaryColor.withOpacity(0.03),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              const SizedBox(height: 24),
              _buildRatesContent(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Consumer<CurrencyRatesProvider>(
      builder: (context, provider, _) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Курсы валют ЦБУ',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                if (provider.lastUpdated != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Обновлено: ${DateFormat('dd.MM.yyyy').format(provider.lastUpdated!)}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
              ],
            ),
            Row(
              children: [
                // Кнопка обновления
                IconButton(
                  onPressed: provider.isLoadingWidget
                      ? null
                      : () => context.read<CurrencyRatesProvider>().loadWidgetRates(),
                  icon: provider.isLoadingWidget
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.refresh, size: 20),
                  tooltip: 'Обновить',
                ),
                const SizedBox(width: 8),
                // Ссылка на архив
                TextButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/currency-archive'),
                  icon: const Icon(Icons.history, size: 16),
                  label: const Text('История'),
                  style: TextButton.styleFrom(
                    foregroundColor: AppTheme.primaryColor,
                  ),
                ),
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildRatesContent(BuildContext context) {
    return Consumer<CurrencyRatesProvider>(
      builder: (context, provider, _) {
        // Ошибка
        if (provider.widgetError != null && provider.widgetRates.isEmpty) {
          return _buildError(context, provider);
        }

        // Загрузка (первичная)
        if (provider.isLoadingWidget && provider.widgetRates.isEmpty) {
          return _buildSkeleton();
        }

        // Нет данных
        if (provider.widgetRates.isEmpty) {
          return _buildEmpty(context);
        }

        // Данные есть
        return _buildRatesGrid(context, provider.widgetRates);
      },
    );
  }

  Widget _buildRatesGrid(BuildContext context, List<CurrencyRate> rates) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isNarrow = constraints.maxWidth < 600;
        final isMedium = constraints.maxWidth < 900;

        int crossAxisCount;
        if (isNarrow) {
          crossAxisCount = 2;
        } else if (isMedium) {
          crossAxisCount = 3;
        } else {
          crossAxisCount = 5;
        }

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            childAspectRatio: isNarrow ? 1.3 : 1.8,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
          ),
          itemCount: rates.length,
          itemBuilder: (context, index) => _CurrencyRateCard(rate: rates[index]),
        );
      },
    );
  }

  Widget _buildSkeleton() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 5,
        childAspectRatio: 1.8,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: 5,
      itemBuilder: (_, __) => _SkeletonCard(),
    );
  }

  Widget _buildError(BuildContext context, CurrencyRatesProvider provider) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.errorColor.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: AppTheme.errorColor),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              provider.widgetError!,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          TextButton(
            onPressed: () => provider.loadWidgetRates(),
            child: const Text('Повторить'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmpty(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: Text(
          'Данные о курсах валют временно недоступны',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ),
    );
  }
}

/// Карточка одной валюты
class _CurrencyRateCard extends StatelessWidget {
  final CurrencyRate rate;

  const _CurrencyRateCard({required this.rate});

  @override
  Widget build(BuildContext context) {
    final changeColor = rate.isZeroChange
        ? AppTheme.textSecondary
        : rate.isPositiveChange
            ? const Color(0xFF27AE60) // зелёный — рост
            : const Color(0xFFE74C3C); // красный — падение

    final changeIcon = rate.isZeroChange
        ? Icons.remove
        : rate.isPositiveChange
            ? Icons.arrow_upward
            : Icons.arrow_downward;

    final rateFormatter = NumberFormat('#,##0.##', 'ru_RU');
    final changeFormatter = NumberFormat('+#,##0.##;-#,##0.##', 'ru_RU');

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Код валюты
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                rate.currencyCode,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppTheme.primaryColor,
                    ),
              ),
              Icon(changeIcon, color: changeColor, size: 16),
            ],
          ),

          const SizedBox(height: 8),

          // Курс
          Text(
            '${rateFormatter.format(rate.rate)} сум',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),

          const SizedBox(height: 4),

          // Изменение
          Text(
            rate.isZeroChange ? '—' : changeFormatter.format(rate.change),
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: changeColor,
                  fontWeight: FontWeight.w500,
                ),
          ),
        ],
      ),
    );
  }
}

/// Плейсхолдер-карточка во время загрузки
class _SkeletonCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          _SkeletonLine(width: 48, height: 20),
          _SkeletonLine(width: 100, height: 18),
          _SkeletonLine(width: 64, height: 14),
        ],
      ),
    );
  }
}

class _SkeletonLine extends StatelessWidget {
  final double width;
  final double height;

  const _SkeletonLine({required this.width, required this.height});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.grey.shade200,
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }
}
