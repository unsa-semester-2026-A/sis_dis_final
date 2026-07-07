import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../config/environment_config.dart';

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

/// Connection status provider. True for online, false for local offline.
final connectivityProvider = StateProvider<bool>((ref) => true);

/// Provider for the configured ApiClient.
@riverpod
ApiClient apiClient(ApiClientRef ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: EnvironmentConfig.walletUrl,
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
    InterceptorsWrapper(
      onResponse: (response, handler) {
        ref.read(connectivityProvider.notifier).state = true;
        return handler.next(response);
      },
      onError: (error, handler) {
        if (error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.sendTimeout ||
            error.type == DioExceptionType.receiveTimeout ||
            error.type == DioExceptionType.connectionError) {
          ref.read(connectivityProvider.notifier).state = false;
        }
        return handler.next(error);
      },
    ),
    LogInterceptor(requestBody: true, responseBody: true),
  ]);

  return ApiClient(dio);
}

/// Helper function to format DioException errors into user-friendly messages in Spanish.
String formatNetworkError(dynamic error) {
  if (error is DioException) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'El servidor está tardando mucho en responder. Por favor, inténtalo de nuevo.';
      case DioExceptionType.connectionError:
        return 'No se pudo establecer conexión con el servidor. Verifica tu internet.';
      case DioExceptionType.badResponse:
        final status = error.response?.statusCode;
        final responseData = error.response?.data;
        String? detail;
        if (responseData is Map) {
          detail = responseData['detail']?.toString();
        }
        
        if (status == 404) {
          return detail ?? 'No se encontró el recurso solicitado en el servidor (404).';
        } else if (status == 400) {
          return detail ?? 'Solicitud inválida. Revisa los datos ingresados.';
        } else if (status == 401 || status == 403) {
          return 'Sesión expirada o no autorizada. Por favor, inicia sesión de nuevo.';
        } else if (status == 422) {
          return detail ?? 'Error de validación del servidor. Verifica los datos ingresados.';
        } else if (status != null && status >= 500) {
          return 'Error interno del servidor. Por favor, re-inténtalo más tarde.';
        }
        return detail ?? 'Error del servidor (${status ?? "desconocido"}).';
      case DioExceptionType.cancel:
        return 'La operación fue cancelada.';
      default:
        return 'Ocurrió un error inesperado al comunicarse con el servidor.';
    }
  }
  return error.toString().replaceAll('Exception: ', '');
}
