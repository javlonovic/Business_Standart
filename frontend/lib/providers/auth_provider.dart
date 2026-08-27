import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  
  bool _isAuthenticated = false;
  String? _token;
  Map<String, dynamic>? _currentUser;
  
  AuthProvider(this._apiService) {
    _loadToken();
  }
  
  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;
  Map<String, dynamic>? get currentUser => _currentUser;
  
  Future<void> _loadToken() async {
    // TODO: Load from SharedPreferences
    notifyListeners();
  }
  
  Future<void> login(String phone, String password) async {
    // TODO: Implement login
    _isAuthenticated = true;
    notifyListeners();
  }
  
  Future<void> register(String phone, String password, String fullName) async {
    // TODO: Implement registration
    _isAuthenticated = true;
    notifyListeners();
  }
  
  Future<void> logout() async {
    _isAuthenticated = false;
    _token = null;
    _currentUser = null;
    notifyListeners();
  }
}
