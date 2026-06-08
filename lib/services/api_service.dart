import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ApiService {
  static String get _defaultBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
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
      connectTimeout: const Duration(minutes: 60),
      receiveTimeout: const Duration(minutes: 60),
      sendTimeout: const Duration(minutes: 60),
    ));
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

    final response = await _dio.post(
      "/api/upload/simple",
      data: formData,
      options: Options(
        sendTimeout: const Duration(minutes: 60),
        receiveTimeout: const Duration(minutes: 60),
      ),
    );

    return response.data["link"];
  }
}
