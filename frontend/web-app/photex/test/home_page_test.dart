import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'mocks.dart';

import 'package:photex/state/auth_state.dart';
import 'package:photex/models/user_image.dart';
import 'package:photex/screens/home_page.dart';

void main() {
  testWidgets('renders image list', (tester) async {
    final api = MockApiClient();
    final storage = MockSecureStorage();

    when(() => api.listUserImages(any())).thenAnswer(
      (_) async => [
        UserImage(
          id: 1,
          filePath: 'test.png',
          uploadedAt: DateTime(2025, 1, 1),
          batchId: 1,
        ),
      ],
    );

    final auth = AuthState(api: api, storage: storage);

    // Allow _loadToken to complete
    await tester.pump();

    // Simulate logged in state
    when(() => api.login(any(), any()))
        .thenAnswer((_) async => 'token');

    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(
          home: Scaffold(
            body: MyHomePage()),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('test.png'), findsOneWidget);
  });
}