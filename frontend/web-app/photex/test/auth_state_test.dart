import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'mocks.dart';

import 'package:photex/state/auth_state.dart';

void main() {
  late MockApiClient api;
  late MockSecureStorage storage;
  late AuthState auth;

  setUp(() {
    api = MockApiClient();
    storage = MockSecureStorage();

    auth = AuthState(api: api, storage: storage);
  });

  test('initially logged out when no token', () async {
    await Future.delayed(Duration.zero);
    expect(auth.isLoggedIn, false);
  });

  test('login stores token and updates state', () async {
    when(() => api.login('user', 'pass'))
        .thenAnswer((_) async => 'token123');

    await auth.login('user', 'pass');

    expect(auth.isLoggedIn, true);
    expect(auth.token, 'token123');
  });

  test('logout clears token and storage', () async {
    await auth.logout();
    expect(auth.isLoggedIn, false);
  });
}
