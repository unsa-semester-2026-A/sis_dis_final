import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'tap_provider.g.dart';

class TapState {
  TapState({
    required this.linkedAccounts,
    required this.consents,
    this.pendingPayment,
  });

  final List<Map<String, dynamic>> linkedAccounts;
  final List<Map<String, dynamic>> consents;
  final Map<String, dynamic>? pendingPayment;

  TapState copyWith({
    List<Map<String, dynamic>>? linkedAccounts,
    List<Map<String, dynamic>>? consents,
    Map<String, dynamic>? pendingPayment,
    bool clearPendingPayment = false,
  }) {
    return TapState(
      linkedAccounts: linkedAccounts ?? this.linkedAccounts,
      consents: consents ?? this.consents,
      pendingPayment: clearPendingPayment ? null : (pendingPayment ?? this.pendingPayment),
    );
  }
}

@riverpod
class TapNotifier extends _$TapNotifier {
  @override
  TapState build() {
    return TapState(
      linkedAccounts: [
        {'bank': 'BCP', 'tappId': 'rafael@tapp', 'balance': '1250.00', 'currency': 'PEN'},
      ],
      consents: [
        {'consentId': 'CONS-uuid-123e4567-e89b-12d3-a456-426614174000', 'status': 'ACTIVE', 'tappId': 'rafael@tapp'},
      ],
    );
  }

  Future<void> createConsent(String bank, String tappId) async {
    state = state.copyWith(
      consents: [
        ...state.consents,
        {
          'consentId': 'CONS-uuid-${DateTime.now().millisecondsSinceEpoch}',
          'status': 'AWAITING_AUTHORISATION',
          'tappId': tappId,
          'bank': bank,
        }
      ],
    );

    // Simular autorización rápida del banco (OTP/Login en banco)
    await Future<void>.delayed(const Duration(seconds: 1));
    
    final list = List<Map<String, dynamic>>.from(state.consents);
    final idx = list.indexWhere((c) => c['tappId'] == tappId && c['status'] == 'AWAITING_AUTHORISATION');
    if (idx != -1) {
      list[idx] = {
        ...list[idx],
        'status': 'ACTIVE',
      };
      
      // Auto-vincular cuenta bancaria local como nodo ASSET también
      state = state.copyWith(
        consents: list,
        linkedAccounts: [
          ...state.linkedAccounts,
          {'bank': bank, 'tappId': tappId, 'balance': '500.00', 'currency': 'PEN'}
        ],
      );
    }
  }

  Future<Map<String, dynamic>> validateAlias(String payeeTappId) async {
    await Future<void>.delayed(const Duration(milliseconds: 600));
    if (payeeTappId.contains('@')) {
      final name = payeeTappId.split('@')[0].toUpperCase();
      return {
        'status': 'S',
        'name': '$name PEREZ LOPEZ',
        'tappId': payeeTappId,
      };
    }
    throw Exception('Formato de TAPP ID inválido (ejemplo: usuario@tapp)');
  }

  Future<void> initiatePayment({
    required String sourceTappId,
    required String destinationTappId,
    required double amount,
    required String remarks,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 800));
    
    final transId = 'TAPP-PAY-${DateTime.now().millisecondsSinceEpoch}';
    final payment = {
      'transId': transId,
      'sourceTappId': sourceTappId,
      'destinationTappId': destinationTappId,
      'amount': amount,
      'remarks': remarks,
      'status': 'INITIATED', // Fase 1 del 2PC
    };

    state = state.copyWith(pendingPayment: payment);
  }

  Future<Map<String, dynamic>> confirmPayment() async {
    final payment = state.pendingPayment;
    if (payment == null) {
      throw Exception('No hay ningún pago pendiente de confirmación');
    }

    await Future<void>.delayed(const Duration(seconds: 1));

    final transRRN = '${100000000000 + DateTime.now().millisecondsSinceEpoch % 100000000000}';
    final receipt = {
      'transId': payment['transId'],
      'transRRN': transRRN,
      'confId': 'CONF-${DateTime.now().millisecondsSinceEpoch}',
      'amount': payment['amount'],
      'status': 'SUCCESS', // Fase 2 del 2PC exitosa
    };

    state = state.copyWith(clearPendingPayment: true);
    return receipt;
  }

  void cancelPayment() {
    state = state.copyWith(clearPendingPayment: true);
  }
}
