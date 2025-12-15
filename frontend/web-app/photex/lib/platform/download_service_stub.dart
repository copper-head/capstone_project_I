import 'download_service.dart';

class StubDownloadService implements DownloadService {
  @override
  void downloadBytes(List<int> bytes, String filename, String mimeType) {
    // no-op
  }
}
