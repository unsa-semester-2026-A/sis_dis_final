import '../../domain/entities/vector.dart';

class VectorModel {
  const VectorModel({
    required this.id,
    required this.lineageToken,
    required this.sourceNodeId,
    required this.targetNodeId,
    required this.amount,
    required this.exchangeRate,
    required this.effectiveAt,
    required this.systemAt,
    this.transactionId,
    required this.tags,
  });

  final String id;
  final String lineageToken;
  final String sourceNodeId;
  final String targetNodeId;
  final String amount;
  final String exchangeRate;
  final String effectiveAt;
  final String systemAt;
  final String? transactionId;
  final Map<String, dynamic> tags;

  factory VectorModel.fromJson(Map<String, dynamic> json) {
    return VectorModel(
      id: json['id'] as String,
      lineageToken: json['lineage_token'] as String,
      sourceNodeId: json['source_node_id'] as String,
      targetNodeId: json['target_node_id'] as String,
      amount: json['amount'] as String,
      exchangeRate: json['exchange_rate'] as String? ?? '1.0',
      effectiveAt: json['effective_at'] as String,
      systemAt: json['system_at'] as String,
      transactionId: json['transaction_id'] as String?,
      tags: (json['tags'] as Map<String, dynamic>?) ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'lineage_token': lineageToken,
      'source_node_id': sourceNodeId,
      'target_node_id': targetNodeId,
      'amount': amount,
      'exchange_rate': exchangeRate,
      'effective_at': effectiveAt,
      'system_at': systemAt,
      'transaction_id': transactionId,
      'tags': tags,
    };
  }

  Vector toDomain() {
    final parsedTags = tags.map((k, v) => MapEntry(k, v.toString()));
    return Vector(
      id: id,
      lineageToken: lineageToken,
      sourceNodeId: sourceNodeId,
      targetNodeId: targetNodeId,
      amount: double.tryParse(amount) ?? 0.0,
      exchangeRate: double.tryParse(exchangeRate) ?? 1.0,
      effectiveAt: DateTime.parse(effectiveAt),
      systemAt: DateTime.parse(systemAt),
      transactionId: transactionId,
      tags: parsedTags,
    );
  }
}
