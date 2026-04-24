import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class AuroraScaffold extends StatelessWidget {
  const AuroraScaffold({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const Positioned.fill(child: _AuroraBackdrop()),
          SafeArea(child: child),
        ],
      ),
    );
  }
}

class FrostPanel extends StatelessWidget {
  const FrostPanel({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(24),
    this.radius = 30,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.16),
                Colors.white.withValues(alpha: 0.06),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.22),
                blurRadius: 32,
                offset: const Offset(0, 20),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}

class AppPill extends StatelessWidget {
  const AppPill({
    super.key,
    required this.label,
    this.icon,
    this.tone = AppPillTone.coral,
  });

  final String label;
  final IconData? icon;
  final AppPillTone tone;

  @override
  Widget build(BuildContext context) {
    final colors = switch (tone) {
      AppPillTone.coral => [AppTheme.coral, AppTheme.gold],
      AppPillTone.aqua => [AppTheme.aqua, AppTheme.sky],
      AppPillTone.ink => [const Color(0xFF28425E), const Color(0xFF1B2F44)],
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        gradient: LinearGradient(colors: colors),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 15, color: AppTheme.ink),
            const SizedBox(width: 8),
          ],
          Text(
            label,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppTheme.ink,
                ),
          ),
        ],
      ),
    );
  }
}

enum AppPillTone { coral, aqua, ink }

class GradientButton extends StatelessWidget {
  const GradientButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.isLoading = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final disabled = onPressed == null || isLoading;

    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(22),
        gradient: LinearGradient(
          colors: disabled
              ? [
                  Colors.white.withValues(alpha: 0.16),
                  Colors.white.withValues(alpha: 0.08),
                ]
              : const [
                  AppTheme.coral,
                  AppTheme.gold,
                  AppTheme.aqua,
                ],
        ),
        boxShadow: disabled
            ? const []
            : [
                BoxShadow(
                  color: AppTheme.coral.withValues(alpha: 0.22),
                  blurRadius: 24,
                  offset: const Offset(0, 16),
                ),
              ],
      ),
      child: ElevatedButton(
        onPressed: disabled ? null : onPressed,
        style: ElevatedButton.styleFrom(
          elevation: 0,
          backgroundColor: Colors.transparent,
          foregroundColor: AppTheme.ink,
          disabledBackgroundColor: Colors.transparent,
          disabledForegroundColor: Colors.white.withValues(alpha: 0.5),
          shadowColor: Colors.transparent,
          minimumSize: const Size.fromHeight(60),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
          ),
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 220),
          child: isLoading
              ? const SizedBox(
                  key: ValueKey('loading'),
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(strokeWidth: 2.2),
                )
              : Row(
                  key: ValueKey(label),
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, size: 19),
                      const SizedBox(width: 10),
                    ],
                    Text(
                      label,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: AppTheme.ink,
                          ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class BrandWordmark extends StatelessWidget {
  const BrandWordmark({
    super.key,
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Container(
          width: 46,
          height: 46,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppTheme.coral, AppTheme.gold, AppTheme.aqua],
            ),
            boxShadow: [
              BoxShadow(
                color: AppTheme.coral.withValues(alpha: 0.24),
                blurRadius: 18,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: const Icon(Icons.cloud_upload_rounded, color: AppTheme.ink),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleLarge,
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class BrandTextField extends StatelessWidget {
  const BrandTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.icon,
    this.keyboardType,
    this.obscureText = false,
    this.suffixIcon,
  });

  final TextEditingController controller;
  final String label;
  final IconData icon;
  final TextInputType? keyboardType;
  final bool obscureText;
  final Widget? suffixIcon;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      style: Theme.of(context).textTheme.bodyLarge,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        suffixIcon: suffixIcon,
      ),
    );
  }
}

class InfoBanner extends StatelessWidget {
  const InfoBanner({
    super.key,
    required this.message,
    this.icon = Icons.info_outline_rounded,
    this.backgroundColor = const Color(0x33FF8080),
  });

