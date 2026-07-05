import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:spondylus/features/auth/domain/entities/user.dart';
import 'package:spondylus/features/auth/domain/repositories/i_auth_repository.dart';

class _MockAuthRepository extends Mock implements IAuthRepository {}

void main() {
  late _MockAuthRepository mockRepository;
  const tUser = User(
    id: 'u-789',
    phoneNumber: '+51999999999',
    name: 'Alvaro Test',
  );

  setUp(() {
    mockRepository = _MockAuthRepository();
  });

  group('IAuthRepository Interface Specifications', () {
    test('login should return User when authentication is successful', () async {
      when(() => mockRepository.login(any(), any()))
          .thenAnswer((_) async => tUser);

      final result = await mockRepository.login('+51999999999', '1234');

      assert(result == tUser);
      verify(() => mockRepository.login('+51999999999', '1234')).called(1);
    });

    test('login should throw exception when authentication fails', () async {
      when(() => mockRepository.login(any(), any()))
          .thenThrow(Exception('Invalid PIN code'));

      expect(
        () => mockRepository.login('+51999999999', 'wrong-pin'),
        throwsA(isA<Exception>()),
      );
      verify(() => mockRepository.login('+51999999999', 'wrong-pin')).called(1);
    });

    test('isLoggedIn should return true if session is active', () async {
      when(() => mockRepository.isLoggedIn()).thenAnswer((_) async => true);

      final result = await mockRepository.isLoggedIn();

      assert(result == true);
      verify(() => mockRepository.isLoggedIn()).called(1);
    });

    test('getCurrentUser should return current active User', () async {
      when(() => mockRepository.getCurrentUser())
          .thenAnswer((_) async => tUser);

      final result = await mockRepository.getCurrentUser();

      assert(result == tUser);
      verify(() => mockRepository.getCurrentUser()).called(1);
    });

    test('logout should execute and complete successfully', () async {
      when(() => mockRepository.logout()).thenAnswer((_) async {});

      await mockRepository.logout();

      verify(() => mockRepository.logout()).called(1);
    });
  });
}
