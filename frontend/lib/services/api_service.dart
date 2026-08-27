import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/service.dart';
import '../models/estimate_result.dart';
import '../models/currency_rate.dart';

class ApiService {
  final String baseUrl = 'http://localhost:8000/api';
  
  Map<String, String> get headers => {
    'Content-Type': 'application/json; charset=UTF-8',
  };
  
  /// Получить список услуг
  Future<List<Service>> getServices() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/services'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final items = data['items'] as List;
        return items.map((item) => Service.fromJson(item)).toList();
      } else {
        throw Exception('Ошибка загрузки услуг: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить услуги: $e');
    }
  }
  
  /// Получить услугу по slug
  Future<Service> getServiceBySlug(String slug) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/services/$slug'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Service.fromJson(data);
      } else if (response.statusCode == 404) {
        throw Exception('Услуга не найдена');
      } else {
        throw Exception('Ошибка загрузки услуги: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить услугу: $e');
    }
  }
  
  /// Получить статический контент
  Future<Map<String, dynamic>> getContent(String pageKey) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/content/$pageKey'),
        headers: headers,
      );
      
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Ошибка загрузки контента: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить контент: $e');
    }
  }

  /// Получить курсы валют для виджета (USD, EUR, RUB, GBP, CNY)
  Future<CurrencyRatesWidget> getCurrencyRatesWidget() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/currency-rates/widget'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return CurrencyRatesWidget.fromJson(data);
      } else {
        throw Exception('Ошибка загрузки курсов валют: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить курсы валют: $e');
    }
  }

  /// Получить историю курсов для выбранной валюты
  Future<CurrencyRatesHistory> getCurrencyRatesHistory({
    required String currency,
    int days = 30,
    int offset = 0,
    int limit = 100,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/currency-rates/history').replace(
        queryParameters: {
          'currency': currency,
          'days': days.toString(),
          'offset': offset.toString(),
          'limit': limit.toString(),
        },
      );
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return CurrencyRatesHistory.fromJson(data);
      } else {
        throw Exception('Ошибка загрузки истории курсов: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить историю курсов: $e');
    }
  }

  /// Получить параметры для калькулятора услуги
  Future<Map<String, dynamic>> getServiceParams(int serviceId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/calculator/params/$serviceId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else if (response.statusCode == 404) {
        throw Exception('Услуга не найдена');
      } else {
        throw Exception('Ошибка загрузки параметров: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить параметры: $e');
    }
  }

  /// Рассчитать стоимость услуги
  Future<EstimateResult> calculateEstimate({
    required int serviceId,
    required Map<String, dynamic> params,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/calculator/estimate'),
        headers: headers,
        body: json.encode({
          'service_id': serviceId,
          'params': params,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return EstimateResult.fromJson(data);
      } else if (response.statusCode == 422) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        throw Exception(data['detail'] ?? 'Ошибка валидации параметров');
      } else {
        throw Exception('Ошибка расчёта стоимости: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось рассчитать стоимость: $e');
    }
  }
}
