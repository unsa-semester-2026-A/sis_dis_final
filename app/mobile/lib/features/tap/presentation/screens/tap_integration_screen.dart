import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/tap_provider.dart';
import '../../../accounts/domain/entities/node.dart';
import '../../../accounts/presentation/providers/nodes_provider.dart';
import '../../../vectors/presentation/providers/vectors_provider.dart';

class TapIntegrationScreen extends ConsumerStatefulWidget {
  const TapIntegrationScreen({super.key});

  @override
  ConsumerState<TapIntegrationScreen> createState() => _TapIntegrationScreenState();
}

class _TapIntegrationScreenState extends ConsumerState<TapIntegrationScreen> {
  final _tappIdController = TextEditingController();
  final _amountController = TextEditingController();
  final _remarksController = TextEditingController();
  final _validateController = TextEditingController();
  final _statusController = TextEditingController();

  String? _selectedBank = 'BCP';
  bool _isLoading = false;
  String? _message;
  String? _validatedPayeeName;

  @override
  void dispose() {
    _tappIdController.dispose();
    _amountController.dispose();
    _remarksController.dispose();
    _validateController.dispose();
    _statusController.dispose();
    super.dispose();
  }

  void _vincular() async {
    final tappId = _tappIdController.text.trim();
    if (tappId.isEmpty) return;

    setState(() => _isLoading = true);
    await ref.read(tapNotifierProvider.notifier).createConsent(_selectedBank!, tappId);
    
    // Auto-crear nodo ASSET real en el wallet-service contable
    try {
      await ref.read(nodesNotifierProvider.notifier).createNode(
        'TAP $_selectedBank ($tappId)',
        NodeType.asset,
        'PEN',
      );
    } catch (_) {}

    if (mounted) {
      setState(() {
        _isLoading = false;
        _message = 'Consentimiento autorizado. Cuenta bancaria vinculada.';
        _tappIdController.clear();
      });
    }
  }

