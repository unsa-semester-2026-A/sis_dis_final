/// Represents a user actor within the personal finance bounded context.
class User {
  /// Create a user entity.
  const User({
    required this.id,
    required this.phoneNumber,
    this.name,
  });

  /// The unique identifier of the user.
  final String id;

  /// The phone number associated with the user account.
  final String phoneNumber;

  /// The display name of the user.
  final String? name;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is User &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          phoneNumber == other.phoneNumber &&
          name == other.name;

  @override
  int get hashCode => id.hashCode ^ phoneNumber.hashCode ^ name.hashCode;
}
