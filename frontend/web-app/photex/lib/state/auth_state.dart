import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../services/secure_storage.dart';

class AuthState extends ChangeNotifier {
  final ApiClient api;
  final SecureStorage storage;

  bool _isLoggedIn = false;
  String? _token;

  bool get isLoggedIn => _isLoggedIn;
  String get token => _token!;

  AuthState({
    required this.api,
    SecureStorage? storage,
  }) : storage = storage ?? FlutterSecureStorageImpl() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    _token = await storage.read(key: 'auth_token');
    _isLoggedIn = _token != null;
    notifyListeners();
  }

  Future<void> login(String username, String password) async {
    _token = await api.login(username, password);
    if (_token != null) {
      await storage.write(key: 'auth_token', value: _token!);
    }
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<void> register(
      String username, String email, String password) async {
    await api.register(username, email, password);
    await login(username, password); // auto-login
  }

  Future<void> logout() async {
    _token = null;
    _isLoggedIn = false;
    await storage.delete(key: 'auth_token');
    notifyListeners();
  }
}