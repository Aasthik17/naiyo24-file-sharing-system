import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

const minLinkExpiryMinutes = 10;
const maxLinkExpiryMinutes = 60;
const defaultLinkExpiryMinutes = 30;

final fileProvider = StateNotifierProvider<FileNotifier, FileState>((ref) {
  return FileNotifier();
});

class FileState {
  final String? filePath;
  final bool loading;
  final String? link;
  final int expiryMinutes;

  FileState({
    this.filePath,
    this.loading = false,
    this.link,
    this.expiryMinutes = defaultLinkExpiryMinutes,
  });

  FileState copyWith({
    String? filePath,
    bool? loading,
    String? link,
    int? expiryMinutes,
    bool clearLink = false,
  }) {
    return FileState(
      filePath: filePath ?? this.filePath,
      loading: loading ?? this.loading,
      link: clearLink ? null : (link ?? this.link),
      expiryMinutes: expiryMinutes ?? this.expiryMinutes,
    );
  }
}

class FileNotifier extends StateNotifier<FileState> {
  FileNotifier() : super(FileState());

  final api = ApiService();

  void setFile(String path) {
    state = state.copyWith(filePath: path, clearLink: true);
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
    if (state.filePath == null) return;

    state = state.copyWith(loading: true, clearLink: true);

    final link = await api.uploadFile(
      state.filePath!,
      expiryMinutes: state.expiryMinutes,
    );

    state = state.copyWith(loading: false, link: link);
  }
}
