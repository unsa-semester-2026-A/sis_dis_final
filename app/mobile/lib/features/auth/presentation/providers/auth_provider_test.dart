import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:spondylus/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:spondylus/features/auth/domain/entities/user.dart';
import 'package:spondylus/features/auth/domain/repositories/i_auth_repository.dart';
import 'package:spondylus/features/auth/presentation/providers/auth_provider.dart';

class _MockAuthRepository extends Mock implements IAuthRepository {}

void main() {
  late _MockAuthRepository mockRepository;
  const tUser = User(
    id: 'u-123',
    phoneNumber: '+51999999999',
    name: 'Alvaro',
  );

  setUp(() {
    mockRepository = _MockAuthRepository();
  });

  ProviderContainer makeContainer() {
    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(mockRepository),
      ],
    );
    addTearDown(container.dispose);
    return container;
  }

  group('AuthNotifier Provider State', () {
    test('initial state should resolve getCurrentUser from repository', () async {
      when(() => mockRepository.getCurrentUser()).thenAnswer((_) async => tUser);

      final container = makeContainer();

      // Initially loading while resolver runs
      expect(
        container.read(authNotifierProvider).isLoading,
        true,
      );

      // Await future resolution
      final result = await container.read(authNotifierProvider.future);
      expect(result, tUser);
      expect(
        container.read(authNotifierProvider),
        const AsyncValue<User?>.data(tUser),
      );
    });

    test('login success should update state to AsyncData with User', () async {
      when(() => mockRepository.getCurrentUser()).thenAnswer((_) async => null);
      when(() => mockRepository.login(any(), any())).thenAnswer((_) async => tUser);

      final container = makeContainer();
      await container.read(authNotifierProvider.future);

      // Perform login
      final future = container.read(authNotifierProvider.notifier).login('+51999999999', '1234');

      // Should show loading state during transition
      expect(
        container.read(authNotifierProvider).isLoading,
        true,
      );

      await future;

      expect(
        container.read(authNotifierProvider),
        const AsyncValue<User?>.data(tUser),
      );
    });

    test('login failure should update state to AsyncError', () async {
      when(() => mockRepository.getCurrentUser()).thenAnswer((_) async => null);
      final exception = Exception('Auth failed');
      when(() => mockRepository.login(any(), any())).thenThrow(exception);

      final container = makeContainer();
      await container.read(authNotifierProvider.future);

      // Perform login
      await container.read(authNotifierProvider.notifier).login('+51999999999', 'wrong-pin');

      expect(
        container.read(authNotifierProvider).hasError,
        true,
      );
    });
  });
}
