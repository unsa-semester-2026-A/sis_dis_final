import '../../domain/entities/node.dart';

class NodeModel {
  const NodeModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.nodeType,
    required this.currency,
    required this.isActive,
  });

  final String id;
  final String userId;
  final String name;
  final String nodeType;
  final String currency;
  final bool isActive;

  factory NodeModel.fromJson(Map<String, dynamic> json) {
    return NodeModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      nodeType: json['node_type'] as String,
      currency: json['currency'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'node_type': nodeType,
      'currency': currency,
      'is_active': isActive,
    };
  }

  Node toDomain() {
    return Node(
      id: id,
      userId: userId,
      name: name,
      nodeType: NodeType.fromValue(nodeType),
      currency: currency,
      isActive: isActive,
    );
  }
}

class BalanceModel {
  const BalanceModel({
    required this.amount,
    required this.currency,
  });

  final String amount;
  final String currency;

  factory BalanceModel.fromJson(Map<String, dynamic> json) {
    return BalanceModel(
      amount: json['amount'] as String,
      currency: json['currency'] as String,
    );
  }
}