  void _validate() async {
    final alias = _validateController.text.trim();
    if (alias.isEmpty) return;

    setState(() {
      _isLoading = true;
      _validatedPayeeName = null;
      _message = null;
    });

    try {
      final res = await ref.read(tapNotifierProvider.notifier).validateAlias(alias);
      if (mounted) {
        setState(() {
          _isLoading = false;
          _validatedPayeeName = res['name'] as String;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _message = 'Error: ${e.toString().replaceAll('Exception: ', '')}';
      });
    }
  }

  void _iniciarPago() async {
    final amount = double.tryParse(_amountController.text.trim()) ?? 0.0;
    final payee = _validateController.text.trim();
    if (amount <= 0 || payee.isEmpty) return;

    setState(() {
      _isLoading = true;
      _message = null;
    });

    await ref.read(tapNotifierProvider.notifier).initiatePayment(
      sourceTappId: 'rafael@tapp',
      destinationTappId: payee,
      amount: amount,
      remarks: _remarksController.text.trim(),
    );

    if (mounted) {
      setState(() {
        _isLoading = false;
        _message = 'Fase 1 del 2PC iniciada. Transacción preparada en ledger distribuido TAP.';
      });
    }
  }

  void _confirmarPago() async {
    setState(() {
      _isLoading = true;
      _message = null;
    });

    try {
      final res = await ref.read(tapNotifierProvider.notifier).confirmPayment();
      
      // Auto-registrar vector real en wallet-service para registrar el movimiento contable
      try {
        final nodes = ref.read(nodesNotifierProvider).valueOrNull ?? [];
        final assetNode = nodes.firstWhere((n) => n.name.contains('TAP BCP'), orElse: () => nodes.firstWhere((n) => n.nodeType == NodeType.asset));
        final sinkNode = nodes.firstWhere((n) => n.nodeType == NodeType.sink);

        await ref.read(vectorsNotifierProvider.notifier).emitVector(
          sourceNodeId: assetNode.id,
          targetNodeId: sinkNode.id,
          amount: res['amount'] as double,
          transactionId: res['transId'] as String,
          tags: {'tap_confirm': 'true', 'conf_id': res['confId'] as String},
        );
      } catch (_) {}

      if (mounted) {
        setState(() {
          _isLoading = false;
          _message = 'Fase 2 (2PC) Exitosa. Código Confirmación: ${res['confId']}\nRRN BCRP: ${res['transRRN']}';
          _amountController.clear();
          _remarksController.clear();
          _validateController.clear();
          _validatedPayeeName = null;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _message = 'Error en confirmación: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final tapState = ref.watch(tapNotifierProvider);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (Navigator.of(context).canPop()) {
          context.pop();
        } else {
          context.go('/profile');
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F2027),
          elevation: 0,
          title: const Text('Integración TAP (BCRP)', style: TextStyle(color: Colors.white)),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () {
              if (Navigator.of(context).canPop()) {
                context.pop();
              } else {
                context.go('/profile');
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
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_message != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: Colors.white.withOpacity(0.08), borderRadius: BorderRadius.circular(10)),
                    child: Text(_message!, style: const TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold, fontSize: 13)),
                  ),
                  const SizedBox(height: 16),
                ],

                // Sección A: Vincular cuenta bancaria real
                const Text('Sección A: Vincular cuenta real (Consentimiento)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(color: Colors.white.withOpacity(0.04), borderRadius: BorderRadius.circular(14)),
                  child: Column(
                    children: [
                      DropdownButtonFormField<String>(
                        value: _selectedBank,
                        dropdownColor: const Color(0xFF162A30),
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(labelText: 'Banco', labelStyle: TextStyle(color: Colors.white70)),
                        items: ['BCP', 'BBVA', 'Interbank', 'Scotiabank'].map((b) {
                          return DropdownMenuItem<String>(value: b, child: Text(b));
                        }).toList(),
                        onChanged: (val) => setState(() => _selectedBank = val),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _tappIdController,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          labelText: 'Tu TAPP ID (ej: rafael@tapp)',
                          labelStyle: TextStyle(color: Colors.white70),
                        ),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _isLoading ? null : _vincular,
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF00FFCC), foregroundColor: const Color(0xFF0F2027)),
                        child: const Text('Autorizar Consentimiento TAP'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Sección B: Cuentas vinculadas
                const Text('Sección B: Cuentas Reales Vinculadas', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 12),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: tapState.linkedAccounts.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final acc = tapState.linkedAccounts[index];
                    return ListTile(
                      tileColor: Colors.white.withOpacity(0.04),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      title: Text('${acc['bank']} — ${acc['tappId']}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      trailing: Text('${acc['currency']} ${acc['balance']}', style: const TextStyle(color: Color(0xFF00FFCC))),
                    );
                  },
                ),
                const SizedBox(height: 24),

                // Sección C: Transferencia TAP
                const Text('Sección C: Transferencia Interbancaria (2PC)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(color: Colors.white.withOpacity(0.04), borderRadius: BorderRadius.circular(14)),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _validateController,
                              style: const TextStyle(color: Colors.white),
                              decoration: const InputDecoration(labelText: 'TAPP ID Destinatario', labelStyle: TextStyle(color: Colors.white70)),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.check_circle_outline, color: Color(0xFF00FFCC)),
                            onPressed: _validate,
                          ),
                        ],
                      ),
                      if (_validatedPayeeName != null) ...[
                        const SizedBox(height: 8),
                        Text('Titular validado: $_validatedPayeeName', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _amountController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(labelText: 'Monto a Transferir'),
                        ),
                        TextField(
                          controller: _remarksController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(labelText: 'Concepto / Glosa'),
                        ),
                        const SizedBox(height: 16),
                        if (tapState.pendingPayment == null)
                          ElevatedButton(
                            onPressed: _isLoading ? null : _iniciarPago,
                            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF00FFCC), foregroundColor: const Color(0xFF0F2027)),
                            child: const Text('Iniciar Transferencia (Fase 1 2PC)'),
                          ),
                      ],
                      if (tapState.pendingPayment != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(color: Colors.amber.withOpacity(0.1), border: Border.all(color: Colors.amber)),
                          child: Column(
                            children: [
                              Text('Pago Preparado: ${tapState.pendingPayment!['transId']}', style: const TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                              const SizedBox(height: 8),
                              const Text('Falta la confirmación de la fase 2 para liberar fondos de forma segura y atómica.', style: TextStyle(color: Colors.white70, fontSize: 12), textAlign: TextAlign.center),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton(
                                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                                onPressed: _isLoading ? null : _confirmarPago,
                                child: const Text('Confirmar 2PC'),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: OutlinedButton(
                                style: OutlinedButton.styleFrom(foregroundColor: Colors.white54),
                                onPressed: () {
                                  ref.read(tapNotifierProvider.notifier).cancelPayment();
                                  setState(() => _message = 'Transacción cancelada de forma segura.');
                                },
                                child: const Text('Abortar'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}
}
