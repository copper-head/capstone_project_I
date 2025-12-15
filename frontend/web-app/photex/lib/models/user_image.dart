class UserImage {
  final int id;
  final String filePath;
  final DateTime? uploadedAt;
  final int? batchId;

  UserImage({
    required this.id,
    required this.filePath,
    this.uploadedAt,
    this.batchId,
  });

  /// filename only (e.g. image.png)
  String get name => filePath.split('/').last;

  /// extension without dot (e.g. png)
  String get type {
    final parts = name.split('.');
    return parts.length > 1 ? parts.last.toLowerCase() : '';
  }

  /// safe timestamp for UI
  DateTime get timestamp => uploadedAt ?? DateTime.fromMillisecondsSinceEpoch(0);

  factory UserImage.fromJson(Map<String, dynamic> json) {
    return UserImage(
      id: json['id'],
      filePath: json['file_path'],
      uploadedAt: json['uploaded_at'] != null
          ? DateTime.parse(json['uploaded_at'])
          : null,
      batchId: json['batch_id'],
    );
  }
}
