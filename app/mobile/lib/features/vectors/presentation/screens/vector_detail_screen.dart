import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/vectors_provider.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../../domain/entities/vector.dart';

class VectorDetailScreen extends ConsumerWidget {
  const VectorDetailScreen({super.key, required this.vectorId});

  final String vectorId;

  void _reclasificar(BuildContext context, WidgetRef ref, Vector vector, List<Node> nodes) {
    // Filtrar nodos SINK para reclasificación
    final sinkNodes = nodes.where((n) => n.nodeType == NodeType.sink && n.isActive).toList();

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF162A30),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Reclasificar Categoría Gasto',
                  style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Esto emitirá un nuevo vector corrector de clasificación con el mismo Lineage Token para mantener el netting en cero.',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: ListView.separated(
                    itemCount: sinkNodes.length,
                    separatorBuilder: (context, index) => const Divider(color: Colors.white10),
                    itemBuilder: (context, index) {
                      final n = sinkNodes[index];
                      return ListTile(
                        title: Text(n.name, style: const TextStyle(color: Colors.white)),
                        trailing: const Icon(Icons.chevron_right, color: Color(0xFF00FFCC)),
                        onTap: () async {
                          Navigator.pop(context);
                          
                          // Emitir el vector compensatorio: del destino antiguo (SINK viejo) al destino nuevo (SINK nuevo)
                          // Esto drena el saldo del SINK viejo y lo pasa al correcto.
                          await ref.read(vectorsNotifierProvider.notifier).emitVector(
                            sourceNodeId: vector.targetNodeId, // Antiguo destino es el nuevo origen
                            targetNodeId: n.id, // Nuevo SINK
                            amount: vector.amount,
                            lineageToken: vector.lineageToken,
                            tags: {'reclasificado': 'true', 'original_vector': vector.id},
                          );

                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Categoría reclasificada exitosamente.'),
                                backgroundColor: Colors.green,
                              ),
                            );
                            context.go('/');
                          }
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vectorsAsync = ref.watch(vectorsNotifierProvider);
    final nodesAsync = ref.watch(nodesNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F2027),
        elevation: 0,
        title: const Text('Detalle de Vector', style: TextStyle(color: Colors.white)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => context.go('/vectors/history'),
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
          child: vectorsAsync.when(
            loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
            error: (err, _) => Center(child: Text('Error: $err')),
            data: (vectors) {
              final vector = vectors.where((v) => v.id == vectorId).firstOrNull;
              if (vector == null) {
                return const Center(child: Text('Vector no encontrado', style: TextStyle(color: Colors.white)));
              }

              return nodesAsync.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (err, _) => Center(child: Text('Error al leer nodos: $err')),
                data: (nodes) {
                  final sourceNode = nodes.where((n) => n.id == vector.sourceNodeId).firstOrNull;
                  final targetNode = nodes.where((n) => n.id == vector.targetNodeId).firstOrNull;

                  // Buscar vectores de la misma familia de linaje
                  final lineageFamily = vectors.where((v) => v.lineageToken == vector.lineageToken).toList();

                  return SingleChildScrollView(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Card de monto
                        Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.06),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: Column(
                            children: [
                              const Text('Monto de la Transacción', style: TextStyle(color: Colors.white70, fontSize: 13)),
                              const SizedBox(height: 8),
                              Text(
                                'S/. ${vector.amount.toStringAsFixed(2)}',
                                style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Color(0xFF00FFCC)),
                              ),
                              const SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                children: [
                                  Column(
                                    children: [
                                      const Text('Origen', style: TextStyle(color: Colors.white38, fontSize: 11)),
                                      const SizedBox(height: 4),
                                      Text(sourceNode?.name ?? "Desconocido", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                    ],
                                  ),
                                  const Icon(Icons.arrow_forward, color: Color(0xFF00FFCC), size: 18),
                                  Column(
                                    children: [
                                      const Text('Destino', style: TextStyle(color: Colors.white38, fontSize: 11)),
                                      const SizedBox(height: 4),
                                      Text(targetNode?.name ?? "Desconocido", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                    ],
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),
                        // Detalles de auditoría
                        const Text('Detalles de Auditoría Logística', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                        const SizedBox(height: 12),
                        _buildAuditField('UUID Vector', vector.id),
                        _buildAuditField('Lineage Token', vector.lineageToken),
                        _buildAuditField('Fecha Efectiva', vector.effectiveAt.toLocal().toString()),
                        _buildAuditField('Fecha Sistema', vector.systemAt.toLocal().toString()),
                        _buildAuditField('Tipo de Cambio', vector.exchangeRate.toStringAsFixed(6)),
                        if (vector.transactionId != null) _buildAuditField('TAP Ref ID', vector.transactionId!),
                        if (vector.tags.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          const Text('Etiquetas (Tags)', style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600)),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: vector.tags.entries.map((e) {
                              return Chip(
                                backgroundColor: Colors.white.withOpacity(0.06),
                                label: Text('${e.key}: ${e.value}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                              );
                            }).toList(),
                          ),
                        ],
                        const SizedBox(height: 24),
                        // Familia de linaje
                        if (lineageFamily.length > 1) ...[
                          const Text('Familia de Netting (Mismo Lineage)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(color: Colors.white.withOpacity(0.04), borderRadius: BorderRadius.circular(12)),
                            child: Column(
                              children: lineageFamily.map((v) {
                                final isOutflow = v.sourceNodeId == vector.sourceNodeId;
                                return Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                                  child: Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        'Vector corrector... ${v.id.substring(0, 8)}',
                                        style: const TextStyle(color: Colors.white54, fontSize: 12),
                                      ),
                                      Text(
                                        '${isOutflow ? "-" : "+"} S/. ${v.amount.toStringAsFixed(2)}',
                                        style: TextStyle(color: isOutflow ? Colors.redAccent : Colors.greenAccent, fontSize: 12),
                                      ),
                                    ],
                                  ),
                                );
                              }).toList(),
                            ),
                          ),
                          const SizedBox(height: 24),
                        ],
                        // Acciones
                        if (targetNode != null && targetNode.nodeType == NodeType.sink) ...[
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF00FFCC),
                              foregroundColor: const Color(0xFF0F2027),
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.category_outlined),
                            label: const Text('Reclasificar Categoría', style: TextStyle(fontWeight: FontWeight.bold)),
                            onPressed: () => _reclasificar(context, ref, vector, nodes),
                          ),
                          const SizedBox(height: 12),
                        ],
                        OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFF00FFCC),
                            side: const BorderSide(color: Color(0xFF00FFCC)),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          icon: const Icon(Icons.copy_outlined),
                          label: const Text('Duplicar Movimiento'),
                          onPressed: () {
                            context.go('/vectors/emit');
                          },
                        ),
                      ],
                    ),
                  );
                },
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildAuditField(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Colors.white38, fontSize: 11)),
          const SizedBox(height: 2),
          SelectableText(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 13, fontFamily: 'monospace'),
          ),
        ],
      ),
    );
  }
}
