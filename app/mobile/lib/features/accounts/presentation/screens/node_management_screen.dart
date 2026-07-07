import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/nodes_provider.dart';
import '../../domain/entities/node.dart';

String _translateNodeType(NodeType type) {
  switch (type) {
    case NodeType.asset:
      return 'Cuenta / Ahorro';
    case NodeType.liability:
      return 'Obligación / Préstamo';
    case NodeType.source:
      return 'Fuente de Ingresos';
    case NodeType.sink:
      return 'Categoría de Gasto';
  }
}

class NodeManagementScreen extends ConsumerWidget {
  const NodeManagementScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesNotifierProvider);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        context.go('/');
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F2027),
          elevation: 0,
          title: const Text('Gestión de Nodos', style: TextStyle(color: Colors.white)),
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
            child: nodesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
              error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
              data: (nodes) {
                return DefaultTabController(
                  length: 5,
                  child: Column(
                    children: [
                      const TabBar(
                        isScrollable: true,
                        indicatorColor: Color(0xFF00FFCC),
                        labelColor: Color(0xFF00FFCC),
                        unselectedLabelColor: Colors.white70,
                        tabs: [
                          Tab(text: 'Todos'),
                          Tab(text: 'Cuentas (ASSET)'),
                          Tab(text: 'Obligaciones (LIABILITY)'),
                          Tab(text: 'Ingresos (SOURCE)'),
                          Tab(text: 'Gastos (SINK)'),
                        ],
                      ),
                      Expanded(
                        child: TabBarView(
                          children: [
                            _buildList(context, ref, nodes),
                            _buildList(context, ref, nodes.where((n) => n.nodeType == NodeType.asset).toList()),
                            _buildList(context, ref, nodes.where((n) => n.nodeType == NodeType.liability).toList()),
                            _buildList(context, ref, nodes.where((n) => n.nodeType == NodeType.source).toList()),
                            _buildList(context, ref, nodes.where((n) => n.nodeType == NodeType.sink).toList()),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => context.push('/nodes/create'),
          backgroundColor: const Color(0xFF00FFCC),
          foregroundColor: const Color(0xFF0F2027),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }

  Widget _buildList(BuildContext context, WidgetRef ref, List<Node> nodes) {
    if (nodes.isEmpty) {
      return const Center(child: Text('No hay nodos registrados en esta categoría', style: TextStyle(color: Colors.white38)));
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: nodes.length,
      separatorBuilder: (context, index) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final node = nodes[index];
        final balanceAsync = ref.watch(nodeBalanceProvider(node.id));

        return ListTile(
          onTap: () => context.push('/node/${node.id}'),
          tileColor: Colors.white.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Colors.white10),
          ),
          title: Text(node.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
          subtitle: Text(
            'Tipo: ${_translateNodeType(node.nodeType)} | ${node.isActive ? "Activo" : "Archivado"}',
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
          trailing: Text(
            balanceAsync.when(
              data: (val) => '${node.currency} $val',
              loading: () => '...',
              error: (_, __) => 'Error',
            ),
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        );
      },
    );
  }
}