  final String message;
  final IconData icon;
  final Color backgroundColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: backgroundColor,
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.white),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.white,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class TransferIllustration extends StatelessWidget {
  const TransferIllustration({
    super.key,
    this.height = 250,
  });

  final double height;

  @override
  Widget build(BuildContext context) {
    final primaryOrbSize = height * 0.78;
    final secondaryOrbSize = height * 0.64;
    final showcaseCardSize = height * 0.58;
    final showcaseCardRadius = showcaseCardSize * 0.24;
    final iconBoxSize = showcaseCardSize * 0.38;
    final lineHeight = showcaseCardSize * 0.07;
    final lineLongWidth = showcaseCardSize * 0.58;
    final lineShortWidth = showcaseCardSize * 0.42;
    final contentGap = showcaseCardSize * 0.08;

    return SizedBox(
      height: height,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: primaryOrbSize,
            height: primaryOrbSize,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppTheme.aqua.withValues(alpha: 0.42),
                  AppTheme.sky.withValues(alpha: 0.18),
                  Colors.transparent,
                ],
              ),
            ),
          ),
          Container(
            width: secondaryOrbSize,
            height: secondaryOrbSize,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
            ),
          ),
          const Positioned(
            left: 12,
            top: 28,
            child: _MiniOrbCard(
              icon: Icons.lock_rounded,
              label: 'Private',
              colors: [AppTheme.sky, AppTheme.aqua],
            ),
          ),
          const Positioned(
            right: 4,
            top: 72,
            child: _MiniOrbCard(
              icon: Icons.flash_on_rounded,
              label: 'Fast',
              colors: [AppTheme.coral, AppTheme.gold],
            ),
          ),
          const Positioned(
            right: 18,
            bottom: 18,
            child: _MiniOrbCard(
              icon: Icons.link_rounded,
              label: 'Short link',
              colors: [AppTheme.gold, AppTheme.aqua],
            ),
          ),
          Transform.rotate(
            angle: -0.16,
            child: Container(
              width: showcaseCardSize,
              height: showcaseCardSize,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(showcaseCardRadius),
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [AppTheme.coral, AppTheme.gold, AppTheme.aqua],
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.coral.withValues(alpha: 0.22),
                    blurRadius: 28,
                    offset: const Offset(0, 18),
                  ),
                ],
              ),
              child: Container(
                margin: const EdgeInsets.all(3),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(showcaseCardRadius - 3),
                  color: const Color(0xFF0E1B29),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: iconBoxSize,
                      height: iconBoxSize,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(iconBoxSize * 0.3),
                        gradient: const LinearGradient(
                          colors: [AppTheme.coral, AppTheme.gold],
                        ),
                      ),
                      child: Icon(
                        Icons.file_present_rounded,
                        size: showcaseCardSize * 0.19,
                        color: AppTheme.ink,
                      ),
                    ),
                    SizedBox(height: contentGap),
                    Container(
                      width: lineLongWidth,
                      height: lineHeight,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(999),
                        color: Colors.white.withValues(alpha: 0.1),
                      ),
                    ),
                    SizedBox(height: contentGap * 0.55),
                    Container(
                      width: lineShortWidth,
                      height: lineHeight,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(999),
                        color: Colors.white.withValues(alpha: 0.06),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class AuthScaffold extends StatelessWidget {
  const AuthScaffold({
    super.key,
    required this.title,
    required this.highlights,
    required this.form,
    this.badge = 'Secure access',
    this.heroTitle = '',
  });

  final String badge;
  final String title;
  final String heroTitle;
  final List<String> highlights;
  final Widget form;

  @override
  Widget build(BuildContext context) {
    final viewInsets = MediaQuery.viewInsetsOf(context);

    return AuroraScaffold(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 930;
          final keyboardVisible = viewInsets.bottom > 0;
          final fullHeight = constraints.maxHeight + viewInsets.bottom;
          final isShort = fullHeight < 700;
          final artHeight = isWide
              ? (constraints.maxHeight * 0.34).clamp(150.0, 220.0)
              : (constraints.maxHeight * 0.16).clamp(88.0, 112.0);

          final hero = Padding(
            padding: EdgeInsets.all(isWide ? 8 : 0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment:
                  isWide ? CrossAxisAlignment.start : CrossAxisAlignment.center,
              children: [
                const BrandWordmark(
                  title: 'Naiyo24 Transfer',
                  subtitle: 'Fast, visual, secure sharing',
                ),
                SizedBox(height: isWide ? 26 : 18),
                TransferIllustration(height: artHeight),
                if (heroTitle.isNotEmpty) ...[
                  SizedBox(height: isWide ? 20 : 12),
                  Text(
                    heroTitle,
                    maxLines: isWide ? 2 : 1,
                    overflow: TextOverflow.ellipsis,
                    textAlign: isWide ? TextAlign.start : TextAlign.center,
                    style: isWide
                        ? Theme.of(context).textTheme.headlineMedium
                        : Theme.of(context).textTheme.titleLarge,
                  ),
                ],
                if (highlights.isNotEmpty) ...[
                  SizedBox(height: isWide ? 18 : 12),
                  Wrap(
                    alignment:
                        isWide ? WrapAlignment.start : WrapAlignment.center,
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      for (final item in highlights.take(isWide ? 3 : 2))
                        AppPill(
                          label: item,
                          tone: item.contains('Fast')
                              ? AppPillTone.coral
                              : AppPillTone.aqua,
                        ),
                    ],
                  ),
                ],
              ],
            ),
          );

          final formPanel = FrostPanel(
            padding: EdgeInsets.fromLTRB(
              24,
              isWide ? 26 : 22,
              24,
              isWide ? 28 : 22,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (!isWide && isShort) ...[
                  const BrandWordmark(
                    title: 'Naiyo24 Transfer',
                    subtitle: 'Fast, visual, secure sharing',
                  ),
                  const SizedBox(height: 16),
                ],
                AppPill(
                  label: badge,
                  icon: Icons.auto_awesome_rounded,
                  tone: AppPillTone.ink,
                ),
                const SizedBox(height: 16),
                Text(title, style: Theme.of(context).textTheme.headlineLarge),
                const SizedBox(height: 22),
                form,
              ],
            ),
          );

          final horizontalPadding = isWide ? 36.0 : 18.0;
          final verticalPadding = isWide ? 24.0 : 16.0;
          final availableHeight =
              (constraints.maxHeight - (verticalPadding * 2)).clamp(
            0.0,
            double.infinity,
          );

          if (isWide) {
            return Padding(
              padding: EdgeInsets.symmetric(
                horizontal: horizontalPadding,
                vertical: verticalPadding,
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1120),
                  child: SizedBox(
                    width: double.infinity,
                    height: double.infinity,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(flex: 10, child: hero),
                        const SizedBox(width: 22),
                        Expanded(
                          flex: 9,
                          child: Center(child: formPanel),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }

          return Padding(
            padding: EdgeInsets.symmetric(
              horizontal: horizontalPadding,
              vertical: verticalPadding,
            ),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520),
                child: SingleChildScrollView(
                  keyboardDismissBehavior:
                      ScrollViewKeyboardDismissBehavior.onDrag,
                  child: ConstrainedBox(
                    constraints: BoxConstraints(minHeight: availableHeight),
                    child: SizedBox(
                      width: double.infinity,
                      child: Column(
                        mainAxisAlignment: keyboardVisible
                            ? MainAxisAlignment.start
                            : MainAxisAlignment.center,
                        children: [
                          if (!isShort) hero,
                          if (!isShort) const SizedBox(height: 16),
                          formPanel,
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return const AuroraScaffold(
      child: Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrandWordmark(
                title: 'Naiyo24 Transfer',
                subtitle: 'Preparing your workspace',
              ),
              SizedBox(height: 28),
              TransferIllustration(height: 210),
              SizedBox(height: 24),
              CircularProgressIndicator(),
            ],
          ),
        ),
      ),
    );
  }
}

class _MiniOrbCard extends StatelessWidget {
  const _MiniOrbCard({
    required this.icon,
    required this.label,
    required this.colors,
  });

  final IconData icon;
  final String label;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(colors: colors),
        boxShadow: [
          BoxShadow(
            color: colors.first.withValues(alpha: 0.18),
            blurRadius: 18,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: AppTheme.ink),
          const SizedBox(width: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppTheme.ink,
                ),
          ),
        ],
      ),
    );
  }
}

