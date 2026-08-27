import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/service.dart';
import '../models/estimate_result.dart';
import '../models/currency_rate.dart';
import '../models/order.dart';

class ApiService {
  final String baseUrl = 'http://localhost:8000/api';
  String? _token;
  
  Map<String, String> get headers {
    final h = {
      'Content-Type': 'application/json; charset=UTF-8',
    };
    if (_token != null) {
      h['Authorization'] = 'Bearer $_token';
    }
    return h;
  }
  
  void setToken(String? token) {
    _token = token;
  }
  
  String? get token => _token;
  
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

  // ========== Authentication ==========
  
  /// Регистрация нового пользователя
  Future<Map<String, dynamic>> register({
    required String phone,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: headers,
        body: json.encode({
          'phone': phone,
          'password': password,
          'full_name': fullName,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else if (response.statusCode == 400) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        throw Exception(data['detail'] ?? 'Ошибка регистрации');
      } else if (response.statusCode == 422) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final errors = data['detail'] as List;
        final errorMsg = errors.map((e) => e['msg']).join(', ');
        throw Exception(errorMsg);
      } else {
        throw Exception('Ошибка регистрации: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось зарегистрироваться: $e');
    }
  }

  /// Вход в систему
  Future<Map<String, dynamic>> login({
    required String phone,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: headers,
        body: json.encode({
          'phone': phone,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else if (response.statusCode == 401) {
        throw Exception('Неверный номер телефона или пароль');
      } else if (response.statusCode == 403) {
        throw Exception('Учётная запись деактивирована');
      } else {
        throw Exception('Ошибка входа: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось войти: $e');
    }
  }

  // ========== Orders ==========
  
  /// Создать заявку
  Future<Order> createOrder({
    required int serviceId,
    required Map<String, dynamic> params,
    required double estimateTotal,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/orders/create'),
        headers: headers,
        body: json.encode({
          'service_id': serviceId,
          'params': params,
          'estimate_total': estimateTotal,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Order.fromJson(data);
      } else if (response.statusCode == 401) {
        throw Exception('Требуется авторизация');
      } else if (response.statusCode == 400) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        throw Exception(data['detail'] ?? 'Ошибка создания заявки');
      } else {
        throw Exception('Ошибка создания заявки: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось создать заявку: $e');
    }
  }

  /// Получить список своих заявок
  Future<Map<String, dynamic>> getMyOrders({
    String? statusFilter,
    int offset = 0,
    int limit = 20,
  }) async {
    try {
      final queryParams = {
        'offset': offset.toString(),
        'limit': limit.toString(),
      };
      if (statusFilter != null) {
        queryParams['status_filter'] = statusFilter;
      }

      final uri = Uri.parse('$baseUrl/orders/my').replace(
        queryParameters: queryParams,
      );
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else if (response.statusCode == 401) {
        throw Exception('Требуется авторизация');
      } else {
        throw Exception('Ошибка загрузки заявок: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить заявки: $e');
    }
  }

  /// Получить детали заявки
  Future<Order> getOrderDetails(int orderId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/orders/$orderId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Order.fromJson(data);
      } else if (response.statusCode == 401) {
        throw Exception('Требуется авторизация');
      } else if (response.statusCode == 403) {
        throw Exception('Доступ запрещён');
      } else if (response.statusCode == 404) {
        throw Exception('Заявка не найдена');
      } else {
        throw Exception('Ошибка загрузки заявки: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Не удалось загрузить заявку: $e');
    }
  }
}
