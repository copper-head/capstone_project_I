import 'dart:typed_data';
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:file_selector/file_selector.dart';
import 'package:provider/provider.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'services/api_service.dart';
import 'models/user_image.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => AuthState(),
      child: MaterialApp(
        title: 'Photex',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        ),
        home: AuthWrapper(),
      ),
    );
  }
}

class AuthState extends ChangeNotifier {
  final _storage = const FlutterSecureStorage();

  bool _isLoggedIn = false;
  String? _token;

  bool get isLoggedIn => _isLoggedIn;
  String get token => _token!;

  AuthState() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    _token = await _storage.read(key: 'auth_token');
    _isLoggedIn = _token != null;
    notifyListeners();
  }

  Future<void> login(String username, String password) async {
    _token = await ApiService.login(username, password);
    await _storage.write(key: 'auth_token', value: _token);
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<void> register(
      String username, String email, String password) async {
    await ApiService.register(username, email, password);
    await login(username, password); // auto-login
  }

  Future<void> logout() async {
    _token = null;
    _isLoggedIn = false;
    await _storage.delete(key: 'auth_token');
    notifyListeners();
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authState = context.watch<AuthState>();
    return authState.isLoggedIn ? MyHomePage() : LoginScreen();
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  void _register() async{
    if (_usernameController.text.isEmpty ||
        _emailController.text.isEmpty ||
        _passwordController.text.isEmpty ||
        _confirmPasswordController.text.isEmpty) {
      _showError('All fields are required');
      return;
    }

    if (_passwordController.text != _confirmPasswordController.text) {
      _showError('Passwords do not match');
      return;
    }

    try {
      await context.read<AuthState>().register(
            _usernameController.text,
            _emailController.text,
            _passwordController.text,
          );
      Navigator.pop(context);
    } catch (e) {
      _showError(e.toString());
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green[900],
        title: const Text('Create Account', style: TextStyle(color: Colors.white)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width / 3,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextField(
                  controller: _usernameController,
                  decoration: const InputDecoration(
                    labelText: 'Username',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _emailController,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _confirmPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Confirm Password',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _register,
                  child: const Text('Create Account'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  void _login() async {
    try {
      await context.read<AuthState>().login(
            _usernameController.text,
            _passwordController.text,
          );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green[900],
        title: Text(
          'Photex',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width / 3),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Login',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 24),
                TextField(
                  controller: _usernameController,
                  decoration: InputDecoration(
                    labelText: 'Username',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _passwordController,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    border: OutlineInputBorder(),
                  ),
                  obscureText: true,
                ),
                SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _login,
                  child: Text('Login'),
                ),
                SizedBox(height: 12),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const RegisterScreen()),
                    );
                  },
                  child: const Text('Create an account'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String searchQuery = '';
  List<UserImage> images = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadImages();
  }

  Future<void> _loadImages() async {
    try {
      final token = context.read<AuthState>().token;
      final result = await ApiService.listUserImages(token);

      setState(() {
        images = result;
        loading = false;
      });
    } catch (e) {
      loading = false;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  List<UserImage> get filteredFiles {
    if (searchQuery.isEmpty) {
      return images;
    }
    return images.where((file) => file.name.toLowerCase().contains(searchQuery.toLowerCase())).toList();
  }

  bool _isImageFile(UserImage image) {
  final ext = image.type.toLowerCase();
  return ext == 'jpg' || ext == 'jpeg' || ext == 'png' || ext == 'pdf';
  }

  Future<void> _convertImageToLatex(UserImage image) async {
    try {
      final token = context.read<AuthState>().token;

      final texBytes = await ApiService.imagesToLatex(
        imageIds: [image.id],
        token: token,
      );

      _downloadTex(texBytes, 'image_${image.id}.tex');
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  
  void _downloadTex(Uint8List bytes, String filename) {
    final blob = html.Blob([bytes], 'application/x-tex');
    final url = html.Url.createObjectUrlFromBlob(blob);

    final anchor = html.AnchorElement(href: url)
      ..setAttribute("download", filename)
      ..click();

    html.Url.revokeObjectUrl(url);
  }

int? _hoveredIndex;


  Future<void> _uploadImage() async {
    const XTypeGroup typeGroup = XTypeGroup(
      label: 'images',
      extensions: <String>['jpg', 'jpeg', 'png'],
    );
    final XFile? file = await openFile(acceptedTypeGroups: <XTypeGroup>[typeGroup]);
    if (file != null) {
      // Show preview dialog
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Upload Preview'),
            content: FutureBuilder<Uint8List>(
              future: file.readAsBytes(),
              builder: (BuildContext context, AsyncSnapshot<Uint8List> snapshot) {
                if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
                  return Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        height: 200,
                        width: 200,
                        child: Image.memory(
                          snapshot.data!,
                          fit: BoxFit.cover,
                        ),
                      ),
                      SizedBox(height: 16),
                      Text(file.name),
                    ],
                  );
                } else if (snapshot.hasError) {
                  return Text('Error loading image');
                } else {
                  return CircularProgressIndicator();
                }
              },
            ),
            actions: [
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[900],
                  foregroundColor: Colors.white,
                ),
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Uploaded and converting ${file.name} to LaTeX')),
                  );
                },
                child: Text('Upload & Convert to LaTeX'),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[900],
                  foregroundColor: Colors.white,
                ),
                onPressed: () async {
                  Navigator.of(context).pop();

                  try {
                    final bytes = await file.readAsBytes();
                    final token = context.read<AuthState>().token;

                    await ApiService.uploadImage(
                      bytes: bytes,
                      filename: file.name,
                      token: token,
                    );

                    final newImages = await ApiService.listUserImages(token);

                    setState(() {
                      images = newImages;
                    });

                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Uploaded ${file.name}')),
                    );
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Upload failed')),
                    );
                  }
                },
                child: Text('Upload'),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  _uploadImage(); // Select different
                },
                child: Text('Select Different File'),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Cancel
                },
                child: Text('Cancel'),
              ),
            ],
          );
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green[900],
        title: Text(
          'Photex',
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.logout, color: Colors.white),
            onPressed: () {
              context.read<AuthState>().logout();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search files...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) {
                setState(() {
                  searchQuery = value;
                });
              },
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: filteredFiles.length,
              itemBuilder: (context, index) {
                final file = filteredFiles[index];
                return MouseRegion(
                  onEnter: (_) => setState(() => _hoveredIndex = index),
                  onExit: (_) => setState(() => _hoveredIndex = null),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    color: _hoveredIndex == index
                        ? Colors.green.withAlpha(30)
                        : Colors.transparent,
                    child: ListTile(
                      leading: Icon(_getFileIcon(file.type)),
                      title: Text(file.name),
                      subtitle: Text('${file.type} - ${file.timestamp}'),

                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => FileViewerPage(file: file),
                          ),
                        );
                      },

                      trailing: _isImageFile(file)
                          ? Tooltip(
                              message: 'Convert to LaTeX',
                              child: IconButton(
                                icon: const Icon(Icons.functions),
                                color: Colors.green[900],
                                onPressed: () => _convertImageToLatex(file),
                              ),
                            )
                          : null,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _uploadImage,
        child: Icon(Icons.add_circle_outline_rounded),
      ),
    );
  }

  IconData _getFileIcon(String type) {
    switch (type.toLowerCase()) {
      case 'jpeg':
      case 'jpg':
      case 'png':
        return Icons.image;
      case 'pdf':
        return Icons.picture_as_pdf;
      case '.txt':
        return Icons.description;
      default:
        return Icons.insert_drive_file;
    }
  }
}

class FileViewerPage extends StatelessWidget {
  final UserImage file;

  const FileViewerPage({super.key, required this.file});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green[900],
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          file.name,
          style: const TextStyle(color: Colors.white),
        ),
      ),
      body: _buildFileContent(),
    );
  }

  Widget _buildFileContent() {
    switch (file.type.toLowerCase()) {
      case 'jpg':
      case 'jpeg':
      case 'png':
        return _buildImageView();
      case 'pdf':
        return _buildPdfPlaceholder();
      case 'txt':
        return _buildTextPlaceholder();
      default:
        return const Center(child: Text('Unsupported file type'));
    }
  }

  Widget _buildImageView() {
    // Placeholder image viewer
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.image, size: 120),
          SizedBox(height: 16),
          Text('Image preview goes here'),
        ],
      ),
    );
  }

  Widget _buildPdfPlaceholder() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.picture_as_pdf, size: 120),
          SizedBox(height: 16),
          Text('PDF viewer coming soon'),
        ],
      ),
    );
  }

  Widget _buildTextPlaceholder() {
    return const Padding(
      padding: EdgeInsets.all(16.0),
      child: Text(
        'Text file preview goes here',
        style: TextStyle(fontSize: 16),
      ),
    );
  }
}