import 'package:flutter/material.dart';

import '../models/user_image.dart';

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