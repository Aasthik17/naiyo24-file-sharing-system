import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

// ── Layout ───────────────────────────────────────────────────────────────────

class AuroraScaffold extends StatelessWidget {
  const AuroraScaffold({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) => Scaffold(
        body: Stack(
          children: [
            const Positioned.fill(child: _AuroraBackdrop()),
            SafeArea(child: child),
          ],
        ),
      );
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
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: DecoratedBox(
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
            child: Padding(padding: padding, child: child),
          ),
        ),
      );
}

// ── Components ───────────────────────────────────────────────────────────────

enum AppPillTone { coral, aqua, ink, custom }

class AppPill extends StatelessWidget {
  const AppPill({
    super.key,
    required this.label,
    this.icon,
    this.tone = AppPillTone.coral,
    this.customColors,
    this.radius = 999,
    this.boxShadow,
  });

  final String label;
  final IconData? icon;
  final AppPillTone tone;
  final List<Color>? customColors;
  final double radius;
  final List<BoxShadow>? boxShadow;

  @override
  Widget build(BuildContext context) {
    final colors = customColors ?? switch (tone) {
      AppPillTone.coral  => [AppTheme.coral, AppTheme.gold],
      AppPillTone.aqua   => [AppTheme.aqua, AppTheme.sky],
      AppPillTone.ink    => [const Color(0xFF28425E), const Color(0xFF1B2F44)],
      AppPillTone.custom => [Colors.white, Colors.white],
    };
    final contentColor = tone == AppPillTone.ink ? Colors.white : AppTheme.ink;

    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(radius),
        gradient: LinearGradient(colors: colors),
        boxShadow: boxShadow,
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(icon, size: 15, color: contentColor),
              const SizedBox(width: 8),
            ],
            Text(
              label,
              style: Theme.of(context)
                  .textTheme
                  .labelLarge
                  ?.copyWith(color: contentColor),
            ),
          ],
        ),
      ),
    );
  }
}

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
              ? [Colors.white.withValues(alpha: 0.16), Colors.white.withValues(alpha: 0.08)]
              : const [AppTheme.coral, AppTheme.gold, AppTheme.aqua],
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
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 220),
          child: isLoading
              ? const SizedBox.square(
                  key: ValueKey('loading'),
                  dimension: 22,
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
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(color: AppTheme.ink),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class BrandWordmark extends StatelessWidget {
  const BrandWordmark({super.key, required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        SizedBox.square(
          dimension: 46,
          child: DecoratedBox(
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
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.titleLarge),
              const SizedBox(height: 2),
              Text(subtitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodyMedium),
            ],
          ),
        ),
      ],
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
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: backgroundColor,
          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Icon(icon, size: 18, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  message,
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      );
}

class TransferIllustration extends StatelessWidget {
  const TransferIllustration({super.key, this.height = 250});
  final double height;

