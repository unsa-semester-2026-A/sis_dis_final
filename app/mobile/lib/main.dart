import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'core/router/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Clean up legacy non-UUID user IDs to prevent 404/422 REST API validation errors
  const storage = FlutterSecureStorage();
  try {
    final currentId = await storage.read(key: 'user_id');
    if (currentId != null && !currentId.startsWith('550e8400')) {
      await storage.deleteAll();
    }
  } catch (_) {}

  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

/// Root widget of the Spondylus application.
class MyApp extends ConsumerWidget {
  /// Create the MyApp widget instance.
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'Spondylus',
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF00FFCC),
        scaffoldBackgroundColor: const Color(0xFF0F2027),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF00FFCC),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      routerConfig: router,
    );
  }
}
