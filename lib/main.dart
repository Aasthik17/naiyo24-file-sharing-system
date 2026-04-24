import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/upload_screen.dart';
import 'theme/app_theme.dart';
import 'widgets/brand_kit.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    Widget homeWidget;
    if (authState.isCheckingAuth) {
      homeWidget = const LoadingView();
    } else if (authState.isAuthenticated) {
      homeWidget = const UploadScreen();
    } else {
      homeWidget = const LoginScreen();
    }

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark(),
      home: homeWidget,
    );
  }
}
