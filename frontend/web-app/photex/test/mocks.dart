import 'package:mocktail/mocktail.dart';
import 'package:photex/services/api_client.dart';
import 'package:photex/services/secure_storage.dart';

class MockApiClient extends Mock implements ApiClient {}

class MockSecureStorage implements SecureStorage {
  String? _value;

  @override
  Future<String?> read({required String key}) async {
    return _value;
  }

  @override
  Future<void> write({required String key, required String value}) async {
    _value = value;
  }

  @override
  Future<void> delete({required String key}) async {
    _value = null;
  }
}