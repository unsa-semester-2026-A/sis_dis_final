import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../../core/network/api_client.dart';
import '../models/auth_models.dart';

part 'auth_remote_data_source.g.dart';

/// Remote data source interface for authentication calls.
class AuthRemoteDataSource {
  /// Create an AuthRemoteDataSource wrapping ApiClient.
  AuthRemoteDataSource(this._apiClient);

  final ApiClient _apiClient;

  /// Call login endpoint.
  Future<LoginResponse> login(String phoneNumber, String pin) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '/auth/login',
      data: <String, dynamic>{
        'phone_number': phoneNumber,
        'pin': pin,
      },
    );

    if (response.data == null) {
      throw Exception('Received empty payload from login server');
    }

    return LoginResponse.fromJson(response.data!);
  }
}

/// Provider for the AuthRemoteDataSource.
@riverpod
AuthRemoteDataSource authRemoteDataSource(AuthRemoteDataSourceRef ref) {
  return AuthRemoteDataSource(ref.watch(apiClientProvider));
}
