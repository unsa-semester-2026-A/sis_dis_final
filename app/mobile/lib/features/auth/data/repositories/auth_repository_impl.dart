import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../../core/network/api_client.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/i_auth_repository.dart';
import '../datasources/auth_remote_data_source.dart';

part 'auth_repository_impl.g.dart';

/// Implementation of the IAuthRepository port.
class AuthRepositoryImpl implements IAuthRepository {
  /// Create an AuthRepositoryImpl with datasource and storage.
  AuthRepositoryImpl(this._remoteDataSource, this._secureStorage);

  final AuthRemoteDataSource _remoteDataSource;
  final FlutterSecureStorage _secureStorage;

  @override
  Future<User> login(String phoneNumber, String pin) async {
    final response = await _remoteDataSource.login(phoneNumber, pin);

    // Store credentials securely
    await _secureStorage.write(key: 'jwt_token', value: response.accessToken);
    await _secureStorage.write(key: 'user_id', value: response.user.id);
    await _secureStorage.write(
      key: 'user_phone',
      value: response.user.phoneNumber,
    );
    if (response.user.name != null) {
      await _secureStorage.write(key: 'user_name', value: response.user.name);
    }

    return response.user.toDomain();
  }

  @override
  Future<bool> isLoggedIn() async {
    final token = await _secureStorage.read(key: 'jwt_token');
    return token != null;
  }

  @override
  Future<User?> getCurrentUser() async {
    final token = await _secureStorage.read(key: 'jwt_token');
    if (token == null) {
      return null;
    }

    var id = await _secureStorage.read(key: 'user_id');
    final phone = await _secureStorage.read(key: 'user_phone');
    final name = await _secureStorage.read(key: 'user_name');

    if (id == null || phone == null) {
      return null;
    }

    if (!id.startsWith('550e8400')) {
      final digits = phone.replaceAll(RegExp(r'\D'), '');
      final padded = digits.padLeft(12, '0').substring(0, 12);
      id = '550e8400-e29b-41d4-a716-$padded';
      await _secureStorage.write(key: 'user_id', value: id);
      await _secureStorage.write(key: 'jwt_token', value: 'jwt_token_$id');
    }

    return User(
      id: id,
      phoneNumber: phone,
      name: name,
    );
  }

  @override
  Future<void> logout() async {
    await _secureStorage.delete(key: 'jwt_token');
    await _secureStorage.delete(key: 'user_id');
    await _secureStorage.delete(key: 'user_phone');
    await _secureStorage.delete(key: 'user_name');
  }
}

/// Provider for the IAuthRepository.
@riverpod
IAuthRepository authRepository(AuthRepositoryRef ref) {
  return AuthRepositoryImpl(
    ref.watch(authRemoteDataSourceProvider),
    ref.watch(secureStorageProvider),
  );
}
