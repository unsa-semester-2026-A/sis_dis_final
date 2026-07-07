enum NodeType {
  asset('ASSET'),
  liability('LIABILITY'),
  source('SOURCE'),
  sink('SINK');

  const NodeType(this.value);
  final String value;

  static NodeType fromValue(String value) {
    return NodeType.values.firstWhere(
      (e) => e.value.toUpperCase() == value.toUpperCase(),
      orElse: () => NodeType.asset,
    );
  }
}

class Node {
  const Node({
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
  final NodeType nodeType;
  final String currency;
  final bool isActive;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Node && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}
