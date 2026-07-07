import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../providers/nodes_provider.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/entities/node.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  DateTime? _lastPressed;

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);
    final user = ref.watch(authNotifierProvider).valueOrNull;
    final isConnected = ref.watch(connectivityProvider);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        final now = DateTime.now();
        if (_lastPressed == null || now.difference(_lastPressed!) > const Duration(seconds: 2)) {
          _lastPressed = now;
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Presiona atrás otra vez para salir'),
                duration: Duration(seconds: 2),
              ),
            );
          }
          return;
        }
        await SystemNavigator.pop();
      },
      child: Scaffold(
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
            error: (err, stack) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
            data: (nodes) {
              // Filtrar nodos ASSET para calcular el Safe-to-Spend
              final assetNodes = nodes.where((n) => n.nodeType == NodeType.asset && n.isActive).toList();

              return RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(nodesNotifierProvider);
                  ref.invalidate(nodeBalanceProvider);
                },
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 16),
                      // Header
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Hola, ${user?.name ?? "Rafael"}',
                                style: const TextStyle(fontSize: 16, color: Colors.white70),
                              ),
                              Row(
                                children: [
                                  const Text(
                                    'Spondylus Wallet',
                                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
                                  ),
                                  const SizedBox(width: 8),
                                  Container(
                                    width: 6,
                                    height: 6,
                                    decoration: BoxDecoration(
                                      color: isConnected ? const Color(0xFF00FFCC) : Colors.cyanAccent,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.sync, color: Color(0xFF00FFCC)),
                                onPressed: () {
                                  // Restablece el indicador optimistamente antes de recargar
                                  ref.read(connectivityProvider.notifier).state = true;
                                  ref.invalidate(nodesNotifierProvider);
                                  ref.invalidate(nodeBalanceProvider);
                                },
                              ),
                              IconButton(
                                icon: const Icon(Icons.account_circle_outlined, color: Colors.white, size: 28),
                                onPressed: () => context.push('/profile'),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      // Safe-to-Spend Card
                      _buildSafeToSpendCard(context, ref, assetNodes),
                      const SizedBox(height: 24),
                      // Secciones de nodos
                      _buildNodeSection(context, ref, 'Cuentas y Ahorros', Icons.account_balance, nodes.where((n) => n.nodeType == NodeType.asset).toList()),
                      _buildNodeSection(context, ref, 'Deudas y Préstamos', Icons.credit_card, nodes.where((n) => n.nodeType == NodeType.liability).toList()),
                      _buildNodeSection(context, ref, 'Fuentes de Ingresos', Icons.trending_up, nodes.where((n) => n.nodeType == NodeType.source).toList()),
                      _buildNodeSection(context, ref, 'Categorías de Gasto', Icons.shopping_cart, nodes.where((n) => n.nodeType == NodeType.sink).toList()),
                      const SizedBox(height: 80), // Espacio para el BottomBar
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showQuickActionsMenu(context),
        backgroundColor: const Color(0xFF00FFCC),
        foregroundColor: const Color(0xFF0F2027),
        icon: const Icon(Icons.add),
        label: const Text('Nueva operación', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      bottomNavigationBar: _buildBottomNavigationBar(context, 0),
    ),
  );
}

  Widget _buildSafeToSpendCard(BuildContext context, WidgetRef ref, List<Node> assetNodes) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Safe-to-Spend Consolidado',
            style: TextStyle(color: Colors.white70, fontSize: 14),
          ),
          const SizedBox(height: 8),
          // Sumar balances de manera síncrona/asíncrona
          Consumer(
            builder: (context, ref, child) {
              double total = 0;
              for (var node in assetNodes) {
                final balanceAsync = ref.watch(nodeBalanceProvider(node.id));
                total += double.tryParse(balanceAsync.valueOrNull ?? '0.00') ?? 0.0;
              }
              return Text(
                'S/. ${total.toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
              );
            },
          ),
          const SizedBox(height: 8),
          const Text(
            'Dinero libre disponible de tus cuentas activas',
            style: TextStyle(color: Colors.white38, fontSize: 12),
          ),
        ],
      ),
    );
  }

  IconData _iconForNodeType(NodeType type) {
    switch (type) {
      case NodeType.asset:
        return Icons.account_balance_outlined;
      case NodeType.liability:
        return Icons.credit_card_outlined;
      case NodeType.source:
        return Icons.trending_up;
      case NodeType.sink:
        return Icons.shopping_bag_outlined;
    }
  }

  Widget _buildNodeSection(BuildContext context, WidgetRef ref, String title, IconData icon, List<Node> nodes) {
    if (nodes.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.0),
          child: Row(
            children: [
              Icon(icon, color: const Color(0xFF00FFCC), size: 18),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ],
          ),
        ),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: nodes.length,
          separatorBuilder: (context, index) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final node = nodes[index];
            final balanceAsync = ref.watch(nodeBalanceProvider(node.id));

            return Opacity(
              opacity: node.isActive ? 1.0 : 0.5,
              child: ListTile(
                onTap: () => context.push('/node/${node.id}'),
                tileColor: Colors.white.withOpacity(0.04),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: Colors.white10),
                ),
                leading: CircleAvatar(
                  backgroundColor: const Color(0xFF00FFCC).withOpacity(0.12),
                  child: Icon(
                    _iconForNodeType(node.nodeType),
                    color: const Color(0xFF00FFCC),
                  ),
                ),
                title: Text(node.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                subtitle: Text(
                  node.isActive ? 'Activo' : 'Archivado',
                  style: TextStyle(color: node.isActive ? Colors.greenAccent : Colors.white30, fontSize: 12),
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      balanceAsync.when(
                        data: (val) => '${node.currency} $val',
                        loading: () => '...',
                        error: (_, __) => 'Error',
                      ),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    const SizedBox(width: 4),
                    const Icon(Icons.chevron_right, color: Colors.white54),
                  ],
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  void _showQuickActionsMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF162A30),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Acciones Rápidas',
                  style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.swap_horiz, color: Color(0xFF00FFCC)),
                  title: const Text('Registrar ingreso / gasto / transferencia', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Mueve dinero entre tus cuentas y categorías', style: TextStyle(color: Colors.white38, fontSize: 11)),
                  onTap: () {
                    Navigator.pop(context);
                    context.push('/vectors/emit');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.account_balance_outlined, color: Color(0xFF00FFCC)),
                  title: const Text('Crear cuenta o categoría', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Agrega una cuenta bancaria, deuda o categoría de gasto', style: TextStyle(color: Colors.white38, fontSize: 11)),
                  onTap: () {
                    Navigator.pop(context);
                    context.push('/nodes/create');
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildBottomNavigationBar(BuildContext context, int currentIndex) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      backgroundColor: const Color(0xFF0F2027),
      selectedItemColor: const Color(0xFF00FFCC),
      unselectedItemColor: Colors.white54,
      type: BottomNavigationBarType.fixed,
      onTap: (index) {
        if (index == 0) context.go('/');
        if (index == 1) context.go('/vectors/history');
        if (index == 2) context.go('/budgets');
        if (index == 3) context.go('/reports');
      },
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), label: 'Inicio'),
        BottomNavigationBarItem(icon: Icon(Icons.history_toggle_off), label: 'Movimientos'),
        BottomNavigationBarItem(icon: Icon(Icons.pie_chart_outline), label: 'Presupuesto'),
        BottomNavigationBarItem(icon: Icon(Icons.bar_chart_outlined), label: 'Reportes'),
      ],
    );
  }
}

// Helper externo para poder usar el Navbar desde cualquier pantalla
Widget buildGlobalBottomNavigationBar(BuildContext context, int currentIndex) {
  return BottomNavigationBar(
    currentIndex: currentIndex,
    backgroundColor: const Color(0xFF0F2027),
    selectedItemColor: const Color(0xFF00FFCC),
    unselectedItemColor: Colors.white54,
    type: BottomNavigationBarType.fixed,
    onTap: (index) {
      if (index == 0) context.go('/');
      if (index == 1) context.go('/vectors/history');
      if (index == 2) context.go('/budgets');
      if (index == 3) context.go('/reports');
    },
    items: const [
      BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), label: 'Inicio'),
      BottomNavigationBarItem(icon: Icon(Icons.history_toggle_off), label: 'Movimientos'),
      BottomNavigationBarItem(icon: Icon(Icons.pie_chart_outline), label: 'Presupuesto'),
      BottomNavigationBarItem(icon: Icon(Icons.bar_chart_outlined), label: 'Reportes'),
    ],
  );
}

