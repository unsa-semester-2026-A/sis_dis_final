import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/user.dart';

part 'auth_models.freezed.dart';
part 'auth_models.g.dart';

/// Request DTO for authentication login.
@freezed
class LoginRequest with _$LoginRequest {
  /// Create a login request DTO.
  const factory LoginRequest({
    @JsonKey(name: 'phone_number') required String phoneNumber,
    required String pin,
  }) = _LoginRequest;

  /// Deserialize from JSON mapping.
  factory LoginRequest.fromJson(Map<String, dynamic> json) =>
      _$LoginRequestFromJson(json);
}

/// User details DTO nested inside authentication responses.
@freezed
class UserDto with _$UserDto {
  /// Create a user DTO.
  const factory UserDto({
    required String id,
    @JsonKey(name: 'phone_number') required String phoneNumber,
    String? name,
  }) = _UserDto;

  /// Deserialize from JSON mapping.
  factory UserDto.fromJson(Map<String, dynamic> json) =>
      _$UserDtoFromJson(json);

  /// Convert to pure Domain User entity.
  const UserDto._();
  
  /// Map to domain Entity.
  User toDomain() => User(
        id: id,
        phoneNumber: phoneNumber,
        name: name,
      );
}

/// Response DTO containing authentication results.
@freezed
class LoginResponse with _$LoginResponse {
  /// Create a login response DTO.
  const factory LoginResponse({
    @JsonKey(name: 'access_token') required String accessToken,
    required UserDto user,
  }) = _LoginResponse;

  /// Deserialize from JSON mapping.
  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);
}
