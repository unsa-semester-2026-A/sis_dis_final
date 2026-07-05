import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:spondylus/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:spondylus/features/auth/data/models/auth_models.dart';
import 'package:spondylus/features/auth/data/repositories/auth_repository_impl.dart';

class _MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}
class _MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  late _MockAuthRemoteDataSource mockRemoteDataSource;
  late _MockFlutterSecureStorage mockSecureStorage;
  late AuthRepositoryImpl repository;

  setUp(() {
    mockRemoteDataSource = _MockAuthRemoteDataSource();
    mockSecureStorage = _MockFlutterSecureStorage();
    repository = AuthRepositoryImpl(mockRemoteDataSource, mockSecureStorage);
  });

  group('AuthRepositoryImpl', () {
    const tPhone = '+51999999999';
    const tPin = '1234';
    const tUserDto = UserDto(id: 'u-123', phoneNumber: tPhone, name: 'Alvaro');
    const tLoginResponse = LoginResponse(accessToken: 'test-token', user: tUserDto);
    final tUser = tUserDto.toDomain();

    test('login should save token and details, and return domain User', () async {
      when(() => mockRemoteDataSource.login(any(), any()))
          .thenAnswer((_) async => tLoginResponse);
      when(() => mockSecureStorage.write(
            key: any(named: 'key'),
            value: any(named: 'value'),
          )).thenAnswer((_) async {});

      final result = await repository.login(tPhone, tPin);

      expect(result, tUser);
      verify(() => mockRemoteDataSource.login(tPhone, tPin)).called(1);
      verify(() => mockSecureStorage.write(key: 'jwt_token', value: 'test-token')).called(1);
      verify(() => mockSecureStorage.write(key: 'user_id', value: 'u-123')).called(1);
    });

    test('isLoggedIn should return true when token is present', () async {
      when(() => mockSecureStorage.read(key: 'jwt_token'))
          .thenAnswer((_) async => 'token-exists');

      final result = await repository.isLoggedIn();

      expect(result, true);
      verify(() => mockSecureStorage.read(key: 'jwt_token')).called(1);
    });

    test('getCurrentUser should return User when stored fields are present', () async {
      when(() => mockSecureStorage.read(key: 'jwt_token'))
          .thenAnswer((_) async => 'token-exists');
      when(() => mockSecureStorage.read(key: 'user_id'))
          .thenAnswer((_) async => 'u-123');
      when(() => mockSecureStorage.read(key: 'user_phone'))
          .thenAnswer((_) async => tPhone);
      when(() => mockSecureStorage.read(key: 'user_name'))
          .thenAnswer((_) async => 'Alvaro');

      final result = await repository.getCurrentUser();

      expect(result, tUser);
    });

    test('logout should clear storage fields', () async {
      when(() => mockSecureStorage.delete(key: any(named: 'key')))
          .thenAnswer((_) async {});

      await repository.logout();

      verify(() => mockSecureStorage.delete(key: 'jwt_token')).called(1);
      verify(() => mockSecureStorage.delete(key: 'user_id')).called(1);
    });
  });
}
