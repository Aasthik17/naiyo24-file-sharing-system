import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/auth_provider.dart';
import '../widgets/brand_kit.dart';
import 'login_screen.dart';
import 'upload_screen.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    final success = await ref.read(authProvider.notifier).register(
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
      badge: 'Create your space',
      title: 'Create account',
      heroTitle: 'Register and start sharing',
      highlights: const ['Quick setup', 'Secure'],
      form: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          BrandTextField(
            controller: _emailController,
            label: 'Email',
            icon: Icons.mail_outline_rounded,
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 14),
          BrandTextField(
            controller: _passwordController,
            label: 'Password',
            icon: Icons.shield_outlined,
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
            label: 'Register',
            icon: Icons.auto_awesome_rounded,
            onPressed: authState.isLoading
                ? null
                : () {
                    _register();
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
                          builder: (_) => const LoginScreen(),
                        ),
                      );
                    },
              child: const Text('Already have an account? Login'),
            ),
          ),
        ],
      ),
    );
  }
}
