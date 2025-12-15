import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data';
import 'package:file_selector/file_selector.dart';

import '../state/auth_state.dart';
import '../models/user_image.dart';
import 'file_viewer_page.dart';

import '../platform/download_service.dart';
final _downloadService = DownloadService();

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_loaded) {
      _loadImages();
      _loaded = true;
    }
  }

  String searchQuery = '';
  List<UserImage> images = [];
  bool loading = true;

  Future<void> _loadImages() async {
    try {
      final auth = context.read<AuthState>();
      final result = await auth.api.listUserImages(auth.token);

      if (!mounted) return;

      setState(() {
        images = result;
        loading = false;
      });
    } catch (e) {
      setState(() {
        loading = false;
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.toString())),
        );
      });
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
      final auth = context.read<AuthState>();

      final texBytes = await auth.api.imagesToLatex(
        imageIds: [image.id],
        token: auth.token,
      );

      _downloadService.downloadBytes(texBytes, 'image_${image.id}.tex', 'application/x-tex');
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.toString())));
    }
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
                onPressed: () async {
                  Navigator.of(context).pop();

                  try {
                    final bytes = await file.readAsBytes();
                    final auth = context.read<AuthState>();

                    await auth.api.uploadImage(
                      bytes: bytes,
                      filename: file.name,
                      token: auth.token,
                    );

                    final newImages = await auth.api.listUserImages(auth.token);

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