import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/service.dart';

class ServicesProvider with ChangeNotifier {
  final ApiService _apiService;
  
  List<Service> _services = [];
  bool _isLoading = false;
  String? _error;
  
  ServicesProvider(this._apiService) {
    loadServices();
  }
  
  List<Service> get services => _services;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  Future<void> loadServices() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _services = await _apiService.getServices();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<Service?> getServiceBySlug(String slug) async {
    try {
      return await _apiService.getServiceBySlug(slug);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }
}
