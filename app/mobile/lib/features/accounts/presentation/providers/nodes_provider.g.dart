// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'nodes_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$nodeRemoteDataSourceHash() =>
    r'9a73133fb0e9f6c40507e20d32b0c26ab57f9118';

/// See also [nodeRemoteDataSource].
@ProviderFor(nodeRemoteDataSource)
final nodeRemoteDataSourceProvider =
    AutoDisposeProvider<NodeRemoteDataSource>.internal(
  nodeRemoteDataSource,
  name: r'nodeRemoteDataSourceProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$nodeRemoteDataSourceHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef NodeRemoteDataSourceRef = AutoDisposeProviderRef<NodeRemoteDataSource>;
String _$nodeRepositoryHash() => r'14014c5b446974f29b9748859738c99e261368f9';

/// See also [nodeRepository].
@ProviderFor(nodeRepository)
final nodeRepositoryProvider = AutoDisposeProvider<INodeRepository>.internal(
  nodeRepository,
  name: r'nodeRepositoryProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$nodeRepositoryHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef NodeRepositoryRef = AutoDisposeProviderRef<INodeRepository>;
String _$nodeBalanceHash() => r'0b2365e2929aec90b7d92e8c99f7329be445143e';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// See also [nodeBalance].
@ProviderFor(nodeBalance)
const nodeBalanceProvider = NodeBalanceFamily();

/// See also [nodeBalance].
class NodeBalanceFamily extends Family<AsyncValue<String>> {
  /// See also [nodeBalance].
  const NodeBalanceFamily();

  /// See also [nodeBalance].
  NodeBalanceProvider call(
    String nodeId, {
    DateTime? start,
    DateTime? end,
  }) {
    return NodeBalanceProvider(
      nodeId,
      start: start,
      end: end,
    );
  }

  @override
  NodeBalanceProvider getProviderOverride(
    covariant NodeBalanceProvider provider,
  ) {
    return call(
      provider.nodeId,
      start: provider.start,
      end: provider.end,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'nodeBalanceProvider';
}

/// See also [nodeBalance].
class NodeBalanceProvider extends AutoDisposeFutureProvider<String> {
  /// See also [nodeBalance].
  NodeBalanceProvider(
    String nodeId, {
    DateTime? start,
    DateTime? end,
  }) : this._internal(
          (ref) => nodeBalance(
            ref as NodeBalanceRef,
            nodeId,
            start: start,
            end: end,
          ),
          from: nodeBalanceProvider,
          name: r'nodeBalanceProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$nodeBalanceHash,
          dependencies: NodeBalanceFamily._dependencies,
          allTransitiveDependencies:
              NodeBalanceFamily._allTransitiveDependencies,
          nodeId: nodeId,
          start: start,
          end: end,
        );

  NodeBalanceProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.nodeId,
    required this.start,
    required this.end,
  }) : super.internal();

  final String nodeId;
  final DateTime? start;
  final DateTime? end;

  @override
  Override overrideWith(
    FutureOr<String> Function(NodeBalanceRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: NodeBalanceProvider._internal(
        (ref) => create(ref as NodeBalanceRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        nodeId: nodeId,
        start: start,
        end: end,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<String> createElement() {
    return _NodeBalanceProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is NodeBalanceProvider &&
        other.nodeId == nodeId &&
        other.start == start &&
        other.end == end;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, nodeId.hashCode);
    hash = _SystemHash.combine(hash, start.hashCode);
    hash = _SystemHash.combine(hash, end.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin NodeBalanceRef on AutoDisposeFutureProviderRef<String> {
  /// The parameter `nodeId` of this provider.
  String get nodeId;

  /// The parameter `start` of this provider.
  DateTime? get start;

  /// The parameter `end` of this provider.
  DateTime? get end;
}

class _NodeBalanceProviderElement
    extends AutoDisposeFutureProviderElement<String> with NodeBalanceRef {
  _NodeBalanceProviderElement(super.provider);

  @override
  String get nodeId => (origin as NodeBalanceProvider).nodeId;
  @override
  DateTime? get start => (origin as NodeBalanceProvider).start;
  @override
  DateTime? get end => (origin as NodeBalanceProvider).end;
}

String _$nodesNotifierHash() => r'08043fdfebd15bd813909451141b93cbd12d1e1d';

/// See also [NodesNotifier].
@ProviderFor(NodesNotifier)
final nodesNotifierProvider =
    AutoDisposeAsyncNotifierProvider<NodesNotifier, List<Node>>.internal(
  NodesNotifier.new,
  name: r'nodesNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$nodesNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$NodesNotifier = AutoDisposeAsyncNotifier<List<Node>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
