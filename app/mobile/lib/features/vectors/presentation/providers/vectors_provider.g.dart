// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'vectors_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$vectorRemoteDataSourceHash() =>
    r'0231e96206b2a0e13573704b41a2a9a1d664c878';

/// See also [vectorRemoteDataSource].
@ProviderFor(vectorRemoteDataSource)
final vectorRemoteDataSourceProvider =
    AutoDisposeProvider<VectorRemoteDataSource>.internal(
  vectorRemoteDataSource,
  name: r'vectorRemoteDataSourceProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$vectorRemoteDataSourceHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef VectorRemoteDataSourceRef
    = AutoDisposeProviderRef<VectorRemoteDataSource>;
String _$vectorRepositoryHash() => r'e7ede862231bc4bdc60038b184bc694afd84adb8';

/// See also [vectorRepository].
@ProviderFor(vectorRepository)
final vectorRepositoryProvider =
    AutoDisposeProvider<IVectorRepository>.internal(
  vectorRepository,
  name: r'vectorRepositoryProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$vectorRepositoryHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef VectorRepositoryRef = AutoDisposeProviderRef<IVectorRepository>;
String _$vectorsNotifierHash() => r'60c3f650caca88f286d6981787661fd120b03f17';

/// See also [VectorsNotifier].
@ProviderFor(VectorsNotifier)
final vectorsNotifierProvider =
    AutoDisposeAsyncNotifierProvider<VectorsNotifier, List<Vector>>.internal(
  VectorsNotifier.new,
  name: r'vectorsNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$vectorsNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$VectorsNotifier = AutoDisposeAsyncNotifier<List<Vector>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
