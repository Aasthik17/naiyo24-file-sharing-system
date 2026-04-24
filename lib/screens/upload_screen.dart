import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/auth_provider.dart';
import '../providers/file_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/brand_kit.dart';

class UploadScreen extends ConsumerWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fileState = ref.watch(fileProvider);
    final notifier = ref.read(fileProvider.notifier);

    return AuroraScaffold(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 980;
          final compact = !isWide || constraints.maxHeight < 820;

          final overviewPanel = FrostPanel(
            padding: const EdgeInsets.fromLTRB(24, 24, 24, 24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const AppPill(
                  label: 'Transfer studio',
                  icon: Icons.waves_rounded,
                ),
                const SizedBox(height: 16),
                Text(
                  'Short links.\nFast uploads.',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 14),
                const Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    AppPill(
                      label: 'Short link output',
                      icon: Icons.link_rounded,
                      tone: AppPillTone.aqua,
                    ),
                    AppPill(
                      label: 'Private access',
                      icon: Icons.lock_rounded,
                    ),
                    AppPill(
                      label: 'Fast upload',
                      icon: Icons.bolt_rounded,
                      tone: AppPillTone.aqua,
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                TransferIllustration(height: compact ? 185 : 230),
              ],
            ),
          );

          final workspacePanel = FrostPanel(
            padding: EdgeInsets.fromLTRB(
              compact ? 20 : 24,
              compact ? 20 : 24,
              compact ? 20 : 24,
              compact ? 20 : 24,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Expanded(
                      child: BrandWordmark(
                        title: 'Naiyo24 Transfer',
                        subtitle: 'Private upload workspace',
                      ),
                    ),
                    const SizedBox(width: 16),
                    IconButton.filledTonal(
                      onPressed: () {
                        ref.read(authProvider.notifier).logout();
                      },
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.white.withValues(alpha: 0.08),
                        foregroundColor: Colors.white,
                      ),
                      icon: const Icon(Icons.logout_rounded),
                      tooltip: 'Logout',
                    ),
                  ],
                ),
                SizedBox(height: compact ? 14 : 18),
                const Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    AppPill(
                      label: 'Upload',
                      icon: Icons.arrow_upward_rounded,
                    ),
                    AppPill(
                      label: 'Share',
                      icon: Icons.link_rounded,
                      tone: AppPillTone.aqua,
                    ),
                  ],
                ),
                SizedBox(height: compact ? 16 : 18),
                _ChooseFileCard(
                  compact: compact,
                  onTap: () async {
                    final result = await FilePicker.platform.pickFiles();

                    if (result != null && result.files.single.path != null) {
                      notifier.setFile(result.files.single.path!);
                    }
                  },
                ),
                SizedBox(height: compact ? 12 : 16),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 260),
                  child: fileState.filePath == null
                      ? _HintPlaceholder(
                          key: const ValueKey('empty-file'),
                          icon: Icons.folder_open_rounded,
                          title: 'No file selected',
                          subtitle: 'Pick a file to begin.',
                          compact: compact,
                        )
                      : _SelectedFileCard(
                          key: const ValueKey('selected-file'),
                          filePath: fileState.filePath!,
                          compact: compact,
                        ),
                ),
                SizedBox(height: compact ? 12 : 16),
                GradientButton(
                  label: fileState.loading ? 'Uploading' : 'Upload now',
                  icon: Icons.arrow_upward_rounded,
                  onPressed: fileState.filePath == null || fileState.loading
                      ? null
                      : () {
                          notifier.upload();
                        },
                  isLoading: fileState.loading,
                ),
                SizedBox(height: compact ? 14 : 18),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 280),
                  switchInCurve: Curves.easeOutCubic,
                  switchOutCurve: Curves.easeInCubic,
                  child: fileState.link == null
                      ? _HintPlaceholder(
                          key: const ValueKey('empty-link'),
                          icon: Icons.link_off_rounded,
                          title: 'No link yet',
                          subtitle: 'Your short share link will appear here.',
                          compact: compact,
                        )
                      : _ShareLinkCard(
                          key: const ValueKey('share-link'),
                          link: fileState.link!,
                          compact: compact,
                        ),
                ),
              ],
            ),
          );

          return Padding(
            padding: EdgeInsets.symmetric(
              horizontal: isWide ? 32 : 18,
              vertical: isWide ? 24 : 16,
            ),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1180),
                child: SizedBox(
                  width: double.infinity,
                  height: double.infinity,
                  child: isWide
                      ? Row(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Expanded(flex: 9, child: overviewPanel),
                            const SizedBox(width: 22),
                            Expanded(
                              flex: 11,
                              child: Center(child: workspacePanel),
                            ),
                          ],
                        )
                      : Center(
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 620),
                            child: workspacePanel,
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

