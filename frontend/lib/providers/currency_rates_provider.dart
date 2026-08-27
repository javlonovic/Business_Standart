import 'dart:async';
import 'package:flutter/material.dart';
import '../models/currency_rate.dart';
import '../services/api_service.dart';

/// Provider для управления курсами валют.
/// Автоматически обновляет данные каждые 10 минут.
class CurrencyRatesProvider extends ChangeNotifier {
  final ApiService _apiService;

  CurrencyRatesProvider(this._apiService) {
    loadWidgetRates();
    _startAutoRefresh();
  }

  // --- Состояние виджета ---
  List<CurrencyRate> _widgetRates = [];
  bool _isLoadingWidget = false;
  String? _widgetError;
  DateTime? _lastUpdated;

  List<CurrencyRate> get widgetRates => _widgetRates;
  bool get isLoadingWidget => _isLoadingWidget;
  String? get widgetError => _widgetError;
  DateTime? get lastUpdated => _lastUpdated;

  // --- Состояние истории ---
  CurrencyRatesHistory? _history;
  bool _isLoadingHistory = false;
  String? _historyError;
  String _selectedCurrency = 'USD';
  int _selectedDays = 30;

  CurrencyRatesHistory? get history => _history;
  bool get isLoadingHistory => _isLoadingHistory;
  String? get historyError => _historyError;
  String get selectedCurrency => _selectedCurrency;
  int get selectedDays => _selectedDays;

  Timer? _refreshTimer;

  // Доступные валюты
  static const List<String> availableCurrencies = [
    'USD',
    'EUR',
    'RUB',
    'GBP',
    'CNY',
  ];

  // Доступные периоды
  static const List<int> availableDays = [7, 14, 30, 60, 90];

  /// Загрузить данные для виджета главной страницы
  Future<void> loadWidgetRates() async {
    _isLoadingWidget = true;
    _widgetError = null;
    notifyListeners();

    try {
      final result = await _apiService.getCurrencyRatesWidget();
      _widgetRates = result.rates;
      _lastUpdated = result.updatedAt;
      _widgetError = null;
    } catch (e) {
      _widgetError = 'Не удалось загрузить курсы валют';
    } finally {
      _isLoadingWidget = false;
      notifyListeners();
    }
  }

  /// Загрузить историю для выбранной валюты и периода
  Future<void> loadHistory({
    String? currency,
    int? days,
  }) async {
    _selectedCurrency = currency ?? _selectedCurrency;
    _selectedDays = days ?? _selectedDays;

    _isLoadingHistory = true;
    _historyError = null;
    notifyListeners();

    try {
      final result = await _apiService.getCurrencyRatesHistory(
        currency: _selectedCurrency,
        days: _selectedDays,
      );
      _history = result;
      _historyError = null;
    } catch (e) {
      _historyError = 'Не удалось загрузить историю курсов';
      _history = null;
    } finally {
      _isLoadingHistory = false;
      notifyListeners();
    }
  }

  /// Сменить валюту в истории
  Future<void> changeCurrency(String currency) {
    return loadHistory(currency: currency);
  }

  /// Сменить период в истории
  Future<void> changeDays(int days) {
    return loadHistory(days: days);
  }

  /// Запустить авто-обновление каждые 10 минут
  void _startAutoRefresh() {
    _refreshTimer = Timer.periodic(
      const Duration(minutes: 10),
      (_) => loadWidgetRates(),
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}
