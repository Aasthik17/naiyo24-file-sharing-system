import 'package:dio/dio.dart';

class ApiService {
  final Dio _dio = Dio(
    BaseOptions(baseUrl: "http://localhost:8000"),
  );

  Future<String> uploadFile(String path) async {
    FormData formData = FormData.fromMap({
      "file": await MultipartFile.fromFile(path),
    });

    final response = await _dio.post("/upload", data: formData);

    return response.data["link"];
  }
}