class _ChooseFileCard extends StatelessWidget {
  const _ChooseFileCard({
    required this.onTap,
    required this.compact,
  });

  final Future<void> Function() onTap;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(28),
        onTap: () {
          onTap();
        },
        child: Ink(
          padding: EdgeInsets.all(compact ? 18 : 24),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.12),
                Colors.white.withValues(alpha: 0.04),
              ],
            ),
          ),
          child: Row(
            children: [
              Container(
                width: compact ? 52 : 64,
                height: compact ? 52 : 64,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(22),
                  gradient: const LinearGradient(
                    colors: [AppTheme.coral, AppTheme.gold, AppTheme.aqua],
                  ),
                ),
                child: Icon(
                  Icons.add_photo_alternate_rounded,
                  color: AppTheme.ink,
                  size: compact ? 24 : 30,
                ),
              ),
              SizedBox(width: compact ? 14 : 18),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Choose a file',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    SizedBox(height: compact ? 4 : 6),
                    Text(
                      'Tap to browse from your device.',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Icon(
                Icons.arrow_forward_rounded,
                color: Colors.white.withValues(alpha: 0.8),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SelectedFileCard extends StatelessWidget {
  const _SelectedFileCard({
    super.key,
    required this.filePath,
    required this.compact,
  });

  final String filePath;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final fileName = _basename(filePath);

    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(compact ? 14 : 18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        color: Colors.white.withValues(alpha: 0.07),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: Row(
        children: [
          Container(
            width: compact ? 44 : 52,
            height: compact ? 44 : 52,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              color: AppTheme.sky.withValues(alpha: 0.15),
            ),
            child: const Icon(
              Icons.insert_drive_file_rounded,
              color: AppTheme.sky,
            ),
          ),
          SizedBox(width: compact ? 12 : 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  fileName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  filePath,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ShareLinkCard extends StatelessWidget {
  const _ShareLinkCard({
    super.key,
    required this.link,
    required this.compact,
  });

  final String link;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(compact ? 16 : 20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(26),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.aqua.withValues(alpha: 0.18),
            AppTheme.sky.withValues(alpha: 0.08),
            Colors.white.withValues(alpha: 0.06),
          ],
        ),
        border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  color: Colors.white.withValues(alpha: 0.12),
                ),
                child: const Icon(Icons.link_rounded, color: AppTheme.aqua),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Link ready',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    if (!compact) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Compact route generated successfully.',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 12),
              IconButton.filled(
                onPressed: () async {
                  await Clipboard.setData(ClipboardData(text: link));

                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Share link copied')),
                  );
                },
                style: IconButton.styleFrom(
                  backgroundColor: AppTheme.aqua,
                  foregroundColor: AppTheme.ink,
                ),
                icon: const Icon(Icons.copy_rounded),
                tooltip: 'Copy link',
              ),
            ],
          ),
          SizedBox(height: compact ? 12 : 16),
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(
              horizontal: 16,
              vertical: compact ? 12 : 14,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: Colors.black.withValues(alpha: 0.18),
              border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
            ),
            child: Text(
              _compactLink(link),
              maxLines: compact ? 1 : 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Colors.white,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _HintPlaceholder extends StatelessWidget {
  const _HintPlaceholder({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.compact,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(compact ? 14 : 18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Container(
            width: compact ? 44 : 52,
            height: compact ? 44 : 52,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              color: Colors.white.withValues(alpha: 0.08),
            ),
            child: Icon(icon, color: Colors.white.withValues(alpha: 0.82)),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: Theme.of(context).textTheme.titleMedium),
                SizedBox(height: compact ? 2 : 4),
                Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

String _basename(String path) {
  final normalized = path.replaceAll('\\', '/');
  return normalized.split('/').last;
}

String _compactLink(String link) {
  if (link.length <= 52) return link;
  return '${link.substring(0, 34)}...${link.substring(link.length - 12)}';
}
