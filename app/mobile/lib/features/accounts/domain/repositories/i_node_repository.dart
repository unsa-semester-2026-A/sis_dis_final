import '../../domain/entities/node.dart';

abstract interface class INodeRepository {
  Future<List<Node>> getNodes(String userId);
  Future<Node> createNode(String userId, String name, NodeType nodeType, String currency);
  Future<String> getBalance(String nodeId, {DateTime? start, DateTime? end});
  Future<void> deactivateNode(String nodeId);
}
