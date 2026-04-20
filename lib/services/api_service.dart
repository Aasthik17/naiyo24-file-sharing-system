import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    String baseUrl = "http://10.12.85.40:8000";
    _dio = Dio(BaseOptions(baseUrl: baseUrl));

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
    final response = await _dio.post(
      "/api/auth/login",
      data: {
        "username": email,
        "password": password,
      },
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );

    return response.data["access_token"];
  }

  Future<void> register(String email, String password) async {
    await _dio.post(
      "/api/auth/register",
      data: {
        "email": email,
        "password": password,
      },
    );
  }

  Future<String> uploadFile(String path) async {
    FormData formData = FormData.fromMap({
      "file": await MultipartFile.fromFile(path),
    });

    final response = await _dio.post("/api/upload/simple", data: formData);

    return response.data["link"];
  }
}
