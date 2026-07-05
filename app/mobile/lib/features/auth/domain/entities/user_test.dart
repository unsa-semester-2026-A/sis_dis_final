import 'package:flutter_test/flutter_test.dart';
import 'package:spondylus/features/auth/domain/entities/user.dart';

void main() {
  group('User Entity', () {
    test('should instantiate correctly with given values', () {
      const user = User(
        id: 'u-123',
        phoneNumber: '+51999999999',
        name: 'Alvaro',
      );

      assert(user.id == 'u-123');
      assert(user.phoneNumber == '+51999999999');
      assert(user.name == 'Alvaro');
    });

    test('should support value equality', () {
      const user1 = User(
        id: 'u-123',
        phoneNumber: '+51999999999',
        name: 'Alvaro',
      );
      const user2 = User(
        id: 'u-123',
        phoneNumber: '+51999999999',
        name: 'Alvaro',
      );

      assert(user1 == user2);
      assert(user1.hashCode == user2.hashCode);
    });

    test('should differentiate between unequal instances', () {
      const user1 = User(
        id: 'u-123',
        phoneNumber: '+51999999999',
        name: 'Alvaro',
      );
      const user2 = User(
        id: 'u-456',
        phoneNumber: '+51999999999',
        name: 'Alvaro',
      );

      assert(user1 != user2);
    });
  });
}