class _AuroraBackdrop extends StatelessWidget {
  const _AuroraBackdrop();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color(0xFF05111B),
                Color(0xFF0A1A2B),
                Color(0xFF102238),
              ],
            ),
          ),
          child: SizedBox.expand(),
        ),
        Positioned(
          top: -120,
          left: -90,
          child: _GlowOrb(
            size: 290,
            colors: [
              AppTheme.coral.withValues(alpha: 0.9),
              AppTheme.gold.withValues(alpha: 0.45),
            ],
          ),
        ),
        Positioned(
          top: 120,
          right: -90,
          child: _GlowOrb(
            size: 260,
            colors: [
              AppTheme.sky.withValues(alpha: 0.85),
              AppTheme.aqua.withValues(alpha: 0.42),
            ],
          ),
        ),
        Positioned(
          bottom: -160,
          left: 40,
          child: _GlowOrb(
            size: 320,
            colors: [
              AppTheme.aqua.withValues(alpha: 0.7),
              AppTheme.sky.withValues(alpha: 0.28),
            ],
          ),
        ),
        Positioned.fill(
          child: IgnorePointer(
            child: CustomPaint(
              painter: _MeshPainter(),
            ),
          ),
        ),
      ],
    );
  }
}

class _GlowOrb extends StatelessWidget {
  const _GlowOrb({
    required this.size,
    required this.colors,
  });

  final double size;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(colors: [
          colors.first,
          colors.last,
          Colors.transparent,
        ]),
      ),
    );
  }
}

class _MeshPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..color = Colors.white.withValues(alpha: 0.04);

    final width = size.width;
    final height = size.height;

    final arcOne = Path()
      ..moveTo(width * 0.05, height * 0.28)
      ..quadraticBezierTo(
          width * 0.28, height * 0.14, width * 0.56, height * 0.24)
      ..quadraticBezierTo(
          width * 0.82, height * 0.34, width * 0.96, height * 0.16);
    canvas.drawPath(arcOne, paint);

    final arcTwo = Path()
      ..moveTo(width * 0.02, height * 0.82)
      ..quadraticBezierTo(
          width * 0.28, height * 0.72, width * 0.44, height * 0.84)
      ..quadraticBezierTo(
          width * 0.74, height * 1.02, width * 0.98, height * 0.78);
    canvas.drawPath(arcTwo, paint);

    final dashPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = Colors.white.withValues(alpha: 0.06);

    for (final point in [
      Offset(width * 0.12, height * 0.18),
      Offset(width * 0.35, height * 0.22),
      Offset(width * 0.78, height * 0.32),
      Offset(width * 0.18, height * 0.78),
      Offset(width * 0.66, height * 0.86),
      Offset(width * 0.88, height * 0.7),
    ]) {
      canvas.drawCircle(point, 2.2, dashPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
