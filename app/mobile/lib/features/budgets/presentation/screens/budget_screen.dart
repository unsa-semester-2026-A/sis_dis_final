import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../../../accounts/presentation/screens/dashboard_screen.dart';

/// Provider para los límites de presupuesto por nodo, almacenados en SecureStorage.
final budgetLimitsProvider = StateNotifierProvider<BudgetLimitsNotifier, Map<String, double>>(
  (ref) => BudgetLimitsNotifier(),
);

class BudgetLimitsNotifier extends StateNotifier<Map<String, double>> {
  static const _storage = FlutterSecureStorage();
  static const _key = 'budget_limits_v1';

  BudgetLimitsNotifier() : super({}) {
    _load();
  }

  Future<void> _load() async {
    final raw = await _storage.read(key: _key);
    if (raw != null) {
      final decoded = jsonDecode(raw) as Map<String, dynamic>;
      state = decoded.map((k, v) => MapEntry(k, (v as num).toDouble()));
    }
  }

  Future<void> setLimit(String nodeId, double limit) async {
    final next = Map<String, double>.from(state);
    next[nodeId] = limit;
    state = next;
    await _storage.write(key: _key, value: jsonEncode(next));
  }

  double getLimit(String nodeId) => state[nodeId] ?? 500.0;
}

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

  void _editLimit(BuildContext context, Node node) {
    final limits = ref.read(budgetLimitsProvider.notifier);
    final current = limits.getLimit(node.id);
    final controller = TextEditingController(text: current.toStringAsFixed(2));

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF162A30),
        title: Text(
          'Límite de "${node.name}"',
          style: const TextStyle(color: Colors.white, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ingresa el límite mensual para esta categoría:',
              style: TextStyle(color: Colors.white70, fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              autofocus: true,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Límite (${node.currency})',
                labelStyle: const TextStyle(color: Colors.white70),
                prefixText: '${node.currency} ',
                prefixStyle: const TextStyle(color: Color(0xFF00FFCC)),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: Colors.white30),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: Color(0xFF00FFCC)),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFCC),
              foregroundColor: const Color(0xFF0F2027),
            ),
            onPressed: () {
              final val = double.tryParse(controller.text.trim());
              if (val != null && val > 0) {
                ref.read(budgetLimitsProvider.notifier).setLimit(node.id, val);
              }
              Navigator.pop(ctx);
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);
    final budgetLimits = ref.watch(budgetLimitsProvider);

    // Calcular el rango del mes
    final start = DateTime(_selectedMonth.year, _selectedMonth.month, 1);
    final end = DateTime(_selectedMonth.year, _selectedMonth.month + 1, 0, 23, 59, 59);

    final List<String> months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

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
          title: const Text('Presupuesto Mensual', style: TextStyle(color: Colors.white)),
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
              final sinkNodes = nodes.where((n) => n.nodeType == NodeType.sink).toList();

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 16),
                    // Selector de Mes
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.chevron_left, color: Color(0xFF00FFCC), size: 30),
                            onPressed: () => _changeMonth(-1),
                          ),
                          Column(
                            children: [
                              Text(
                                '${months[_selectedMonth.month - 1]} ${_selectedMonth.year}',
                                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                              const Text(
                                'Presupuesto por categoría',
                                style: TextStyle(color: Colors.white38, fontSize: 11),
                              ),
                            ],
                          ),
                          IconButton(
                            icon: const Icon(Icons.chevron_right, color: Color(0xFF00FFCC), size: 30),
                            onPressed: () => _changeMonth(1),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Hint de ayuda
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, color: Colors.white38, size: 14),
                          SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              'Toca el ícono de editar de cada categoría para ajustar su límite mensual.',
                              style: TextStyle(color: Colors.white38, fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: sinkNodes.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.category_outlined, color: Colors.white24, size: 48),
                                  const SizedBox(height: 12),
                                  const Text(
                                    'No hay categorías de gasto aún.',
                                    style: TextStyle(color: Colors.white38, fontSize: 15),
                                  ),
                                  const SizedBox(height: 8),
                                  const Text(
                                    'Crea una categoría (tipo "Gasto") desde el dashboard.',
                                    style: TextStyle(color: Colors.white24, fontSize: 12),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 20),
                                  OutlinedButton.icon(
                                    onPressed: () => context.push('/nodes/create'),
                                    icon: const Icon(Icons.add, color: Color(0xFF00FFCC)),
                                    label: const Text('Crear categoría', style: TextStyle(color: Color(0xFF00FFCC))),
                                    style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFF00FFCC))),
                                  ),
                                ],
                              ),
                            )
                          : ListView.separated(
                              itemCount: sinkNodes.length,
                              separatorBuilder: (context, index) => const SizedBox(height: 12),
                              itemBuilder: (context, index) {
                                final node = sinkNodes[index];
                                final limit = budgetLimits[node.id] ?? 500.0;
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
                                          Expanded(
                                            child: Text(
                                              node.name,
                                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                          Row(
                                            children: [
                                              Text(
                                                balanceAsync.when(
                                                  data: (val) => '${node.currency} $val',
                                                  loading: () => '...',
                                                  error: (_, __) => 'Error',
                                                ),
                                                style: const TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold, fontSize: 15),
                                              ),
                                              const SizedBox(width: 4),
                                              GestureDetector(
                                                onTap: () => _editLimit(context, node),
                                                child: Container(
                                                  padding: const EdgeInsets.all(4),
                                                  decoration: BoxDecoration(
                                                    color: Colors.white.withOpacity(0.08),
                                                    borderRadius: BorderRadius.circular(6),
                                                  ),
                                                  child: const Icon(Icons.edit_outlined, color: Colors.white54, size: 16),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 12),
                                      // Barra de progreso con límite real
                                      balanceAsync.when(
                                        data: (val) {
                                          final amount = double.tryParse(val) ?? 0.0;
                                          final percent = limit > 0 ? (amount / limit).clamp(0.0, 1.0) : 0.0;
                                          final isOver = amount > limit;

                                          return Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              ClipRRect(
                                                borderRadius: BorderRadius.circular(4),
                                                child: LinearProgressIndicator(
                                                  value: percent,
                                                  backgroundColor: Colors.white12,
                                                  color: isOver
                                                      ? Colors.redAccent
                                                      : percent >= 0.8
                                                          ? Colors.orangeAccent
                                                          : const Color(0xFF00FFCC),
                                                  minHeight: 8,
                                                ),
                                              ),
                                              const SizedBox(height: 6),
                                              Row(
                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                children: [
                                                   isOver
                                                      ? Row(
                                                          mainAxisSize: MainAxisSize.min,
                                                          children: [
                                                            const Icon(Icons.warning, color: Colors.redAccent, size: 12),
                                                            const SizedBox(width: 4),
                                                            Text(
                                                              'Excedido en ${node.currency} ${(amount - limit).toStringAsFixed(2)}',
                                                              style: const TextStyle(
                                                                color: Colors.redAccent,
                                                                fontSize: 11,
                                                                fontWeight: FontWeight.bold,
                                                              ),
                                                            ),
                                                          ],
                                                        )
                                                      : Text(
                                                          '${(percent * 100).toInt()}% consumido',
                                                          style: const TextStyle(
                                                            color: Colors.white30,
                                                            fontSize: 11,
                                                          ),
                                                        ),
                                                  Text(
                                                    'Límite: ${node.currency} ${limit.toStringAsFixed(2)}',
                                                    style: const TextStyle(color: Colors.white30, fontSize: 11),
                                                  ),

                                                ],
                                              ),
                                            ],
                                          );
                                        },
                                        loading: () => const LinearProgressIndicator(
                                          backgroundColor: Colors.white12,
                                          color: Color(0xFF00FFCC),
                                          minHeight: 8,
                                        ),
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
    ),
  );
}
}

