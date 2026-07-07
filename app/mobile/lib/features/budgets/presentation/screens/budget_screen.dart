import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../../../accounts/presentation/screens/dashboard_screen.dart';

class BudgetScreen extends ConsumerStatefulWidget {
  const BudgetScreen({super.key});

  @override
  ConsumerState<BudgetScreen> createState() => _BudgetScreenState();
}

class _BudgetScreenState extends ConsumerState<BudgetScreen> {
  DateTime _selectedMonth = DateTime(DateTime.now().year, DateTime.now().month);

  void _changeMonth(int increment) {
    setState(() {
      _selectedMonth = DateTime(_selectedMonth.year, _selectedMonth.month + increment);
    });
  }

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);

    // Calcular el rango del mes
    final start = DateTime(_selectedMonth.year, _selectedMonth.month, 1);
    final end = DateTime(_selectedMonth.year, _selectedMonth.month + 1, 0, 23, 59, 59);

    final List<String> months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F2027),
        elevation: 0,
        title: const Text('Presupuestos y Categorías', style: TextStyle(color: Colors.white)),
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
            error: (err, _) => Center(child: Text('Error: $err')),
            data: (nodes) {
              final sinkNodes = nodes.where((n) => n.nodeType == NodeType.sink).toList();

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 16),
                    // Selector de Mes
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.chevron_left, color: Color(0xFF00FFCC), size: 30),
                          onPressed: () => _changeMonth(-1),
                        ),
                        Text(
                          '${months[_selectedMonth.month - 1]} ${_selectedMonth.year}',
                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        IconButton(
                          icon: const Icon(Icons.chevron_right, color: Color(0xFF00FFCC), size: 30),
                          onPressed: () => _changeMonth(1),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Monitoreo de Gasto por Categoría',
                      style: TextStyle(color: Colors.white70, fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: sinkNodes.isEmpty
                          ? const Center(child: Text('No hay categorías (SINK) registradas.', style: TextStyle(color: Colors.white38)))
                          : ListView.separated(
                              itemCount: sinkNodes.length,
                              separatorBuilder: (context, index) => const SizedBox(height: 12),
                              itemBuilder: (context, index) {
                                final node = sinkNodes[index];
                                final balanceAsync = ref.watch(nodeBalanceProvider(node.id, start: start, end: end));

                                return Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.04),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(color: Colors.white10),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(node.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                                          Text(
                                            balanceAsync.when(
                                              data: (val) => '${node.currency} $val',
                                              loading: () => '...',
                                              error: (_, __) => 'Error',
                                            ),
                                            style: const TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold, fontSize: 15),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 12),
                                      // Barra de progreso de ejemplo (límite hardcodeado de 1000.0 PEN en UI)
                                      balanceAsync.when(
                                        data: (val) {
                                          final amount = double.tryParse(val) ?? 0.0;
                                          const limit = 1000.0;
                                          final percent = (amount / limit).clamp(0.0, 1.0);

                                          return Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              LinearProgressIndicator(
                                                value: percent,
                                                backgroundColor: Colors.white12,
                                                color: percent >= 0.9 ? Colors.redAccent : const Color(0xFF00FFCC),
                                                minHeight: 6,
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                              const SizedBox(height: 6),
                                              Row(
                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                children: [
                                                  Text(
                                                    '${(percent * 100).toInt()}% consumido',
                                                    style: const TextStyle(color: Colors.white30, fontSize: 11),
                                                  ),
                                                  const Text(
                                                    'Meta UI: S/. 1,000.00',
                                                    style: TextStyle(color: Colors.white30, fontSize: 11),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          );
                                        },
                                        loading: () => const LinearProgressIndicator(),
                                        error: (_, __) => const SizedBox.shrink(),
                                      ),
                                    ],
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
      bottomNavigationBar: buildGlobalBottomNavigationBar(context, 2),
    );
  }
}
