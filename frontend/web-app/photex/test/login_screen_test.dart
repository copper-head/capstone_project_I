import 'package:flutter_test/flutter_test.dart';
void main() {
  testWidgets('login button calls AuthState.login', (tester) async {
    final api = MockApiClient();
    final storage = MockSecureStorage();

    when(() => api.login(any(), any()))
        .thenAnswer((_) async => 'token');

    when(() => storage.write(key: any(named: 'key'), value: any(named: 'value')))
        .thenAnswer((_) async {});

    final auth = AuthState(api: api, storage: storage);

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.enterText(find.byType(TextField).at(0), 'user');
    await tester.enterText(find.byType(TextField).at(1), 'pass');

    await tester.tap(find.text('Login'));
    await tester.pump();

    verify(() => api.login('user', 'pass')).called(1);
  });
}