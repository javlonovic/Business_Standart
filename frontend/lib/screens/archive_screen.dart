import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../models/currency_rate.dart';
import '../providers/currency_rates_provider.dart';
import '../widgets/app_bar_widget.dart';
import '../widgets/footer_widget.dart';

/// Страница архива курсов валют.
/// Позволяет выбрать валюту и период, показывает таблицу с историей.
class ArchiveScreen extends StatefulWidget {
  const ArchiveScreen({super.key});

  @override
  State<ArchiveScreen> createState() => _ArchiveScreenState();
}

class _ArchiveScreenState extends State<ArchiveScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CurrencyRatesProvider>().loadHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: const AppBarWidget(),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPageHeader(context),
            _buildFilters(context),
            _buildContent(context),
            const FooterWidget(),
          ],
        ),
      ),
    );
  }

  Widget _buildPageHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 48, 24, 0),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Хлебные крошки
              Row(
                children: [
                  InkWell(
                    onTap: () => Navigator.pushNamedAndRemoveUntil(
                      context,
                      '/',
                      (route) => false,
                    ),
                    child: Text(
                      'Главная',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.primaryColor,
                          ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: Icon(
                      Icons.chevron_right,
                      size: 16,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                  Text(
                    'Курсы валют',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                'Архив курсов валют ЦБУ',
                style: Theme.of(context).textTheme.displayMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Официальные курсы Центрального банка Республики Узбекистан',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFilters(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      color: Colors.white,
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Consumer<CurrencyRatesProvider>(
            builder: (context, provider, _) {
              return Wrap(
                spacing: 16,
                runSpacing: 16,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  // Выбор валюты
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Валюта',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                      const SizedBox(height: 8),
                      _CurrencyDropdown(
                        value: provider.selectedCurrency,
                        onChanged: (value) {
                          if (value != null) provider.changeCurrency(value);
                        },
                      ),
                    ],
                  ),

                  // Выбор периода
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Период',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                      const SizedBox(height: 8),
                      _PeriodSelector(
                        selectedDays: provider.selectedDays,
                        onChanged: provider.changeDays,
                      ),
                    ],
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 48),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Consumer<CurrencyRatesProvider>(
            builder: (context, provider, _) {
              // Загрузка
              if (provider.isLoadingHistory) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 64),
                  child: Center(child: CircularProgressIndicator()),
                );
              }

              // Ошибка
              if (provider.historyError != null) {
                return _buildError(context, provider);
              }

              // Нет данных
              final history = provider.history;
              if (history == null || history.items.isEmpty) {
                return _buildEmpty(context);
              }

              return _buildHistoryTable(context, history.items, provider.selectedCurrency);
            },
          ),
        ),
      ),
    );
  }

  Widget _buildHistoryTable(
    BuildContext context,
    List<CurrencyRate> items,
    String currency,
  ) {
    final rateFormatter = NumberFormat('#,##0.##', 'ru_RU');
    final changeFormatter = NumberFormat('+#,##0.##;-#,##0.##', 'ru_RU');
    final dateFormatter = DateFormat('dd.MM.yyyy');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Показано ${items.length} записей · $currency к узбекскому суму',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                headingRowColor: WidgetStateProperty.all(
                  AppTheme.primaryColor.withOpacity(0.05),
                ),
                columnSpacing: 32,
                columns: const [
                  DataColumn(label: Text('Дата')),
                  DataColumn(label: Text('Валюта'), numeric: false),
                  DataColumn(label: Text('Курс (сум)'), numeric: true),
                  DataColumn(label: Text('Изменение'), numeric: true),
                ],
                rows: items.map((rate) {
                  final changeColor = rate.isZeroChange
                      ? AppTheme.textSecondary
                      : rate.isPositiveChange
                          ? const Color(0xFF27AE60)
                          : const Color(0xFFE74C3C);

                  return DataRow(cells: [
                    DataCell(Text(dateFormatter.format(rate.date))),
                    DataCell(
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              rate.currencyCode,
                              style: TextStyle(
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    DataCell(
                      Text(
                        rateFormatter.format(rate.rate),
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                    ),
                    DataCell(
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (!rate.isZeroChange)
                            Icon(
                              rate.isPositiveChange
                                  ? Icons.arrow_upward
                                  : Icons.arrow_downward,
                              size: 14,
                              color: changeColor,
                            ),
                          const SizedBox(width: 4),
                          Text(
                            rate.isZeroChange
                                ? '—'
                                : changeFormatter.format(rate.change),
                            style: TextStyle(
                              color: changeColor,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ]);
                }).toList(),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildError(BuildContext context, CurrencyRatesProvider provider) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 64),
      child: Center(
        child: Column(
          children: [
            Icon(Icons.error_outline, size: 48, color: AppTheme.errorColor),
            const SizedBox(height: 16),
            Text(
              provider.historyError!,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => provider.loadHistory(),
              icon: const Icon(Icons.refresh),
              label: const Text('Повторить'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmpty(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 64),
      child: Center(
        child: Column(
          children: [
            Icon(Icons.bar_chart, size: 48, color: AppTheme.textSecondary),
            const SizedBox(height: 16),
            Text(
              'Нет данных за выбранный период',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Попробуйте выбрать другую валюту или расширить период',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

/// Дропдаун для выбора валюты
class _CurrencyDropdown extends StatelessWidget {
  final String value;
  final ValueChanged<String?> onChanged;

  const _CurrencyDropdown({
    required this.value,
    required this.onChanged,
  });

  static const Map<String, String> _currencyNames = {
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'RUB': '🇷🇺 Российский рубль',
    'GBP': '🇬🇧 Британский фунт',
    'CNY': '🇨🇳 Китайский юань',
  };

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          onChanged: onChanged,
          items: CurrencyRatesProvider.availableCurrencies
              .map(
                (code) => DropdownMenuItem(
                  value: code,
                  child: Text(_currencyNames[code] ?? code),
                ),
              )
              .toList(),
        ),
      ),
    );
  }
}

/// Кнопки для выбора периода
class _PeriodSelector extends StatelessWidget {
  final int selectedDays;
  final ValueChanged<int> onChanged;

  const _PeriodSelector({
    required this.selectedDays,
    required this.onChanged,
  });

  static const Map<int, String> _labels = {
    7: '7 дней',
    14: '14 дней',
    30: '30 дней',
    60: '60 дней',
    90: '90 дней',
  };

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: CurrencyRatesProvider.availableDays.map((days) {
        final isSelected = days == selectedDays;
        return InkWell(
          onTap: () => onChanged(days),
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.primaryColor : Colors.white,
              border: Border.all(
                color: isSelected ? AppTheme.primaryColor : Colors.grey.shade300,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              _labels[days] ?? '$days дней',
              style: TextStyle(
                color: isSelected ? Colors.white : AppTheme.textPrimary,
                fontWeight:
                    isSelected ? FontWeight.w600 : FontWeight.normal,
                fontSize: 14,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
