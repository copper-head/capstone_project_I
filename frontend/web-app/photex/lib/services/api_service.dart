import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../models/user_image.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';

  static Map<String, String> authHeaders(String token) => {
        'Authorization': 'Bearer $token',
      };

  /// LOGIN
  static Future<String> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Invalid credentials');
    }

    final data = jsonDecode(response.body);
    return data['token']; // opaque token
  }

  /// REGISTER
  static Future<void> register(
      String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );

    print('STATUS: ${response.statusCode}');
    print('HEADERS: ${response.headers}');
    print('BODY: ${response.body}');

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Registration failed');
    }
  }

  /// UPLOAD IMAGE
  static Future<void> uploadImage({
    required Uint8List bytes,
    required String filename,
    required String token,
  }) async {
    final request =
        http.MultipartRequest('POST', Uri.parse('$baseUrl/upload/image'));

    request.headers.addAll(authHeaders(token));
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: filename,
      ),
    );

    final response = await request.send();

    if (response.statusCode != 200) {
      throw Exception('Upload failed');
    }
  }

  static Future<List<UserImage>> listUserImages(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/tex/images'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to fetch images');
    }

    final decoded = jsonDecode(response.body);
    final List images = decoded['images'];

    return images.map((e) => UserImage.fromJson(e)).toList();
  }

  static Future<Uint8List> imagesToLatex({
    required List<int> imageIds,
    required String token,}) async {
      final response = await http.post(
        Uri.parse('$baseUrl/tex/images-to-latex'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'image_ids': imageIds,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('LaTeX generation failed');
      }

      return response.bodyBytes; // IMPORTANT
    }

}
