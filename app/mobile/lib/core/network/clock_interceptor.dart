import 'dart:math';
import 'package:dio/dio.dart';

/// Interceptor to track and attach Lamport logical clocks on API transactions.
class ClockInterceptor extends Interceptor {
  int _clock = 0;

  /// Returns the current logical clock value.
  int get currentClock => _clock;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Increment local clock before request emission
    _clock++;
    options.headers['X-Lamport-Clock'] = _clock.toString();
    handler.next(options);
  }

  @override
  void onResponse(Response<dynamic> response, ResponseInterceptorHandler handler) {
    _updateClockFromHeaders(response.headers);
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response != null) {
      _updateClockFromHeaders(err.response!.headers);
    }
    handler.next(err);
  }

  void _updateClockFromHeaders(Headers headers) {
    final headerVal = headers.value('X-Lamport-Clock');
    if (headerVal != null) {
      final serverClock = int.tryParse(headerVal);
      if (serverClock != null) {
        // Sync: max(client, server) + 1
        _clock = max(_clock, serverClock) + 1;
      }
    }
  }
}
