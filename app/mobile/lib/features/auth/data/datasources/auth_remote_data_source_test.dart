import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:spondylus/core/network/api_client.dart';
import 'package:spondylus/features/auth/data/datasources/auth_remote_data_source.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient mockApiClient;
  late AuthRemoteDataSource dataSource;

  setUp(() {
    mockApiClient = _MockApiClient();
    dataSource = AuthRemoteDataSource(mockApiClient);
  });

  group('AuthRemoteDataSource', () {
    const tPhone = '+51999999999';
    const tPin = '1234';
    final tResponseMap = <String, dynamic>{
      'access_token': 'test-token-123',
      'user': <String, dynamic>{
        'id': 'u-123',
        'phone_number': tPhone,
        'name': 'Alvaro',
      }
    };

    test('should perform a POST request to /auth/login and return LoginResponse', () async {
      when(() => mockApiClient.post<Map<String, dynamic>>(
            any<String>(),
            data: any<dynamic>(named: 'data'),
          )).thenAnswer((_) async => Response<Map<String, dynamic>>(
            requestOptions: RequestOptions(path: '/auth/login'),
            data: tResponseMap,
            statusCode: 200,
          ));

      final result = await dataSource.login(tPhone, tPin);

      expect(result.accessToken, 'test-token-123');
      expect(result.user.id, 'u-123');
      expect(result.user.phoneNumber, tPhone);
      expect(result.user.name, 'Alvaro');

      verify(() => mockApiClient.post<Map<String, dynamic>>(
            '/auth/login',
            data: <String, dynamic>{
              'phone_number': tPhone,
              'pin': tPin,
            },
          )).called(1);
    });

    test('should throw an exception when the response data is null', () async {
      when(() => mockApiClient.post<Map<String, dynamic>>(
            any<String>(),
            data: any<dynamic>(named: 'data'),
          )).thenAnswer((_) async => Response<Map<String, dynamic>>(
            requestOptions: RequestOptions(path: '/auth/login'),
            data: null,
            statusCode: 200,
          ));

      expect(
        () => dataSource.login(tPhone, tPin),
        throwsA(isA<Exception>()),
      );
    });
  });
}
