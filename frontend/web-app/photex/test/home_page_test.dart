import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'mocks.dart';

void main() {
  testWidgets('renders image list', (tester) async {
    final api = MockApiClient();
    final storage = MockSecureStorage();

    when(() => storage.read(key: any(named: 'key')))
        .thenAnswer((_) async => 'token');

    when(() => api.listUserImages(any())).thenAnswer(
      (_) async => [
        UserImage(
          id: 1,
          name: 'test.png',
          type: 'png',
          timestamp: 'now',
        ),
      ],
    );

    final auth = AuthState(api: api, storage: storage);

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: MyHomePage()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('test.png'), findsOneWidget);
  });
}