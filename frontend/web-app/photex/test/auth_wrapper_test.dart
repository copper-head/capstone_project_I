import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'mocks.dart';

import 'package:photex/state/auth_state.dart';
import 'package:photex/screens/auth_wrapper.dart';


void main() {
  testWidgets('shows LoginScreen when logged out', (tester) async {
    final auth = AuthState(
      api: MockApiClient(),
      storage: MockSecureStorage(),
    );

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: AuthWrapper()),
      ),
    );

    expect(find.text('Login'), findsOneWidget);
  });

  testWidgets('shows HomePage when logged in', (tester) async {
    final api = MockApiClient();
    final storage = MockSecureStorage();

    when(() => storage.read(key: any(named: 'key')))
        .thenAnswer((_) async => 'token');

    when(() => api.listUserImages(any()))
        .thenAnswer((_) async => []);

    final auth = AuthState(api: api, storage: storage);

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: AuthWrapper()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Photex'), findsOneWidget);
  });
}
