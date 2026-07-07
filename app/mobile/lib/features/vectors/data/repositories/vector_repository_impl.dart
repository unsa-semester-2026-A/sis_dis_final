import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../domain/entities/vector.dart';
import '../../domain/repositories/i_vector_repository.dart';
import '../datasources/vector_remote_data_source.dart';
import '../models/vector_models.dart';

class VectorRepositoryImpl implements IVectorRepository {
  VectorRepositoryImpl(this._remoteDataSource, this._secureStorage);

  final VectorRemoteDataSource _remoteDataSource;
  final FlutterSecureStorage _secureStorage;

  String _storageKey(String userId) => 'vectors_list_$userId';

  @override
  Future<List<Vector>> getVectors(String userId) async {
    final key = _storageKey(userId);
    final data = await _secureStorage.read(key: key);
    
    if (data == null) {
      // Vectores iniciales de prueba
      final defaultVectors = [
        Vector(
          id: '550e8400-e29b-41d4-a716-446655441001',
          lineageToken: 'lineage-sueldo-bcp',
          sourceNodeId: '550e8400-e29b-41d4-a716-446655440003', // Sueldo BCP
          targetNodeId: '550e8400-e29b-41d4-a716-446655440001', // BCP Ahorros
          amount: 3000.0,
          exchangeRate: 1.0,
          effectiveAt: DateTime.now().subtract(const Duration(days: 5)),
          systemAt: DateTime.now().subtract(const Duration(days: 5)),
          tags: {'category': 'sueldo', 'info': 'Pago Mensual'},
        ),
        Vector(
          id: '550e8400-e29b-41d4-a716-446655441002',
          lineageToken: 'lineage-compra-super',
          sourceNodeId: '550e8400-e29b-41d4-a716-446655440001', // BCP Ahorros
          targetNodeId: '550e8400-e29b-41d4-a716-446655440002', // Comida
          amount: 250.0,
          exchangeRate: 1.0,
          effectiveAt: DateTime.now().subtract(const Duration(days: 2)),
          systemAt: DateTime.now().subtract(const Duration(days: 2)),
          tags: {'category': 'comida', 'supermarket': 'Metro'},
        ),
      ];
      await _saveVectorsToStorage(userId, defaultVectors);
      return defaultVectors;
    }

    final List<dynamic> decoded = jsonDecode(data) as List<dynamic>;
    return decoded
        .map((item) => VectorModel.fromJson(item as Map<String, dynamic>).toDomain())
        .toList();
  }

  @override
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
  }) async {
    // 1. Emitir en el servidor real para impactar la contabilidad
    final model = await _remoteDataSource.emitVector(
      sourceNodeId: sourceNodeId,
      targetNodeId: targetNodeId,
      amount: amount,
      exchangeRate: exchangeRate,
      lineageToken: lineageToken,
      transactionId: transactionId,
      tags: tags,
      effectiveAt: effectiveAt,
    );

    final domainVector = model.toDomain();

    // 2. Guardar en local secure storage
    final vectors = await getVectors(userId);
    vectors.add(domainVector);
    await _saveVectorsToStorage(userId, vectors);

    return domainVector;
  }

  Future<void> _saveVectorsToStorage(String userId, List<Vector> vectors) async {
    final listModels = vectors.map((v) => VectorModel(
      id: v.id,
      lineageToken: v.lineageToken,
      sourceNodeId: v.sourceNodeId,
      targetNodeId: v.targetNodeId,
      amount: v.amount.toStringAsFixed(2),
      exchangeRate: v.exchangeRate.toStringAsFixed(6),
      effectiveAt: v.effectiveAt.toIso8601String(),
      systemAt: v.systemAt.toIso8601String(),
      transactionId: v.transactionId,
      tags: v.tags,
    ).toJson()).toList();
    
    await _secureStorage.write(key: _storageKey(userId), value: jsonEncode(listModels));
  }
}
