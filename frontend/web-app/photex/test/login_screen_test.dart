import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'mocks.dart';

import 'package:photex/state/auth_state.dart';
import 'package:photex/screens/login_screen.dart';

void main() {
  testWidgets('login button calls AuthState.login', (tester) async {
    final api = MockApiClient();
    final storage = MockSecureStorage();

    when(() => api.login(any(), any()))
        .thenAnswer((_) async => 'token');

    final auth = AuthState(api: api, storage: storage);

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.enterText(find.byType(TextField).at(0), 'user');
    await tester.enterText(find.byType(TextField).at(1), 'pass');

    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pump();

    verify(() => api.login('user', 'pass')).called(1);
  });
}