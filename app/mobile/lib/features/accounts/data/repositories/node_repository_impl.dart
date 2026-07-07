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

      // Inicializar de inmediato los vectores por defecto
      final vectorsKey = 'vectors_list_$userId';
      final vectorsData = await _secureStorage.read(key: vectorsKey);
      if (vectorsData == null) {
        final defaultVectors = [
          {
            'id': '550e8400-e29b-41d4-a716-446655441001',
            'lineage_token': 'lineage-sueldo-bcp',
            'source_node_id': '550e8400-e29b-41d4-a716-446655440003',
            'target_node_id': '550e8400-e29b-41d4-a716-446655440001',
            'amount': '3000.0',
            'exchange_rate': '1.0',
            'effective_at': DateTime.now().subtract(const Duration(days: 5)).toIso8601String(),
            'system_at': DateTime.now().subtract(const Duration(days: 5)).toIso8601String(),
            'transaction_id': null,
            'tags': {'category': 'sueldo', 'info': 'Pago Mensual'},
          },
          {
            'id': '550e8400-e29b-41d4-a716-446655441002',
            'lineage_token': 'lineage-compra-super',
            'source_node_id': '550e8400-e29b-41d4-a716-446655440001',
            'target_node_id': '550e8400-e29b-41d4-a716-446655440002',
            'amount': '250.0',
            'exchange_rate': '1.0',
            'effective_at': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
            'system_at': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
            'transaction_id': null,
            'tags': {'category': 'comida', 'supermarket': 'Metro'},
          }
        ];
        await _secureStorage.write(key: vectorsKey, value: jsonEncode(defaultVectors));
      }

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
    final activeUserId = await _secureStorage.read(key: 'user_id');
    
    double baseBalance = 0.0;
    bool isRemoteSuccess = false;

    try {
      final balance = await _remoteDataSource.getBalance(nodeId, startDate: startStr, endDate: endStr);
      baseBalance = double.tryParse(balance.amount) ?? 0.0;
      isRemoteSuccess = true;
    } catch (_) {
      isRemoteSuccess = false;
    }

    try {
      if (activeUserId == null) return '0.00';
      
      double localAdjustments = 0.0;
      final vectorsJson = await _secureStorage.read(key: 'vectors_list_$activeUserId');
      if (vectorsJson != null) {
        final List<dynamic> decoded = jsonDecode(vectorsJson) as List<dynamic>;
        for (var item in decoded) {
          final id = item['id'] as String? ?? '';
          final src = item['source_node_id'] as String;
          final tgt = item['target_node_id'] as String;
          final amt = double.tryParse(item['amount']?.toString() ?? '0.0') ?? 0.0;
          final rate = double.tryParse(item['exchange_rate']?.toString() ?? '1.0') ?? 1.0;
          
          // Filtrar por fecha si está definido
          if (start != null || end != null) {
            final effStr = item['effective_at'] as String?;
            if (effStr != null) {
              final eff = DateTime.tryParse(effStr);
              if (eff != null) {
                if (start != null && eff.isBefore(start)) continue;
                if (end != null && eff.isAfter(end)) continue;
              }
            }
          }

          // Un vector se considera "local-only" si tiene el prefijo de cliente
          final isLocalOnly = id.startsWith('550e8400-e29b-41d4-a716-');

          if (isRemoteSuccess) {
            // Si el servidor respondió, solo sumamos el impacto de vectores locales
            // que el servidor no conoce (para evitar doble contabilidad)
            if (isLocalOnly) {
              if (tgt == nodeId) {
                localAdjustments += amt * rate;
              }
              if (src == nodeId) {
                localAdjustments -= amt;
              }
            }
          } else {
            // Si el servidor falló, sumamos TODOS los vectores locales (tanto los de fallback como los sincronizados)
            if (tgt == nodeId) {
              localAdjustments += amt * rate;
            }
            if (src == nodeId) {
              localAdjustments -= amt;
            }
          }
        }
      }

      return (baseBalance + localAdjustments).toStringAsFixed(2);
    } catch (err) {
      return isRemoteSuccess ? baseBalance.toStringAsFixed(2) : '0.00';
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
