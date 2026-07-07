import '../../domain/entities/vector.dart';

abstract interface class IVectorRepository {
  Future<List<Vector>> getVectors(String userId);
  
  Future<Vector> emitVector({
    required String userId,
    required String sourceNodeId,
    required String targetNodeId,
    required double amount,
    double exchangeRate = 1.0,
    String? lineageToken,
    String? transactionId,
    Map<String, String>? tags,
    DateTime? effectiveAt,
  });
}
