import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/vectors_provider.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/presentation/screens/dashboard_screen.dart';

class VectorHistoryScreen extends ConsumerStatefulWidget {
  const VectorHistoryScreen({super.key});

  @override
  ConsumerState<VectorHistoryScreen> createState() => _VectorHistoryScreenState();
}

class _VectorHistoryScreenState extends ConsumerState<VectorHistoryScreen> {
  final _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vectorsAsync = ref.watch(vectorsNotifierProvider);
    final nodesAsync = ref.watch(nodesNotifierProvider);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (mounted) {
          context.go('/');
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F2027),
          elevation: 0,
          title: const Text('Historial de Movimientos', style: TextStyle(color: Colors.white)),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => context.go('/'),
          ),
        ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F2027),
              Color(0xFF203A43),
              Color(0xFF2C5364),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Barra de búsqueda
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: TextField(
                  controller: _searchController,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Buscar por Lineage Token o Tag...',
                    hintStyle: const TextStyle(color: Colors.white38),
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF00FFCC)),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, color: Colors.white54),
                            onPressed: () {
                              _searchController.clear();
                              setState(() => _searchQuery = '');
                            },
                          )
                        : null,
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Colors.white30),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFF00FFCC)),
                    ),
                  ),
                  onChanged: (val) {
                    setState(() => _searchQuery = val.trim().toLowerCase());
                  },
                ),
              ),
              Expanded(
                child: vectorsAsync.when(
                  loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
                  error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
                  data: (vectors) {
                    // Filtrar localmente según la búsqueda
                    final filtered = vectors.where((v) {
                      if (_searchQuery.isEmpty) return true;
                      
                      final matchLineage = v.lineageToken.toLowerCase().contains(_searchQuery);
                      final matchTags = v.tags.entries.any(
                        (e) => e.key.toLowerCase().contains(_searchQuery) || e.value.toLowerCase().contains(_searchQuery),
                      );
                      
                      return matchLineage || matchTags;
                    }).toList();

                    // Ordenar descendente por fecha efectiva
                    filtered.sort((a, b) => b.effectiveAt.compareTo(a.effectiveAt));

                    if (filtered.isEmpty) {
                      return const Center(child: Text('No se encontraron transacciones', style: TextStyle(color: Colors.white38)));
                    }

                    return nodesAsync.when(
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (err, _) => Center(child: Text('Error al leer nodos: $err')),
                      data: (nodes) {
                        return ListView.separated(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0),
                          itemCount: filtered.length,
                          separatorBuilder: (context, index) => const Divider(color: Colors.white10),
                          itemBuilder: (context, index) {
                            final vector = filtered[index];
                            final sourceNode = nodes.where((n) => n.id == vector.sourceNodeId).firstOrNull;
                            final targetNode = nodes.where((n) => n.id == vector.targetNodeId).firstOrNull;

                            return ListTile(
                              onTap: () => context.push('/vector/${vector.id}'),
                              leading: CircleAvatar(
                                backgroundColor: const Color(0xFF00FFCC).withOpacity(0.12),
                                child: const Icon(Icons.swap_horiz, color: Color(0xFF00FFCC)),
                              ),
                              title: Text(
                                '${sourceNode?.name ?? "Origen"} → ${targetNode?.name ?? "Destino"}',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text(
                                    'Fecha: ${vector.effectiveAt.day}/${vector.effectiveAt.month}/${vector.effectiveAt.year}',
                                    style: const TextStyle(color: Colors.white30, fontSize: 12),
                                  ),
                                  if (vector.tags.isNotEmpty) ...[
                                    const SizedBox(height: 6),
                                    Wrap(
                                      spacing: 4,
                                      runSpacing: 4,
                                      children: vector.tags.entries.map((e) {
                                        return Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: Colors.white.withOpacity(0.06),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text('${e.key}: ${e.value}', style: const TextStyle(color: Colors.white70, fontSize: 10)),
                                        );
                                      }).toList(),
                                    ),
                                  ],
                                ],
                              ),
                              trailing: Text(
                                'S/. ${vector.amount.toStringAsFixed(2)}',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                              ),
                            );
                          },
                        );
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: buildGlobalBottomNavigationBar(context, 1),
    ),
  );
}
}
