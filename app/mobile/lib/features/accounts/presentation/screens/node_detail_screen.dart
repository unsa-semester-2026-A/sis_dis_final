import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/nodes_provider.dart';
import '../../../vectors/presentation/providers/vectors_provider.dart';
import '../../domain/entities/node.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class NodeDetailScreen extends ConsumerStatefulWidget {
  const NodeDetailScreen({super.key, required this.nodeId});

  final String nodeId;

  @override
  ConsumerState<NodeDetailScreen> createState() => _NodeDetailScreenState();
}

class _NodeDetailScreenState extends ConsumerState<NodeDetailScreen> {
  DateTime? _startDate;
  DateTime? _endDate;
  final _nameController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _editName(Node node) {
    _nameController.text = node.name;
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF162A30),
          title: const Text('Editar nombre', style: TextStyle(color: Colors.white)),
          content: TextField(
            controller: _nameController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: 'Nombre del nodo',
              labelStyle: TextStyle(color: Colors.white70),
              enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white30)),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar', style: TextStyle(color: Colors.white54)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF00FFCC)),
              onPressed: () async {
                final newName = _nameController.text.trim();
                if (newName.isNotEmpty) {
                  // Como guardamos la lista de nodos en SecureStorage
                  // Llamamos a un actualizador local de repositorios
                  final repo = ref.read(nodeRepositoryProvider);
                  // Buscamos y sobreescribimos
                  final list = await repo.getNodes(node.userId);
                  final idx = list.indexWhere((n) => n.id == node.id);
                  if (idx != -1) {
                    list[idx] = Node(
                      id: node.id,
                      userId: node.userId,
                      name: newName,
                      nodeType: node.nodeType,
                      currency: node.currency,
                      isActive: node.isActive,
                    );
                    // Guardamos la lista actualizada
                    const storage = FlutterSecureStorage();
                    importJsonNodes(ref, node.userId, list, storage);
                  }
                  ref.invalidate(nodesNotifierProvider);
                  if (context.mounted) Navigator.pop(context);
                }
              },
              child: const Text('Guardar', style: TextStyle(color: Color(0xFF0F2027))),
            ),
          ],
        );
      },
    );
  }

  // Guardado auxiliar
  void importJsonNodes(WidgetRef ref, String userId, List<Node> nodes, FlutterSecureStorage storage) async {
    final listModels = nodes.map((n) => {
      'id': n.id,
      'user_id': n.userId,
      'name': n.name,
      'node_type': n.nodeType.value,
      'currency': n.currency,
      'is_active': n.isActive,
    }).toList();
    await storage.write(key: 'nodes_list_$userId', value: jsonEncode(listModels));
  }

  void _archiveNode(Node node) async {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF162A30),
          title: const Text('Archivar nodo', style: TextStyle(color: Colors.white)),
          content: const Text(
            '¿Estás seguro de que deseas archivar este nodo financiero? No podrá emitir ni recibir nuevas transferencias.',
            style: TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar', style: TextStyle(color: Colors.white54)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
              onPressed: () async {
                await ref.read(nodesNotifierProvider.notifier).archiveNode(node.id);
                if (context.mounted) {
                  Navigator.pop(context);
                  context.go('/');
                }
              },
              child: const Text('Confirmar', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);
    final vectorsAsync = ref.watch(vectorsNotifierProvider);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (Navigator.of(context).canPop()) {
          context.pop();
        } else {
          context.go('/');
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F2027),
          elevation: 0,
          title: const Text('Detalle del Nodo', style: TextStyle(color: Colors.white)),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () {
              if (Navigator.of(context).canPop()) {
                context.pop();
              } else {
                context.go('/');
              }
            },
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
              final node = nodes.where((n) => n.id == widget.nodeId).firstOrNull;
              if (node == null) {
                return const Center(child: Text('Nodo no encontrado', style: TextStyle(color: Colors.white)));
              }

              // Calcular balance con o sin filtros
              final balanceAsync = ref.watch(nodeBalanceProvider(node.id, start: _startDate, end: _endDate));

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 16),
                    // Header card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.06),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Chip(
                                label: Text(node.nodeType.value),
                                backgroundColor: const Color(0xFF00FFCC).withOpacity(0.15),
                                labelStyle: const TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold),
                              ),
                              Row(
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.edit_outlined, color: Colors.white70),
                                    onPressed: () => _editName(node),
                                  ),
                                  if (node.isActive)
                                    IconButton(
                                      icon: const Icon(Icons.archive_outlined, color: Colors.redAccent),
                                      onPressed: () => _archiveNode(node),
                                    ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            node.name,
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            balanceAsync.when(
                              data: (val) => '${node.currency} $val',
                              loading: () => 'Cargando saldo...',
                              error: (_, __) => 'Error',
                            ),
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF00FFCC)),
                          ),
                          if (!node.isActive) ...[
                            const SizedBox(height: 12),
                            Container(
                              padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
                              decoration: BoxDecoration(color: Colors.redAccent.withOpacity(0.2), borderRadius: BorderRadius.circular(8)),
                              child: const Text('NODO ARCHIVADO (Inactivo)', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold)),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Filtros de fecha
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Filtro de período:', style: TextStyle(color: Colors.white70)),
                        TextButton.icon(
                          icon: const Icon(Icons.date_range, size: 16, color: Color(0xFF00FFCC)),
                          label: Text(
                            _startDate == null ? 'Todo el tiempo' : 'Filtrado',
                            style: const TextStyle(color: Color(0xFF00FFCC)),
                          ),
                          onPressed: () async {
                            final picked = await showDateRangePicker(
                              context: context,
                              firstDate: DateTime(2025),
                              lastDate: DateTime(2027),
                            );
                            if (picked != null) {
                              setState(() {
                                _startDate = picked.start;
                                _endDate = picked.end;
                              });
                            } else {
                              setState(() {
                                _startDate = null;
                                _endDate = null;
                              });
                            }
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text('Historial de Movimientos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                    const SizedBox(height: 12),
                    // Lista de vectores
                    Expanded(
                      child: vectorsAsync.when(
                        loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC))),
                        error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Colors.redAccent))),
                        data: (vectors) {
                          // Filtrar vectores de este nodo
                          final nodeVectors = vectors.where((v) {
                            final isMatch = v.sourceNodeId == node.id || v.targetNodeId == node.id;
                            if (!isMatch) return false;
                            
                            // Aplicar filtro de fecha
                            if (_startDate != null && v.effectiveAt.isBefore(_startDate!)) return false;
                            if (_endDate != null && v.effectiveAt.isAfter(_endDate!)) return false;
                            return true;
                          }).toList();

                          if (nodeVectors.isEmpty) {
                            return const Center(child: Text('No hay movimientos en este nodo', style: TextStyle(color: Colors.white38)));
                          }

                          return ListView.separated(
                            itemCount: nodeVectors.length,
                            separatorBuilder: (context, index) => const Divider(color: Colors.white10),
                            itemBuilder: (context, index) {
                              final vector = nodeVectors[index];
                              final isOutflow = vector.sourceNodeId == node.id;
                              
                              return ListTile(
                                onTap: () => context.push('/vector/${vector.id}'),
                                leading: CircleAvatar(
                                  backgroundColor: isOutflow ? Colors.redAccent.withOpacity(0.15) : Colors.greenAccent.withOpacity(0.15),
                                  child: Icon(
                                    isOutflow ? Icons.arrow_downward : Icons.arrow_upward,
                                    color: isOutflow ? Colors.redAccent : Colors.greenAccent,
                                  ),
                                ),
                                title: Text(
                                  isOutflow ? 'Salida hacia nodo destino' : 'Entrada desde nodo origen',
                                  style: const TextStyle(color: Colors.white, fontSize: 14),
                                ),
                                subtitle: Text(
                                  'Fecha: ${vector.effectiveAt.day}/${vector.effectiveAt.month}/${vector.effectiveAt.year}',
                                  style: const TextStyle(color: Colors.white30, fontSize: 12),
                                ),
                                trailing: Text(
                                  '${isOutflow ? "-" : "+"} S/. ${vector.amount.toStringAsFixed(2)}',
                                  style: TextStyle(
                                    color: isOutflow ? Colors.redAccent : Colors.greenAccent,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15,
                                  ),
                                ),
                              );
                            },
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
    ),
  );
}
}

// Convertidor Json manual para los cambios locales
String jsonEncode(Object? object) {
  return const JsonEncoder().convert(object);
}
