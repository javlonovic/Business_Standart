import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  
  bool _isAuthenticated = false;
  String? _token;
  Map<String, dynamic>? _currentUser;
  bool _isLoading = true;
  
  AuthProvider(this._apiService) {
    _loadToken();
  }
  
  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;
  Map<String, dynamic>? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  
  Future<void> _loadToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      final userJson = prefs.getString('current_user');
      
      if (token != null && userJson != null) {
        _token = token;
        _currentUser = Map<String, dynamic>.from(
          // Parse JSON string
          userJson.split(',').fold<Map<String, dynamic>>({}, (map, item) {
            final parts = item.split(':');
            if (parts.length == 2) {
              map[parts[0].trim()] = parts[1].trim();
            }
            return map;
          })
        );
        _apiService.setToken(token);
        _isAuthenticated = true;
      }
    } catch (e) {
      debugPrint('Error loading token: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> login(String phone, String password) async {
    try {
      final response = await _apiService.login(
        phone: phone,
        password: password,
      );
      
      _token = response['access_token'];
      _currentUser = {
        'user_id': response['user_id'],
        'full_name': response['full_name'],
        'phone': response['phone'],
        'role': response['role'],
      };
      
      _apiService.setToken(_token);
      _isAuthenticated = true;
      
      // Сохранить в SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);
      await prefs.setString('current_user', _currentUser.toString());
      
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> register(String phone, String password, String fullName) async {
    try {
      final response = await _apiService.register(
        phone: phone,
        password: password,
        fullName: fullName,
      );
      
      _token = response['access_token'];
      _currentUser = {
        'user_id': response['user_id'],
        'full_name': response['full_name'],
        'phone': response['phone'],
        'role': response['role'],
      };
      
      _apiService.setToken(_token);
      _isAuthenticated = true;
      
      // Сохранить в SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);
      await prefs.setString('current_user', _currentUser.toString());
      
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> logout() async {
    _isAuthenticated = false;
    _token = null;
    _currentUser = null;
    _apiService.setToken(null);
    
    // Удалить из SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('current_user');
    
    notifyListeners();
  }
}
