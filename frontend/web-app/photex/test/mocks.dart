import 'package:mocktail/mocktail.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:photex/services/api_client.dart';

class MockApiClient extends Mock implements ApiClient {}

class MockSecureStorage extends Mock implements FlutterSecureStorage {}

