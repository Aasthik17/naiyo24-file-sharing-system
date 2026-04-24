import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color ink = Color(0xFF07131F);
  static const Color surface = Color(0xFF102335);
  static const Color surfaceStrong = Color(0xFF16314A);
  static const Color line = Color(0x33FFFFFF);
  static const Color mist = Color(0xFFB6C7D8);
  static const Color coral = Color(0xFFFF8F70);
  static const Color gold = Color(0xFFF5C76B);
  static const Color aqua = Color(0xFF57E6CF);
  static const Color sky = Color(0xFF83D4FF);

  static ThemeData dark() {
    const colorScheme = ColorScheme.dark(
      primary: coral,
      secondary: aqua,
      surface: surface,
      onPrimary: Color(0xFF06131D),
      onSecondary: Color(0xFF06131D),
      onSurface: Colors.white,
      error: Color(0xFFFF7D7D),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: ink,
      textTheme: _textTheme(),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: const Color(0xFF11283D),
        behavior: SnackBarBehavior.floating,
        contentTextStyle: GoogleFonts.dmSans(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.08),
        labelStyle: GoogleFonts.dmSans(
          color: mist,
          fontWeight: FontWeight.w500,
        ),
        hintStyle: GoogleFonts.dmSans(
          color: Colors.white.withValues(alpha: 0.38),
        ),
        prefixIconColor: Colors.white.withValues(alpha: 0.75),
        suffixIconColor: Colors.white.withValues(alpha: 0.75),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 20,
          vertical: 18,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: const BorderSide(color: sky, width: 1.4),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: const BorderSide(color: Color(0xFFFF7D7D), width: 1.2),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: Colors.white,
          textStyle: GoogleFonts.dmSans(
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      dividerColor: line,
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: aqua,
      ),
    );
  }

  static TextTheme _textTheme() {
    final base = GoogleFonts.dmSansTextTheme(
      ThemeData(brightness: Brightness.dark).textTheme,
    ).apply(
      bodyColor: Colors.white,
      displayColor: Colors.white,
    );

    return base.copyWith(
      displaySmall: GoogleFonts.spaceGrotesk(
        fontSize: 38,
        fontWeight: FontWeight.w700,
        height: 1.02,
        color: Colors.white,
      ),
      headlineLarge: GoogleFonts.spaceGrotesk(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        height: 1.05,
        color: Colors.white,
      ),
      headlineMedium: GoogleFonts.spaceGrotesk(
        fontSize: 26,
        fontWeight: FontWeight.w700,
        height: 1.08,
        color: Colors.white,
      ),
      titleLarge: GoogleFonts.spaceGrotesk(
        fontSize: 21,
        fontWeight: FontWeight.w700,
        color: Colors.white,
      ),
      titleMedium: GoogleFonts.dmSans(
        fontSize: 16,
        fontWeight: FontWeight.w700,
        color: Colors.white,
      ),
      bodyLarge: GoogleFonts.dmSans(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 1.5,
        color: Colors.white,
      ),
      bodyMedium: GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        height: 1.45,
        color: mist,
      ),
      labelLarge: GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w700,
        color: Colors.white,
      ),
    );
  }
}
