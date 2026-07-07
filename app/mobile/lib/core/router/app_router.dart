import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/register_phone_screen.dart';
import '../../features/auth/presentation/screens/register_otp_screen.dart';
import '../../features/auth/presentation/screens/register_pin_screen.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';

import '../../features/accounts/presentation/screens/dashboard_screen.dart';
import '../../features/accounts/presentation/screens/node_detail_screen.dart';
import '../../features/accounts/presentation/screens/node_management_screen.dart';
import '../../features/accounts/presentation/screens/create_node_screen.dart';

import '../../features/vectors/presentation/screens/emit_vector_screen.dart';
import '../../features/vectors/presentation/screens/vector_history_screen.dart';
import '../../features/vectors/presentation/screens/vector_detail_screen.dart';

import '../../features/budgets/presentation/screens/budget_screen.dart';
import '../../features/reports/presentation/screens/reports_screen.dart';
import '../../features/tap/presentation/screens/tap_integration_screen.dart';
import '../../features/settings/presentation/screens/profile_screen.dart';

part 'app_router.g.dart';

/// Configured GoRouter provider for navigation flow control.
@riverpod
GoRouter appRouter(AppRouterRef ref) {
  final authState = ref.watch(authNotifierProvider);
  final isLoggedIn = authState.valueOrNull != null;

  return GoRouter(
    initialLocation: isLoggedIn ? '/' : '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/register/phone',
        builder: (context, state) => const RegisterPhoneScreen(),
      ),
      GoRoute(
        path: '/register/otp',
        builder: (context, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return RegisterOtpScreen(phoneNumber: phone);
        },
      ),
      GoRoute(
        path: '/register/pin',
        builder: (context, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return RegisterPinScreen(phoneNumber: phone);
        },
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/node/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return NodeDetailScreen(nodeId: id);
        },
      ),
      GoRoute(
        path: '/nodes',
        builder: (context, state) => const NodeManagementScreen(),
      ),
      GoRoute(
        path: '/nodes/create',
        builder: (context, state) => const CreateNodeScreen(),
      ),
      GoRoute(
        path: '/vectors/emit',
        builder: (context, state) => const EmitVectorScreen(),
      ),
      GoRoute(
        path: '/vectors/history',
        builder: (context, state) => const VectorHistoryScreen(),
      ),
      GoRoute(
        path: '/vector/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return VectorDetailScreen(vectorId: id);
        },
      ),
      GoRoute(
        path: '/budgets',
        builder: (context, state) => const BudgetScreen(),
      ),
      GoRoute(
        path: '/reports',
        builder: (context, state) => const ReportsScreen(),
      ),
      GoRoute(
        path: '/tap',
        builder: (context, state) => const TapIntegrationScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
    ],
  );
}
