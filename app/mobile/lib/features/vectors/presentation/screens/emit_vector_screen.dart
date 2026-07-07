import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../providers/vectors_provider.dart';

class EmitVectorScreen extends ConsumerStatefulWidget {
  const EmitVectorScreen({super.key});

  @override
  ConsumerState<EmitVectorScreen> createState() => _EmitVectorScreenState();
}

class _EmitVectorScreenState extends ConsumerState<EmitVectorScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _rateController = TextEditingController(text: '1.000000');
  final _lineageController = TextEditingController();
  final _tagKeyController = TextEditingController();
  final _tagValController = TextEditingController();

  Node? _sourceNode;
  Node? _targetNode;
  DateTime _effectiveAt = DateTime.now();
  final Map<String, String> _tags = {};
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _amountController.dispose();
    _rateController.dispose();
    _lineageController.dispose();
    _tagKeyController.dispose();
    _tagValController.dispose();
    super.dispose();
  }

  void _addTag() {
    final key = _tagKeyController.text.trim();
    final val = _tagValController.text.trim();
    if (key.isNotEmpty && val.isNotEmpty) {
      setState(() {
        _tags[key] = val;
        _tagKeyController.clear();
        _tagValController.clear();
      });
    }
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_sourceNode == null || _targetNode == null) {
      setState(() => _errorMessage = 'Selecciona nodo origen y destino');
      return;
    }
    if (_sourceNode!.id == _targetNode!.id) {
      setState(() => _errorMessage = 'Nodo origen y destino deben diferir');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final amount = double.parse(_amountController.text.trim());
      final rate = double.parse(_rateController.text.trim());
      final lineage = _lineageController.text.trim().isEmpty ? null : _lineageController.text.trim();

      await ref.read(vectorsNotifierProvider.notifier).emitVector(
        sourceNodeId: _sourceNode!.id,
        targetNodeId: _targetNode!.id,
        amount: amount,
        exchangeRate: rate,
        lineageToken: lineage,
        tags: _tags,
        effectiveAt: _effectiveAt,
      );

      if (mounted) {
        setState(() => _isLoading = false);
        context.go('/');
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final nodesAsync = ref.watch(nodesNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F2027),
        elevation: 0,
        title: const Text('Emitir Vector', style: TextStyle(color: Colors.white)),
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
              final activeNodes = nodes.where((n) => n.isActive).toList();

              return SingleChildScrollView(
                padding: const EdgeInsets.all(20.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Nueva Transferencia Contable',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Registra un flujo de fondos de un nodo origen (salida) a un destino (entrada).',
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                      const SizedBox(height: 24),
                      // Nodo origen
                      DropdownButtonFormField<Node>(
                        dropdownColor: const Color(0xFF162A30),
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Nodo Origen',
                          labelStyle: const TextStyle(color: Colors.white70),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.white30)),
                        ),
                        items: activeNodes.map((n) {
                          return DropdownMenuItem<Node>(value: n, child: Text('${n.name} (${n.currency})'));
                        }).toList(),
                        onChanged: (value) => setState(() => _sourceNode = value),
                      ),
                      const SizedBox(height: 16),
                      // Nodo destino
                      DropdownButtonFormField<Node>(
                        dropdownColor: const Color(0xFF162A30),
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Nodo Destino',
                          labelStyle: const TextStyle(color: Colors.white70),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.white30)),
                        ),
                        items: activeNodes.map((n) {
                          return DropdownMenuItem<Node>(value: n, child: Text('${n.name} (${n.currency})'));
                        }).toList(),
                        onChanged: (value) => setState(() => _targetNode = value),
                      ),
                      const SizedBox(height: 16),
                      // Monto
                      TextFormField(
                        controller: _amountController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Monto',
                          labelStyle: const TextStyle(color: Colors.white70),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.white30)),
                          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF00FFCC))),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) return 'Ingresa el monto';
                          final val = double.tryParse(value.trim());
                          if (val == null || val <= 0) return 'El monto debe ser positivo y mayor a 0';
                          return null;
                        },
                      ),
                      // Tipo de cambio (visible si monedas difieren)
                      if (_sourceNode != null && _targetNode != null && _sourceNode!.currency != _targetNode!.currency) ...[
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _rateController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          style: const TextStyle(color: Colors.white),
                          decoration: InputDecoration(
                            labelText: 'Tipo de Cambio (1 ${_sourceNode!.currency} = ? ${_targetNode!.currency})',
                            labelStyle: const TextStyle(color: Colors.white70),
                            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.white30)),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) return 'Ingresa el tipo de cambio';
                            final val = double.tryParse(value.trim());
                            if (val == null || val <= 0) return 'Debe ser un valor positivo';
                            return null;
                          },
                        ),
                      ],
                      const SizedBox(height: 16),
                      // Fecha Efectiva
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Fecha Efectiva:', style: TextStyle(color: Colors.white70)),
                          TextButton.icon(
                            icon: const Icon(Icons.date_range, color: Color(0xFF00FFCC)),
                            label: Text(
                              '${_effectiveAt.day}/${_effectiveAt.month}/${_effectiveAt.year} ${_effectiveAt.hour}:${_effectiveAt.minute}',
                              style: const TextStyle(color: Color(0xFF00FFCC)),
                            ),
                            onPressed: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: _effectiveAt,
                                firstDate: DateTime(2025),
                                lastDate: DateTime(2027),
                              );
                              if (date != null) {
                                final time = await showTimePicker(
                                  context: context,
                                  initialTime: TimeOfDay.fromDateTime(_effectiveAt),
                                );
                                if (time != null) {
                                  setState(() {
                                    _effectiveAt = DateTime(date.year, date.month, date.day, time.hour, time.minute);
                                  });
                                }
                              }
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Lineage Token
                      TextFormField(
                        controller: _lineageController,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Lineage Token (Opcional - Netting/Split)',
                          labelStyle: const TextStyle(color: Colors.white70),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.white30)),
                        ),
                      ),
                      const SizedBox(height: 20),
                      // Tags dinámicos
                      const Text('Etiquetas contextuales (Tags)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _tagKeyController,
                              style: const TextStyle(color: Colors.white),
                              decoration: const InputDecoration(labelText: 'Clave', labelStyle: TextStyle(color: Colors.white70)),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextField(
                              controller: _tagValController,
                              style: const TextStyle(color: Colors.white),
                              decoration: const InputDecoration(labelText: 'Valor', labelStyle: TextStyle(color: Colors.white70)),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.add_box, color: Color(0xFF00FFCC), size: 30),
                            onPressed: _addTag,
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        children: _tags.entries.map((e) {
                          return Chip(
                            backgroundColor: Colors.white.withOpacity(0.08),
                            label: Text('${e.key}: ${e.value}', style: const TextStyle(color: Colors.white)),
                            onDeleted: () {
                              setState(() => _tags.remove(e.key));
                            },
                          );
                        }).toList(),
                      ),
                      if (_errorMessage != null) ...[
                        const SizedBox(height: 24),
                        Text(
                          _errorMessage!,
                          style: const TextStyle(color: Colors.redAccent, fontSize: 14),
                          textAlign: TextAlign.center,
                        ),
                      ],
                      const SizedBox(height: 32),
                      ElevatedButton(
                        onPressed: _isLoading ? null : _submit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF00FFCC),
                          foregroundColor: const Color(0xFF0F2027),
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2, valueColor: AlwaysStoppedAnimation(Color(0xFF0F2027))),
                              )
                            : const Text('Emitir Vector', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
