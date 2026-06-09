import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

const minLinkExpiryMinutes = 10;
const maxLinkExpiryMinutes = 60;
const defaultLinkExpiryMinutes = 30;

final fileProvider = StateNotifierProvider<FileNotifier, FileState>((ref) {
  return FileNotifier();
});

class FileState {
  final PlatformFile? file;
  final bool loading;
  final String? link;
  final int expiryMinutes;
  final String? errorMessage;

  FileState({
    this.file,
    this.loading = false,
    this.link,
    this.expiryMinutes = defaultLinkExpiryMinutes,
    this.errorMessage,
  });

  FileState copyWith({
    PlatformFile? file,
    bool? loading,
    String? link,
    int? expiryMinutes,
    String? errorMessage,
    bool clearLink = false,
    bool clearError = false,
  }) {
    return FileState(
      file: file ?? this.file,
      loading: loading ?? this.loading,
      link: clearLink ? null : (link ?? this.link),
      expiryMinutes: expiryMinutes ?? this.expiryMinutes,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class FileNotifier extends StateNotifier<FileState> {
  FileNotifier() : super(FileState());

  final api = ApiService();

  void setFile(PlatformFile newFile) {
    state = state.copyWith(file: newFile, clearLink: true);
  }

  void setExpiryMinutes(int minutes) {
    final bounded = minutes.clamp(
      minLinkExpiryMinutes,
      maxLinkExpiryMinutes,
    );
    if (bounded == state.expiryMinutes) return;

    state = state.copyWith(expiryMinutes: bounded, clearLink: true);
  }

  Future<void> upload() async {
    if (state.file == null) return;

    state = state.copyWith(loading: true, clearLink: true, clearError: true);

    try {
      final link = await api.uploadFile(
        path: kIsWeb ? null : state.file!.path,
        bytes: state.file!.bytes,
        filename: state.file!.name,
        expiryMinutes: state.expiryMinutes,
      );

      state = state.copyWith(loading: false, link: link);
    } on Exception catch (e) {
      // Strip the "Exception: " prefix for a cleaner UI message
      final raw = e.toString();
      final msg = raw.startsWith('Exception: ') ? raw.substring(11) : raw;
      state = state.copyWith(loading: false, errorMessage: msg);
      debugPrint('Upload failed: $e');
    } catch (e) {
      state = state.copyWith(
        loading: false,
        errorMessage: 'Unexpected error: $e',
      );
      debugPrint('Upload failed (unknown): $e');
    }
  }
}
