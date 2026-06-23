import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'clock_interceptor.dart';
import 'jwt_interceptor.dart';

part 'api_client.g.dart';

/// Dio-based network client wrapper for API communications.
class ApiClient {
  /// Create an ApiClient with preconfigured Dio.
  ApiClient(this.dio);

  /// Underlying Dio client.
  final Dio dio;

  /// Perform a GET request.
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) {
    return dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// Perform a POST request.
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) {
    return dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
}

/// Provider for the secure storage instance.
@riverpod
FlutterSecureStorage secureStorage(SecureStorageRef ref) {
  return const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );
}

/// Provider for the central clock interceptor.
@riverpod
ClockInterceptor clockInterceptor(ClockInterceptorRef ref) {
  return ClockInterceptor();
}

/// Provider for the configured ApiClient.
@riverpod
ApiClient apiClient(ApiClientRef ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: 'http://localhost:8000',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: <String, dynamic>{
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    ),
  );

  final storage = ref.watch(secureStorageProvider);
  final clock = ref.watch(clockInterceptorProvider);

  dio.interceptors.addAll([
    clock,
    JwtInterceptor(storage),
    LogInterceptor(requestBody: true, responseBody: true),
  ]);

  return ApiClient(dio);
}
