import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../domain/entities/node.dart';
import '../../domain/repositories/i_node_repository.dart';
import '../datasources/node_remote_data_source.dart';
import '../models/node_models.dart';

class NodeRepositoryImpl implements INodeRepository {
  NodeRepositoryImpl(this._remoteDataSource, this._secureStorage);

  final NodeRemoteDataSource _remoteDataSource;
  final FlutterSecureStorage _secureStorage;

  String _storageKey(String userId) => 'nodes_list_$userId';

  @override
  Future<List<Node>> getNodes(String userId) async {
    final key = _storageKey(userId);
    final data = await _secureStorage.read(key: key);
    
    if (data == null) {
      // Nodos iniciales de prueba para que la app no inicie vacía
      final defaultNodes = [
        Node(
          id: '550e8400-e29b-41d4-a716-446655440001',
          userId: userId,
          name: 'BCP Ahorros (Real)',
          nodeType: NodeType.asset,
          currency: 'PEN',
          isActive: true,
        ),
        Node(
          id: '550e8400-e29b-41d4-a716-446655440002',
          userId: userId,
          name: 'Comida (Categoría)',
          nodeType: NodeType.sink,
          currency: 'PEN',
          isActive: true,
        ),
        Node(
          id: '550e8400-e29b-41d4-a716-446655440003',
          userId: userId,
          name: 'Sueldo BCP (Ingreso)',
          nodeType: NodeType.source,
          currency: 'PEN',
          isActive: true,
        ),
      ];
      await _saveNodesToStorage(userId, defaultNodes);
      return defaultNodes;
    }

    final List<dynamic> decoded = jsonDecode(data) as List<dynamic>;
    return decoded
        .map((item) => NodeModel.fromJson(item as Map<String, dynamic>).toDomain())
        .toList();
  }

  @override
  Future<Node> createNode(String userId, String name, NodeType nodeType, String currency) async {
    Node domainNode;
    try {
      // 1. Crear el nodo de verdad en el wallet-service remoto
      final model = await _remoteDataSource.createNode(userId, name, nodeType.value, currency);
      domainNode = model.toDomain();
    } catch (_) {
      // Fallback local: Generar UUID local para persistencia offline / server desactualizado
      final uuid = '550e8400-e29b-41d4-a716-${DateTime.now().millisecondsSinceEpoch.toString().padRight(12, '0').substring(0, 12)}';
      domainNode = Node(
        id: uuid,
        userId: userId,
        name: name,
        nodeType: nodeType,
        currency: currency,
        isActive: true,
      );
    }

    // 2. Guardar localmente en secure storage
    final nodes = await getNodes(userId);
    nodes.add(domainNode);
    await _saveNodesToStorage(userId, nodes);

    return domainNode;
  }

  @override
  Future<String> getBalance(String nodeId, {DateTime? start, DateTime? end}) async {
    final startStr = start?.toUtc().toIso8601String();
    final endStr = end?.toUtc().toIso8601String();
    
    try {
      final balance = await _remoteDataSource.getBalance(nodeId, startDate: startStr, endDate: endStr);
      return balance.amount;
    } catch (_) {
      // Fallback local: Calcular balance localmente barriendo únicamente los vectores del usuario activo actual
      try {
        final activeUserId = await _secureStorage.read(key: 'user_id');
        if (activeUserId == null) return '0.00';
        
        double balance = 0.0;
        final vectorsJson = await _secureStorage.read(key: 'vectors_list_$activeUserId');
        if (vectorsJson != null) {
          final List<dynamic> decoded = jsonDecode(vectorsJson) as List<dynamic>;
          for (var item in decoded) {
            final src = item['source_node_id'] as String;
            final tgt = item['target_node_id'] as String;
            final amt = double.tryParse(item['amount']?.toString() ?? '0.0') ?? 0.0;
            final rate = double.tryParse(item['exchange_rate']?.toString() ?? '1.0') ?? 1.0;
            
            if (tgt == nodeId) {
              balance += amt * rate;
            }
            if (src == nodeId) {
              balance -= amt;
            }
          }
        }
        return balance.toStringAsFixed(2);
      } catch (err) {
        return '0.00';
      }
    }
  }

  @override
  Future<void> deactivateNode(String nodeId) async {
    // Buscar el userId del nodo (leemos del SecureStorage)
    // Deactivamos el nodo localmente marcándolo como isActive = false
    // Nota: El backend soporta node.deactivate() pero la llamada REST no expone un endpoint POST/PUT /nodes/{id}/deactivate.
    // Así que lo desactivamos localmente.
    final keys = await _secureStorage.readAll();
    for (var key in keys.keys) {
      if (key.startsWith('nodes_list_')) {
        final userId = key.replaceFirst('nodes_list_', '');
        final nodes = await getNodes(userId);
        final index = nodes.indexWhere((n) => n.id == nodeId);
        if (index != -1) {
          final oldNode = nodes[index];
          nodes[index] = Node(
            id: oldNode.id,
            userId: oldNode.userId,
            name: oldNode.name,
            nodeType: oldNode.nodeType,
            currency: oldNode.currency,
            isActive: false,
          );
          await _saveNodesToStorage(userId, nodes);
          break;
        }
      }
    }
  }

  Future<void> _saveNodesToStorage(String userId, List<Node> nodes) async {
    final listModels = nodes.map((n) => NodeModel(
      id: n.id,
      userId: n.userId,
      name: n.name,
      nodeType: n.nodeType.value,
      currency: n.currency,
      isActive: n.isActive,
    ).toJson()).toList();
    
    await _secureStorage.write(key: _storageKey(userId), value: jsonEncode(listModels));
  }
}
