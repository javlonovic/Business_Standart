/// Модель курса валюты
class CurrencyRate {
  final int id;
  final String currencyCode;
  final double rate;
  final double change;
  final DateTime date;

  const CurrencyRate({
    required this.id,
    required this.currencyCode,
    required this.rate,
    required this.change,
    required this.date,
  });

  factory CurrencyRate.fromJson(Map<String, dynamic> json) {
    return CurrencyRate(
      id: json['id'] as int,
      currencyCode: json['currency_code'] as String,
      rate: double.parse(json['rate'].toString()),
      change: double.parse(json['change'].toString()),
      date: DateTime.parse(json['date'] as String),
    );
  }

  /// Положительное изменение — курс вырос
  bool get isPositiveChange => change > 0;

  /// Нулевое изменение — без изменений
  bool get isZeroChange => change == 0;
}

/// Ответ виджета курсов валют
class CurrencyRatesWidget {
  final List<CurrencyRate> rates;
  final bool cached;
  final DateTime? updatedAt;

  const CurrencyRatesWidget({
    required this.rates,
    required this.cached,
    this.updatedAt,
  });

  factory CurrencyRatesWidget.fromJson(Map<String, dynamic> json) {
    return CurrencyRatesWidget(
      rates: (json['rates'] as List)
          .map((r) => CurrencyRate.fromJson(r as Map<String, dynamic>))
          .toList(),
      cached: json['cached'] as bool? ?? false,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }
}

/// Ответ истории курсов
class CurrencyRatesHistory {
  final String currencyCode;
  final List<CurrencyRate> items;
  final int total;
  final int days;

  const CurrencyRatesHistory({
    required this.currencyCode,
    required this.items,
    required this.total,
    required this.days,
  });

  factory CurrencyRatesHistory.fromJson(Map<String, dynamic> json) {
    return CurrencyRatesHistory(
      currencyCode: json['currency_code'] as String,
      items: (json['items'] as List)
          .map((r) => CurrencyRate.fromJson(r as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int,
      days: json['days'] as int,
    );
  }
}
