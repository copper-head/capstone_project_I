import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';

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

    if (response.statusCode != 201) {
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

  /// CONVERT TO LATEX
  static Future<void> convertToLatex(String fileId, String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/convert/$fileId'),
      headers: authHeaders(token),
    );

    if (response.statusCode != 200) {
      throw Exception('Conversion failed');
    }
  }
}
