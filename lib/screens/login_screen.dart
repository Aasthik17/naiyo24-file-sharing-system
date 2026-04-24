import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/auth_provider.dart';
import '../widgets/brand_kit.dart';
import 'register_screen.dart';
import 'upload_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    final success = await ref.read(authProvider.notifier).login(
          _emailController.text.trim(),
          _passwordController.text,
        );

    if (!mounted || !success) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const UploadScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return AuthScaffold(
      badge: 'Secure access',
      title: 'Welcome back',
      heroTitle: 'Login and share instantly',
      highlights: const ['Short links', 'Private'],
      form: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          BrandTextField(
            controller: _emailController,
            label: 'Email',
            icon: Icons.alternate_email_rounded,
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 14),
          BrandTextField(
            controller: _passwordController,
            label: 'Password',
            icon: Icons.lock_outline_rounded,
            obscureText: _obscurePassword,
            suffixIcon: IconButton(
              onPressed: () {
                setState(() => _obscurePassword = !_obscurePassword);
              },
              icon: Icon(
                _obscurePassword
                    ? Icons.visibility_rounded
                    : Icons.visibility_off_rounded,
              ),
            ),
          ),
          const SizedBox(height: 14),
          if (authState.errorMessage != null) ...[
            InfoBanner(
              message: authState.errorMessage!,
              icon: Icons.error_outline_rounded,
            ),
            const SizedBox(height: 14),
          ],
          GradientButton(
            label: 'Login',
            icon: Icons.arrow_forward_rounded,
            onPressed: authState.isLoading
                ? null
                : () {
                    _login();
                  },
            isLoading: authState.isLoading,
          ),
          const SizedBox(height: 10),
          Center(
            child: TextButton(
              onPressed: authState.isLoading
                  ? null
                  : () {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const RegisterScreen(),
                        ),
                      );
                    },
              child: const Text("Don't have an account? Register"),
            ),
          ),
        ],
      ),
    );
  }
}
