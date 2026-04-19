import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../providers/file_provider.dart';
import '../providers/auth_provider.dart';

class UploadScreen extends ConsumerWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fileState = ref.watch(fileProvider);
    final notifier = ref.read(fileProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text("File Sharing"),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              ref.read(authProvider.notifier).logout();
            },
          )
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () async {
                final result = await FilePicker.platform.pickFiles();

                if (result != null) {
                  notifier.setFile(result.files.single.path!);
                }
              },
              child: const Text("Choose File"),
            ),
            if (fileState.filePath != null) Text(fileState.filePath!),
            const SizedBox(height: 20),
            fileState.loading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: notifier.upload,
                    child: const Text("Upload"),
                  ),
            const SizedBox(height: 20),
            if (fileState.link != null) ...[
              const Text("Share Link:"),
              SelectableText(fileState.link!),
            ]
          ],
        ),
      ),
    );
  }
}
