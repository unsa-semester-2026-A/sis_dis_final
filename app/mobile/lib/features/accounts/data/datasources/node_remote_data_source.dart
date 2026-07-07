import '../../../../core/network/api_client.dart';
import '../models/node_models.dart';

class NodeRemoteDataSource {
  NodeRemoteDataSource(this._apiClient);

  final ApiClient _apiClient;

  Future<NodeModel> createNode(String userId, String name, String nodeType, String currency) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '/ledger/nodes',
      data: {
        'user_id': userId,
        'name': name,
        'node_type': nodeType.toUpperCase(),
        'currency': currency.toUpperCase(),
      },
    );

    if (response.data == null) {
      throw Exception('Error al crear el nodo en el servidor');
    }

    return NodeModel.fromJson(response.data!);
  }

  Future<BalanceModel> getBalance(String nodeId, {String? startDate, String? endDate}) async {
    final Map<String, dynamic> query = {};
    if (startDate != null) query['start'] = startDate;
    if (endDate != null) query['end'] = endDate;

    final response = await _apiClient.get<Map<String, dynamic>>(
      '/ledger/nodes/$nodeId/balance',
      queryParameters: query.isNotEmpty ? query : null,
    );

    if (response.data == null) {
      throw Exception('Error al obtener el balance del nodo');
    }

    return BalanceModel.fromJson(response.data!);
  }
}
