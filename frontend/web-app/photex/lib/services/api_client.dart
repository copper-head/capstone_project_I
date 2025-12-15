import 'dart:typed_data';
import '../models/user_image.dart';

abstract class ApiClient {
  Future<String> login(String username, String password);

  Future<void> register(
    String username,
    String email,
    String password,
  );

  Future<void> uploadImage({
    required Uint8List bytes,
    required String filename,
    required String token,
  });

  Future<List<UserImage>> listUserImages(String token);

  Future<Uint8List> imagesToLatex({
    required List<int> imageIds,
    required String token,
  });
}
