import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

final fileProvider =
StateNotifierProvider<FileNotifier, FileState>((ref) {
  return FileNotifier();
});

class FileState {
  final String? filePath;
  final bool loading;
  final String? link;

  FileState({this.filePath, this.loading = false, this.link});

  FileState copyWith({String? filePath, bool? loading, String? link}) {
    return FileState(
      filePath: filePath ?? this.filePath,
      loading: loading ?? this.loading,
      link: link ?? this.link,
    );
  }
}

class FileNotifier extends StateNotifier<FileState> {
  FileNotifier() : super(FileState());

  final api = ApiService();

  void setFile(String path) {
    state = state.copyWith(filePath: path);
  }

  Future<void> upload() async {
    if (state.filePath == null) return;

    state = state.copyWith(loading: true);

    final link = await api.uploadFile(state.filePath!);

    state = state.copyWith(loading: false, link: link);
  }
}