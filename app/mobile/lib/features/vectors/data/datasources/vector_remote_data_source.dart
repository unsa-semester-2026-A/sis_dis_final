import '../../../../core/network/api_client.dart';
import '../models/vector_models.dart';

class VectorRemoteDataSource {
  VectorRemoteDataSource(this._apiClient);

  final ApiClient _apiClient;

  Future<VectorModel> emitVector({
    required String sourceNodeId,
    required String targetNodeId,
    required double amount,
    double exchangeRate = 1.0,
    String? lineageToken,
    String? transactionId,
    Map<String, String>? tags,
    DateTime? effectiveAt,
  }) async {
    final Map<String, dynamic> body = {
      'source_node_id': sourceNodeId,
      'target_node_id': targetNodeId,
      'amount': amount.toStringAsFixed(2),
      'exchange_rate': exchangeRate.toStringAsFixed(6),
    };

    if (lineageToken != null) body['lineage_token'] = lineageToken;
    if (transactionId != null) body['transaction_id'] = transactionId;
    if (tags != null) body['tags'] = tags;
    if (effectiveAt != null) body['effective_at'] = effectiveAt.toUtc().toIso8601String();

    final response = await _apiClient.post<Map<String, dynamic>>(
      '/ledger/vectors',
      data: body,
    );

    if (response.data == null) {
      throw Exception('Error al emitir el vector en el servidor');
    }

    return VectorModel.fromJson(response.data!);
  }
}
