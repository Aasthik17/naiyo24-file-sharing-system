import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

class AuthState {
  final bool isLoading;
  final bool isAuthenticated;
  final String? errorMessage;
  final bool isCheckingAuth;

  AuthState({
    this.isLoading = false,
    this.isAuthenticated = false,
    this.errorMessage,
    this.isCheckingAuth = true,
  });

  AuthState copyWith({
    bool? isLoading,
    bool? isAuthenticated,
    String? errorMessage,
    bool? isCheckingAuth,
    bool clearError = false,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      isCheckingAuth: isCheckingAuth ?? this.isCheckingAuth,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState()) {
    checkAuthStatus();
  }

  final _api = ApiService();

  Future<void> checkAuthStatus() async {
    state = state.copyWith(isCheckingAuth: true);
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');

    if (token != null) {
      state = state.copyWith(isAuthenticated: true, isCheckingAuth: false);
    } else {
      state = state.copyWith(isAuthenticated: false, isCheckingAuth: false);
    }
  }

  Future<bool> login(String email, String password) async {
    try {
      state = state.copyWith(isLoading: true, clearError: true);
      final token = await _api.login(email, password);

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', token);

      state = state.copyWith(isLoading: false, isAuthenticated: true);
      return true;
    } catch (e) {
      state = state.copyWith(
          isLoading: false, errorMessage: "Invalid email or password");
      return false;
    }
  }

  Future<bool> register(String email, String password) async {
    try {
      state = state.copyWith(isLoading: true, clearError: true);
      await _api.register(email, password);

      return await login(email, password);
    } catch (e) {
      state = state.copyWith(
          isLoading: false, errorMessage: "Registration failed. Error: $e");
      return false;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    state = state.copyWith(isAuthenticated: false);
  }
}
