import 'dart:typed_data';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:photex/services/api_service.dart';
import 'package:photex/models/user_image.dart';

class MockApiClient extends Mock implements ApiClient {}

class MockSecureStorage extends Mock implements FlutterSecureStorage {}

class FakeUserImage extends Fake implements UserImage {}
