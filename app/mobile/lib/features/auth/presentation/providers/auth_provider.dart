import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../domain/entities/user.dart';

part 'auth_provider.g.dart';

/// Notifier managing authentication state using AsyncValue.
@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  FutureOr<User?> build() async {
    final repo = ref.watch(authRepositoryProvider);
    return repo.getCurrentUser();
  }

  /// Perform user login.
  Future<void> login(String phoneNumber, String pin) async {
    state = const AsyncValue<User?>.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(authRepositoryProvider);
      return repo.login(phoneNumber, pin);
    });
  }

  /// Perform user logout.
  Future<void> logout() async {
    state = const AsyncValue<User?>.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(authRepositoryProvider);
      await repo.logout();
      return null;
    });
  }
}
