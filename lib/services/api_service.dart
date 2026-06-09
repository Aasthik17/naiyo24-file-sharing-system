import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ApiService {
  // ── How to configure the server URL ────────────────────────────────────────
  //
  // Option A — dart-define (recommended, no code change needed):
  //   flutter run --dart-define=API_BASE_URL=http://192.168.1.5:8000
  //
  // Option B — edit LAN_IP below to match your Mac's local IP address.
  //   Run: ipconfig getifaddr en0   (on your Mac terminal)
  //
  // ── Why 10.0.2.2 does NOT work on real phones ──────────────────────────────
  // 10.0.2.2 is a special loopback alias that only Android *emulators* use
  // to reach the host machine's localhost. On a real physical device that
  // address is simply unreachable — the phone needs the Mac's actual LAN IP.
  // ───────────────────────────────────────────────────────────────────────────

  /// Your Mac's LAN IP address. Change this if your router assigns a different IP.
  /// Run `ipconfig getifaddr en0` in Terminal to find it.
  static const String _lanIp = '192.168.1.5';

  static String get _defaultBaseUrl {
    if (kIsWeb) {
      // Web app is served from the same machine — localhost works fine.
      return 'http://127.0.0.1:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      // Use the real LAN IP so both emulators AND real phones work.
      // (Emulators can resolve a LAN IP just as well as 10.0.2.2.)
      return 'http://$_lanIp:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      // iOS physical devices and simulators both work with the LAN IP.
      return 'http://$_lanIp:8000';
    }
    return 'http://127.0.0.1:8000';
  }

  static String get baseUrl {
    // API_BASE_URL dart-define overrides everything — use for CI/staging/prod.
    const envUrl = String.fromEnvironment('API_BASE_URL');
    return envUrl.isNotEmpty ? envUrl : _defaultBaseUrl;
  }

  late final Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      // Connect timeout: fail fast if server is unreachable
      connectTimeout: const Duration(seconds: 15),
      // Send timeout: allow up to 10 min for large file uploads
      sendTimeout: const Duration(minutes: 10),
      // Receive timeout: backend should respond within 60 s of receiving the file
      receiveTimeout: const Duration(seconds: 60),
    ));

    // Add logging interceptor in debug builds
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: false, // avoid logging binary file data
        responseBody: true,
        error: true,
        logPrint: (o) => debugPrint('[API] $o'),
      ));
    }
  }

  Future<String> uploadFile({
    String? path,
    List<int>? bytes,
    String? filename,
    required int expiryMinutes,
  }) async {
    MultipartFile multipartFile;

    if (kIsWeb) {
      // On web, file.bytes must be loaded via withData: true in FilePicker
      if (bytes == null || bytes.isEmpty) {
        throw Exception(
          'No file bytes available. Make sure FilePicker is called with withData: true on web.',
        );
      }
      multipartFile = MultipartFile.fromBytes(
        bytes,
        filename: filename ?? 'upload.file',
      );
    } else if (path != null) {
      multipartFile = await MultipartFile.fromFile(path, filename: filename);
    } else {
      throw Exception('No file data provided (path is null on non-web platform)');
    }

    final formData = FormData.fromMap({
      'file': multipartFile,
      'expiry_minutes': expiryMinutes,
    });

    try {
      final response = await _dio.post(
        '/api/upload/simple',
        data: formData,
        options: Options(
          // Per-request overrides — keep send generous, receive short
          sendTimeout: const Duration(minutes: 10),
          receiveTimeout: const Duration(seconds: 60),
        ),
      );

      final link = response.data['link'] as String?;
      if (link == null || link.isEmpty) {
        throw Exception('Server returned an empty link. Response: ${response.data}');
      }
      return link;
    } on DioException catch (e) {
      // Re-throw with a more user-friendly message
      final msg = switch (e.type) {
        DioExceptionType.connectionTimeout ||
        DioExceptionType.connectionError =>
          'Cannot reach the server. Make sure the backend is running at $baseUrl.',
        DioExceptionType.sendTimeout =>
          'Upload timed out while sending the file. Try a smaller file or check your connection.',
        DioExceptionType.receiveTimeout =>
          'Server took too long to respond after upload. Please try again.',
        DioExceptionType.badResponse =>
          'Server error ${e.response?.statusCode}: ${e.response?.data}',
        _ => 'Upload failed: ${e.message}',
      };
      throw Exception(msg);
    }
  }
}