  @override
  Widget build(BuildContext context) {
    final card   = height * 0.58;
    final r      = card * 0.24;
    final icon   = card * 0.38;
    final line   = card * 0.07;
    final gap    = card * 0.08;

    return SizedBox(
      height: height,
      child: Stack(
        alignment: Alignment.center,
        children: [
          _GlowOrb(
            size: height * 0.78,
            colors: [AppTheme.aqua.withValues(alpha: 0.42), AppTheme.sky.withValues(alpha: 0.18)],
          ),
          SizedBox.square(
            dimension: height * 0.64,
            child: DecoratedBox(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
              ),
            ),
          ),
          Positioned(
            left: 12, top: 28,
            child: AppPill(
              label: 'Private',
              icon: Icons.lock_rounded,
              customColors: const [AppTheme.sky, AppTheme.aqua],
              radius: 18,
              boxShadow: [BoxShadow(color: AppTheme.sky.withValues(alpha: 0.18), blurRadius: 18, offset: const Offset(0, 10))],
            ),
          ),
          Positioned(
            right: 4, top: 72,
            child: AppPill(
              label: 'Fast',
              icon: Icons.flash_on_rounded,
              customColors: const [AppTheme.coral, AppTheme.gold],
              radius: 18,
              boxShadow: [BoxShadow(color: AppTheme.coral.withValues(alpha: 0.18), blurRadius: 18, offset: const Offset(0, 10))],
            ),
          ),
          Positioned(
            right: 18, bottom: 18,
            child: AppPill(
              label: 'Short link',
              icon: Icons.link_rounded,
              customColors: const [AppTheme.gold, AppTheme.aqua],
              radius: 18,
              boxShadow: [BoxShadow(color: AppTheme.gold.withValues(alpha: 0.18), blurRadius: 18, offset: const Offset(0, 10))],
            ),
          ),
          Transform.rotate(
            angle: -0.16,
            child: SizedBox.square(
              dimension: card,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(r),
                  gradient: const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [AppTheme.coral, AppTheme.gold, AppTheme.aqua],
                  ),
                  boxShadow: [
                    BoxShadow(color: AppTheme.coral.withValues(alpha: 0.22), blurRadius: 28, offset: const Offset(0, 18)),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(3),
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(r - 3),
                      color: const Color(0xFF0E1B29),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox.square(
                          dimension: icon,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(icon * 0.3),
                              gradient: const LinearGradient(colors: [AppTheme.coral, AppTheme.gold]),
                            ),
                            child: Icon(Icons.file_present_rounded, size: card * 0.19, color: AppTheme.ink),
                          ),
                        ),
                        SizedBox(height: gap),
                        SizedBox(
                          width: card * 0.58, height: line,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(999),
                              color: Colors.white.withValues(alpha: 0.1),
                            ),
                          ),
                        ),
                        SizedBox(height: gap * 0.55),
                        SizedBox(
                          width: card * 0.42, height: line,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(999),
                              color: Colors.white.withValues(alpha: 0.06),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Background ────────────────────────────────────────────────────────────────

class _AuroraBackdrop extends StatelessWidget {
  const _AuroraBackdrop();

  @override
  Widget build(BuildContext context) => Stack(
        children: [
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF05111B), Color(0xFF0A1A2B), Color(0xFF102238)],
              ),
            ),
            child: SizedBox.expand(),
          ),
          Positioned(
            top: -120, left: -90,
            child: _GlowOrb(size: 290, colors: [AppTheme.coral.withValues(alpha: 0.9), AppTheme.gold.withValues(alpha: 0.45)]),
          ),
          Positioned(
            top: 120, right: -90,
            child: _GlowOrb(size: 260, colors: [AppTheme.sky.withValues(alpha: 0.85), AppTheme.aqua.withValues(alpha: 0.42)]),
          ),
          Positioned(
            bottom: -160, left: 40,
            child: _GlowOrb(size: 320, colors: [AppTheme.aqua.withValues(alpha: 0.7), AppTheme.sky.withValues(alpha: 0.28)]),
          ),
          Positioned.fill(
            child: IgnorePointer(child: CustomPaint(painter: _MeshPainter())),
          ),
        ],
      );
}

class _GlowOrb extends StatelessWidget {
  const _GlowOrb({required this.size, required this.colors});
  final double size;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) => SizedBox.square(
        dimension: size,
        child: DecoratedBox(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [colors.first, colors.last, Colors.transparent],
            ),
          ),
        ),
      );
}

class _MeshPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..color = Colors.white.withValues(alpha: 0.04);

    canvas.drawPath(
      Path()
        ..moveTo(w * 0.05, h * 0.28)
        ..quadraticBezierTo(w * 0.28, h * 0.14, w * 0.56, h * 0.24)
        ..quadraticBezierTo(w * 0.82, h * 0.34, w * 0.96, h * 0.16),
      stroke,
    );
    canvas.drawPath(
      Path()
        ..moveTo(w * 0.02, h * 0.82)
        ..quadraticBezierTo(w * 0.28, h * 0.72, w * 0.44, h * 0.84)
        ..quadraticBezierTo(w * 0.74, h * 1.02, w * 0.98, h * 0.78),
      stroke,
    );

    final dot = Paint()
      ..style = PaintingStyle.fill
      ..color = Colors.white.withValues(alpha: 0.06);

    for (final p in [
      Offset(w * 0.12, h * 0.18),
      Offset(w * 0.35, h * 0.22),
      Offset(w * 0.78, h * 0.32),
      Offset(w * 0.18, h * 0.78),
      Offset(w * 0.66, h * 0.86),
      Offset(w * 0.88, h * 0.70),
    ]) {
      canvas.drawCircle(p, 2.2, dot);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter _) => false;
}
