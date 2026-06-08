import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

// ── Dev server host ───────────────────────────────────────────────────────────
// When running on a physical device (Android or iOS), the phone cannot reach
// 127.0.0.1 — that loopback address points to the phone itself.
// Set this to your laptop's LAN IP (run `ipconfig getifaddr en0` on macOS).
// This constant is only used when no API_BASE_URL env variable is set.
const String _kDevLanHost = '192.168.1.6';

class ApiMessageException implements Exception {
  const ApiMessageException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiService {
  static String get _defaultBaseUrl {
    if (kIsWeb) {
      // Web runs in the browser on the same machine as the server.
      return 'http://127.0.0.1:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      // 10.0.2.2 is the Android EMULATOR host alias.
      // For a real Android device on WiFi, use the laptop's LAN IP.
      return kDebugMode
          ? 'http://$_kDevLanHost:8000'
          : 'http://127.0.0.1:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      // iOS simulator can use 127.0.0.1, but a real device needs the LAN IP.
      return kDebugMode
          ? 'http://$_kDevLanHost:8000'
          : 'http://127.0.0.1:8000';
    }
    // macOS / Linux / Windows desktop — server is on the same machine.
    return 'http://127.0.0.1:8000';
  }

  late final Dio _dio;

  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_BASE_URL');
    return envUrl.isNotEmpty ? envUrl : _defaultBaseUrl;
  }

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(minutes: 2),
      receiveTimeout: const Duration(minutes: 2),
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('auth_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));
  }

  Future<String> login(String email, String password) async {
    try {
      final response = await _dio.post(
        "/api/auth/login",
        data: {
          "username": email,
          "password": password,
        },
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      return response.data["access_token"];
    } on DioException catch (e) {
      throw ApiMessageException(
        _authMessageFromDio(
          e,
          fallback: 'Unable to login right now. Please try again.',
          loginFallback: true,
        ),
      );
    }
  }

  Future<void> register(String email, String password) async {
    try {
      await _dio.post(
        "/api/auth/register",
        data: {
          "email": email,
          "password": password,
        },
      );
    } on DioException catch (e) {
      throw ApiMessageException(
        _authMessageFromDio(
          e,
          fallback: 'Unable to register right now. Please try again.',
        ),
      );
    }
  }

  Future<String> uploadFile({
    String? path,
    List<int>? bytes,
    String? filename,
    required int expiryMinutes,
  }) async {
    MultipartFile multipartFile;
    if (kIsWeb && bytes != null) {
      multipartFile = MultipartFile.fromBytes(bytes, filename: filename ?? 'upload.file');
    } else if (path != null) {
      multipartFile = await MultipartFile.fromFile(path, filename: filename);
    } else {
      throw Exception('No file data provided');
    }

    FormData formData = FormData.fromMap({
      "file": multipartFile,
      "expiry_minutes": expiryMinutes,
    });

    final response = await _dio.post("/api/upload/simple", data: formData);

    return response.data["link"];
  }

  String _authMessageFromDio(
    DioException exception, {
    required String fallback,
    bool loginFallback = false,
  }) {
    final statusCode = exception.response?.statusCode;
    final detail = _detailFromResponse(exception.response?.data);

    if (statusCode == 409) {
      return 'This email is already registered. Try logging in instead.';
    }

    if (statusCode == 401) {
      return 'Incorrect email or password.';
    }

    if (statusCode == 403) {
      return detail ?? 'This account cannot access the app right now.';
    }

    if (statusCode == 422) {
      return 'Please enter a valid email and a password with at least 6 characters.';
    }

    if (detail != null && detail.isNotEmpty) {
      return detail;
    }

    if (loginFallback) {
      return 'Invalid email or password.';
    }

    return fallback;
  }

  String? _detailFromResponse(dynamic data) {
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is String) return detail;
    }
    return null;
  }
}
