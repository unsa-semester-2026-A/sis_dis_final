import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../../core/network/api_client.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../domain/entities/node.dart';
import '../../domain/repositories/i_node_repository.dart';
import '../../data/datasources/node_remote_data_source.dart';
import '../../data/repositories/node_repository_impl.dart';

part 'nodes_provider.g.dart';

@riverpod
NodeRemoteDataSource nodeRemoteDataSource(NodeRemoteDataSourceRef ref) {
  return NodeRemoteDataSource(ref.watch(apiClientProvider));
}

@riverpod
INodeRepository nodeRepository(NodeRepositoryRef ref) {
  return NodeRepositoryImpl(
    ref.watch(nodeRemoteDataSourceProvider),
    ref.watch(secureStorageProvider),
  );
}

@riverpod
class NodesNotifier extends _$NodesNotifier {
  @override
  FutureOr<List<Node>> build() async {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.valueOrNull;
    if (user == null) return [];
    
    final repo = ref.watch(nodeRepositoryProvider);
    return repo.getNodes(user.id);
  }

  Future<void> createNode(String name, NodeType nodeType, String currency) async {
    final authState = ref.read(authNotifierProvider);
    final user = authState.valueOrNull;
    if (user == null) return;

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(nodeRepositoryProvider);
      await repo.createNode(user.id, name, nodeType, currency);
      return repo.getNodes(user.id);
    });
  }

  Future<void> archiveNode(String nodeId) async {
    final authState = ref.read(authNotifierProvider);
    final user = authState.valueOrNull;
    if (user == null) return;

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(nodeRepositoryProvider);
      await repo.deactivateNode(nodeId);
      return repo.getNodes(user.id);
    });
  }
}

@riverpod
FutureOr<String> nodeBalance(NodeBalanceRef ref, String nodeId, {DateTime? start, DateTime? end}) async {
  final repo = ref.watch(nodeRepositoryProvider);
  return repo.getBalance(nodeId, start: start, end: end);
}
