import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../../../vectors/presentation/providers/vectors_provider.dart';
import '../../../vectors/domain/entities/vector.dart';
import '../../../accounts/presentation/screens/dashboard_screen.dart';

class ReportsScreen extends ConsumerStatefulWidget {
  const ReportsScreen({super.key});

  @override
  ConsumerState<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends ConsumerState<ReportsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  DateTime _selectedMonth = DateTime(DateTime.now().year, DateTime.now().month);

  // Estado modo Tags (Netting)
  final _tagKeyController = TextEditingController();
  final _tagValController = TextEditingController();
  String _searchKey = '';
  String _searchVal = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _tagKeyController.dispose();
    _tagValController.dispose();
    super.dispose();
  }

  void _changeMonth(int increment) {
    setState(() {
      _selectedMonth = DateTime(_selectedMonth.year, _selectedMonth.month + increment);
    });
  }

  final List<String> _months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);
    final vectorsAsync = ref.watch(vectorsNotifierProvider);

    final start = DateTime(_selectedMonth.year, _selectedMonth.month, 1);
    final end = DateTime(_selectedMonth.year, _selectedMonth.month + 1, 0, 23, 59, 59);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (mounted) context.go('/');
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F2027),
          elevation: 0,
          title: const Text('Análisis y Reportes', style: TextStyle(color: Colors.white)),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => context.go('/'),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: const Color(0xFF00FFCC),
            labelColor: const Color(0xFF00FFCC),
            unselectedLabelColor: Colors.white38,
            tabs: const [
              Tab(icon: Icon(Icons.arrow_downward, size: 16), text: 'Ingresos'),
              Tab(icon: Icon(Icons.arrow_upward, size: 16), text: 'Gastos'),
              Tab(icon: Icon(Icons.tag, size: 16), text: 'Por Etiqueta'),
            ],
          ),
        ),
        body: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF0F2027), Color(0xFF203A43), Color(0xFF2C5364)],
            ),
          ),
          child: SafeArea(
            child: nodesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
              error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
              data: (nodes) {
                return TabBarView(
                  controller: _tabController,
                  children: [
                    // Tab 1: Ingresos
                    _buildIncomeReport(context, nodes, start, end),
                    // Tab 2: Gastos
                    _buildExpenseReport(context, nodes, start, end),
                    // Tab 3: Tags (Netting)
                    _buildTagNettingReport(vectorsAsync, nodes),
                  ],
                );
              },
            ),
          ),
        ),
        bottomNavigationBar: buildGlobalBottomNavigationBar(context, 3),
      ),
    );
  }

  /// Header de selector de mes para usar en ingresos y gastos
  Widget _buildMonthSelector() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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
            icon: const Icon(Icons.chevron_left, color: Color(0xFF00FFCC)),
            onPressed: () => _changeMonth(-1),
          ),
          Text(
            '${_months[_selectedMonth.month - 1]} ${_selectedMonth.year}',
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right, color: Color(0xFF00FFCC)),
            onPressed: () => _changeMonth(1),
          ),
        ],
      ),
    );
  }

  // ─── Tab Ingresos ──────────────────────────────────────────────────────────

  Widget _buildIncomeReport(BuildContext context, List<Node> nodes, DateTime start, DateTime end) {
    // Ingresos = nodos SOURCE
    final sourceNodes = nodes.where((n) => n.nodeType == NodeType.source).toList();

    return Column(
      children: [
        _buildMonthSelector(),
        if (sourceNodes.isEmpty)
          const Expanded(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.savings_outlined, color: Colors.white24, size: 48),
                  SizedBox(height: 12),
                  Text('No hay fuentes de ingreso registradas.',
                      style: TextStyle(color: Colors.white38, fontSize: 15)),
                  SizedBox(height: 6),
                  Text('Crea una fuente de ingreso desde el dashboard.',
                      style: TextStyle(color: Colors.white24, fontSize: 12)),
                ],
              ),
            ),
          )
        else ...[
          // Resumen total
          _buildSummaryCard(sourceNodes, start, end, color: Colors.greenAccent, label: 'Total ingresos del mes'),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: sourceNodes.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final node = sourceNodes[index];
                final balanceAsync = ref.watch(nodeBalanceProvider(node.id, start: start, end: end));
                return _buildNodeCard(node, balanceAsync, Colors.greenAccent, Icons.arrow_downward);
              },
            ),
          ),
        ],
      ],
    );
  }

  // ─── Tab Gastos ────────────────────────────────────────────────────────────

  Widget _buildExpenseReport(BuildContext context, List<Node> nodes, DateTime start, DateTime end) {
    // Gastos = nodos SINK
    final sinkNodes = nodes.where((n) => n.nodeType == NodeType.sink).toList();

    return Column(
      children: [
        _buildMonthSelector(),
        if (sinkNodes.isEmpty)
          const Expanded(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.shopping_cart_outlined, color: Colors.white24, size: 48),
                  SizedBox(height: 12),
                  Text('No hay categorías de gasto registradas.',
                      style: TextStyle(color: Colors.white38, fontSize: 15)),
                  SizedBox(height: 6),
                  Text('Crea categorías de gasto desde el dashboard.',
                      style: TextStyle(color: Colors.white24, fontSize: 12)),
                ],
              ),
            ),
          )
        else ...[
          _buildSummaryCard(sinkNodes, start, end, color: Colors.redAccent, label: 'Total gastos del mes'),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: sinkNodes.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final node = sinkNodes[index];
                final balanceAsync = ref.watch(nodeBalanceProvider(node.id, start: start, end: end));
                return _buildNodeCard(node, balanceAsync, Colors.redAccent, Icons.arrow_upward);
              },
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildSummaryCard(List<Node> nodes, DateTime start, DateTime end, {required Color color, required String label}) {
    return Consumer(
      builder: (context, ref, _) {
        double total = 0;
        for (final n in nodes) {
          final b = ref.watch(nodeBalanceProvider(n.id, start: start, end: end));
          total += double.tryParse(b.valueOrNull ?? '0') ?? 0;
        }
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: color.withOpacity(0.08),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(color: Colors.white70, fontSize: 13)),
              Text(
                'S/. ${total.toStringAsFixed(2)}',
                style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 22),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildNodeCard(Node node, AsyncValue<String> balanceAsync, Color accentColor, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.04),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: accentColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: accentColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              node.name,
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14),
            ),
          ),
          Text(
            balanceAsync.when(
              data: (v) => '${node.currency} $v',
              loading: () => '...',
              error: (_, __) => 'Error',
            ),
            style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 15),
          ),
        ],
      ),
    );
  }

  // ─── Tab Tags/Netting ──────────────────────────────────────────────────────

  Widget _buildTagNettingReport(AsyncValue<List<Vector>> vectorsAsync, List<Node> nodes) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Consolidar por Etiqueta',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 4),
              const Text(
                'Agrupa tus gastos o ingresos bajo una misma etiqueta (ej: viaje, proyecto) y calcula el saldo neto.',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _tagKeyController,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Clave (ej: viaje)',
                        hintStyle: const TextStyle(color: Colors.white38),
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
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _tagValController,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Valor (ej: arequipa-2026)',
                        hintStyle: const TextStyle(color: Colors.white38),
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
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF00FFCC),
                  foregroundColor: const Color(0xFF0F2027),
                  minimumSize: const Size.fromHeight(48),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: const Icon(Icons.calculate_outlined),
                label: const Text('Consolidar Saldos', style: TextStyle(fontWeight: FontWeight.bold)),
                onPressed: () {
                  setState(() {
                    _searchKey = _tagKeyController.text.trim();
                    _searchVal = _tagValController.text.trim();
                  });
                },
              ),
            ],
          ),
        ),
        Expanded(
          child: vectorsAsync.when(
            loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
            error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
            data: (vectors) {
              if (_searchKey.isEmpty || _searchVal.isEmpty) {
                return const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.tag, color: Colors.white24, size: 48),
                      SizedBox(height: 12),
                      Text('Ingresa clave y valor de etiqueta para ver el consolidado.',
                          style: TextStyle(color: Colors.white38, fontSize: 13), textAlign: TextAlign.center),
                    ],
                  ),
                );
              }

              final matching = vectors.where((v) {
                final val = v.tags[_searchKey];
                return val != null && val.toLowerCase() == _searchVal.toLowerCase();
              }).toList();

              if (matching.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.search_off, color: Colors.white24, size: 48),
                      const SizedBox(height: 12),
                      Text(
                        'No hay movimientos con la etiqueta\n"$_searchKey: $_searchVal".',
                        style: const TextStyle(color: Colors.white38, fontSize: 13),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                );
              }

              double totalNet = 0.0;
              final Map<String, double> nodesAggregation = {};

              for (var v in matching) {
                totalNet += v.amount * v.exchangeRate;
                final target = nodes.where((n) => n.id == v.targetNodeId).firstOrNull;
                final name = target?.name ?? 'Desconocido';
                nodesAggregation[name] = (nodesAggregation[name] ?? 0.0) + (v.amount * v.exchangeRate);
              }

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: const Color(0xFF00FFCC).withOpacity(0.08),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFF00FFCC).withOpacity(0.2)),
                      ),
                      child: Column(
                        children: [
                          Text(
                            'Saldo Neto de "$_searchKey: $_searchVal"',
                            style: const TextStyle(color: Colors.white70, fontSize: 13),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'S/. ${totalNet.toStringAsFixed(2)}',
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF00FFCC)),
                          ),
                          Text(
                            '${matching.length} movimiento(s) encontrado(s)',
                            style: const TextStyle(color: Colors.white38, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Desglose por destino', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                    const SizedBox(height: 8),
                    Expanded(
                      child: ListView.separated(
                        itemCount: nodesAggregation.length,
                        separatorBuilder: (_, __) => const Divider(color: Colors.white10),
                        itemBuilder: (context, index) {
                          final key = nodesAggregation.keys.elementAt(index);
                          final val = nodesAggregation[key]!;
                          final pct = totalNet > 0 ? val / totalNet : 0.0;
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(key, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                                      const SizedBox(height: 4),
                                      LinearProgressIndicator(
                                        value: pct,
                                        backgroundColor: Colors.white12,
                                        color: const Color(0xFF00FFCC),
                                        minHeight: 4,
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Text(
                                  'S/. ${val.toStringAsFixed(2)}',
                                  style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.bold),
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
      ],
    );
  }
}
