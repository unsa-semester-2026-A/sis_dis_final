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

class _ReportsScreenState extends ConsumerState<ReportsScreen> {
  bool _isTagMode = false;
  final _tagKeyController = TextEditingController();
  final _tagValController = TextEditingController();
  
  String _searchKey = '';
  String _searchVal = '';

  final Set<String> _selectedNodeIds = {};

  @override
  void dispose() {
    _tagKeyController.dispose();
    _tagValController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);
    final vectorsAsync = ref.watch(vectorsNotifierProvider);

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
          title: const Text('AnÃ¡lisis y Reportes', style: TextStyle(color: Colors.white)),
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
                return Column(
                  children: [
                    const SizedBox(height: 12),
                    // Selector de modo
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: !_isTagMode ? const Color(0xFF00FFCC) : Colors.white12,
                                foregroundColor: !_isTagMode ? const Color(0xFF0F2027) : Colors.white70,
                              ),
                              onPressed: () => setState(() => _isTagMode = false),
                              child: const Text('Por Nodos'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _isTagMode ? const Color(0xFF00FFCC) : Colors.white12,
                                foregroundColor: _isTagMode ? const Color(0xFF0F2027) : Colors.white70,
                              ),
                              onPressed: () => setState(() => _isTagMode = true),
                              child: const Text('Por etiquetas'),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    Expanded(
                      child: !_isTagMode
                          ? _buildNodeReport(nodes)
                          : _buildTagNettingReport(vectorsAsync, nodes),
                    ),
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

  Widget _buildNodeReport(List<Node> nodes) {
    if (nodes.isEmpty) return const SizedBox.shrink();

    return Column(
      children: [
        const Padding(
          padding: EdgeInsets.all(16.0),
          child: Text(
            'Selecciona cuentas/categorÃ­as para comparar sus balances:',
            style: TextStyle(color: Colors.white70, fontSize: 13),
          ),
        ),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: nodes.length,
            separatorBuilder: (context, index) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final node = nodes[index];
              final isChecked = _selectedNodeIds.contains(node.id);
              final balanceAsync = ref.watch(nodeBalanceProvider(node.id));

              return CheckboxListTile(
                tileColor: Colors.white.withOpacity(0.04),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                title: Text(node.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                subtitle: Text('Tipo: ${node.nodeType.value}', style: const TextStyle(color: Colors.white30, fontSize: 11)),
                value: isChecked,
                activeColor: const Color(0xFF00FFCC),
                checkColor: const Color(0xFF0F2027),
                onChanged: (val) {
                  setState(() {
                    if (val == true) {
                      _selectedNodeIds.add(node.id);
                    } else {
                      _selectedNodeIds.remove(node.id);
                    }
                  });
                },
                secondary: Text(
                  balanceAsync.when(
                    data: (v) => '${node.currency} $v',
                    loading: () => '...',
                    error: (_, __) => 'Error',
                  ),
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTagNettingReport(AsyncValue<List<Vector>> vectorsAsync, List<Node> nodes) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _tagKeyController,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Clave (ej: trip)',
                        hintStyle: const TextStyle(color: Colors.white38),
                        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Colors.white30)),
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
                        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Colors.white30)),
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
                ),
                icon: const Icon(Icons.calculate_outlined),
                label: const Text('Calcular balance por etiquetas', style: TextStyle(fontWeight: FontWeight.bold)),
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
            error: (err, _) => Center(child: Text('Error: $err')),
            data: (vectors) {
              if (_searchKey.isEmpty || _searchVal.isEmpty) {
                return const Center(child: Text('Ingresa clave y valor de tag para calcular', style: TextStyle(color: Colors.white38)));
              }

              // Filtrar vectores por tag
              final matching = vectors.where((v) {
                final val = v.tags[_searchKey];
                return val != null && val.toLowerCase() == _searchVal.toLowerCase();
              }).toList();

              if (matching.isEmpty) {
                return const Center(child: Text('No hay vectores con esa etiqueta', style: TextStyle(color: Colors.white38)));
              }

              double totalNet = 0.0;
              final Map<String, double> nodesAggregation = {};

              for (var v in matching) {
                // Sumar netting. Como los SINK representan salidas, sumamos la cantidad recibida
                totalNet += v.amount * v.exchangeRate;
                
                final target = nodes.firstWhere((n) => n.id == v.targetNodeId, orElse: () => null as dynamic);
                final name = target?.name ?? 'Desconocido';
                nodesAggregation[name] = (nodesAggregation[name] ?? 0.0) + (v.amount * v.exchangeRate);
              }

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
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
                          const Text('Netting Consolidado del Tag', style: TextStyle(color: Colors.white70, fontSize: 13)),
                          const SizedBox(height: 8),
                          Text(
                            'S/. ${totalNet.toStringAsFixed(2)}',
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF00FFCC)),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),
                    const Text('Desglose por Destino', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 12),
                    Expanded(
                      child: ListView.separated(
                        itemCount: nodesAggregation.length,
                        separatorBuilder: (context, index) => const Divider(color: Colors.white10),
                        itemBuilder: (context, index) {
                          final key = nodesAggregation.keys.elementAt(index);
                          final val = nodesAggregation[key]!;
                          return ListTile(
                            title: Text(key, style: const TextStyle(color: Colors.white)),
                            trailing: Text('S/. ${val.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.bold)),
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

