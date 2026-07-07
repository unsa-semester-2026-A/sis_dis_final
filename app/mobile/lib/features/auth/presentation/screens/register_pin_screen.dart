import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';

/// Register PIN Setup Screen (S04)
class RegisterPinScreen extends ConsumerStatefulWidget {
  const RegisterPinScreen({super.key, required this.phoneNumber});

  final String phoneNumber;

  @override
  ConsumerState<RegisterPinScreen> createState() => _RegisterPinScreenState();
}

class _RegisterPinScreenState extends ConsumerState<RegisterPinScreen> {
  final _pinController = TextEditingController();
  final _confirmController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _pinController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final pin = _pinController.text.trim();
    final confirm = _confirmController.text.trim();

    if (pin != confirm) {
      setState(() => _errorMessage = 'Los PINes no coinciden');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    // Guardar credenciales de registro específicas en secure storage
    const storage = FlutterSecureStorage();
    final digits = widget.phoneNumber.replaceAll(RegExp(r'\D'), '');
    final padded = digits.padLeft(12, '0').substring(0, 12);
    final userId = '550e8400-e29b-41d4-a716-$padded';
    final name = 'Usuario ${widget.phoneNumber}';

    await storage.write(key: 'auth_pin_${widget.phoneNumber}', value: pin);
    await storage.write(key: 'auth_userid_${widget.phoneNumber}', value: userId);
    await storage.write(key: 'auth_name_${widget.phoneNumber}', value: name);

    // Iniciar sesión activa de forma inmediata para este usuario
    await storage.write(key: 'jwt_token', value: 'jwt_token_$userId');
    await storage.write(key: 'user_id', value: userId);
    await storage.write(key: 'user_phone', value: widget.phoneNumber);
    await storage.write(key: 'user_name', value: name);

    // Refrescar el estado de autenticación de Riverpod
    ref.invalidate(authNotifierProvider);

    await Future<void>.delayed(const Duration(milliseconds: 1000));

    if (mounted) {
      setState(() => _isLoading = false);
      context.go('/');
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        context.go('/register/phone');
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => context.go('/register/phone'),
          ),
        ),
      extendBodyBehindAppBar: true,
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
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                  const SizedBox(height: 16),
                  // Indicador de progreso
                  Row(
                    children: [
                      Expanded(child: Container(height: 4, color: const Color(0xFF00FFCC))),
                      const SizedBox(width: 8),
                      Expanded(child: Container(height: 4, color: const Color(0xFF00FFCC))),
                      const SizedBox(width: 8),
                      Expanded(child: Container(height: 4, color: const Color(0xFF00FFCC))),
                    ],
                  ),
                  const SizedBox(height: 32),
                  const Text(
                    'Registro: Paso 3 de 3',
                    style: TextStyle(color: Color(0xFF00FFCC), fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Crea tu PIN de acceso',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Define un PIN numérico de seguridad para autorizar tus transacciones y logins futuros.',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const SizedBox(height: 36),
                  TextFormField(
                    controller: _pinController,
                    keyboardType: TextInputType.number,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white, letterSpacing: 8),
                    textAlign: TextAlign.center,
                    maxLength: 6,
                    decoration: InputDecoration(
                      labelText: 'Nuevo PIN (4 a 6 dígitos)',
                      labelStyle: const TextStyle(color: Colors.white70, letterSpacing: 0),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF00FFCC)),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Ingresa tu PIN';
                      }
                      if (value.length < 4) {
                        return 'El PIN debe tener al menos 4 dígitos';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 20),
                  TextFormField(
                    controller: _confirmController,
                    keyboardType: TextInputType.number,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white, letterSpacing: 8),
                    textAlign: TextAlign.center,
                    maxLength: 6,
                    decoration: InputDecoration(
                      labelText: 'Confirmar PIN',
                      labelStyle: const TextStyle(color: Colors.white70, letterSpacing: 0),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF00FFCC)),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Confirma tu PIN';
                      }
                      return null;
                    },
                  ),
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      _errorMessage!,
                      style: const TextStyle(color: Colors.redAccent, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ],
                  const SizedBox(height: 48),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00FFCC),
                      foregroundColor: const Color(0xFF0F2027),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(Color(0xFF0F2027)),
                            ),
                          )
                        : const Text(
                            'Finalizar Registro',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    ),
   ),
  );
}
}
