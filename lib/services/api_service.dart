import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;

class ApiService {
  late final Dio _dio;

  ApiService() {
    String baseUrl = "http://192.168.1.133:8000";
    _dio = Dio(BaseOptions(baseUrl: baseUrl));
  }

  Future<String> uploadFile(String path) async {
    FormData formData = FormData.fromMap({
      "file": await MultipartFile.fromFile(path),
    });

    final response = await _dio.post("/api/upload/simple", data: formData);

    return response.data["link"];
  }
}