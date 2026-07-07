import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../../core/network/api_client.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../domain/entities/vector.dart';
import '../../domain/repositories/i_vector_repository.dart';
import '../../data/datasources/vector_remote_data_source.dart';
import '../../data/repositories/vector_repository_impl.dart';

part 'vectors_provider.g.dart';

@riverpod
VectorRemoteDataSource vectorRemoteDataSource(VectorRemoteDataSourceRef ref) {
  return VectorRemoteDataSource(ref.watch(apiClientProvider));
}

@riverpod
IVectorRepository vectorRepository(VectorRepositoryRef ref) {
  return VectorRepositoryImpl(
    ref.watch(vectorRemoteDataSourceProvider),
    ref.watch(secureStorageProvider),
  );
}

@riverpod
class VectorsNotifier extends _$VectorsNotifier {
  @override
  FutureOr<List<Vector>> build() async {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.valueOrNull;
    if (user == null) return [];

    final repo = ref.watch(vectorRepositoryProvider);
    return repo.getVectors(user.id);
  }

  Future<void> emitVector({
    required String sourceNodeId,
    required String targetNodeId,
    required double amount,
    double exchangeRate = 1.0,
    String? lineageToken,
    String? transactionId,
    Map<String, String>? tags,
    DateTime? effectiveAt,
  }) async {
    final authState = ref.read(authNotifierProvider);
    final user = authState.valueOrNull;
    if (user == null) return;

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(vectorRepositoryProvider);
      await repo.emitVector(
        userId: user.id,
        sourceNodeId: sourceNodeId,
        targetNodeId: targetNodeId,
        amount: amount,
        exchangeRate: exchangeRate,
        lineageToken: lineageToken,
        transactionId: transactionId,
        tags: tags,
        effectiveAt: effectiveAt,
      );
      
      // Invalidar balances de nodos para que se recalculen
      ref.invalidate(nodesNotifierProvider);
      ref.invalidate(nodeBalanceProvider);
      
      return repo.getVectors(user.id);
    });
  }
}
