class Vector {
  const Vector({
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
  final double amount;
  final double exchangeRate;
  final DateTime effectiveAt;
  final DateTime systemAt;
  final String? transactionId;
  final Map<String, String> tags;

  double get targetAmount => amount * exchangeRate;
}
