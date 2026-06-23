import '../entities/user.dart';

/// Secondary port / interface for authentication services.
abstract interface class IAuthRepository {
  /// Log in a user using their phone number and PIN code.
  ///
  /// Raises an exception on authentication failures or network disruptions.
  Future<User> login(String phoneNumber, String pin);

  /// Check if there is an active authenticated session.
  Future<bool> isLoggedIn();

  /// Retrieve the current logged-in user profile, if available.
  Future<User?> getCurrentUser();

  /// Clear the authentication session and log out the user.
  Future<void> logout();
}
