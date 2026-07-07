/// Environment configuration for Spondylus API clients.
class EnvironmentConfig {
  /// Toggle this to switch between local backend and Azure Container Apps.
  /// Set to [true] to target docker-compose local microservices.
  /// Set to [false] to target the deployed Azure endpoints.
  static const bool useLocalBackend = false;

  /// Deployed Azure Container Apps base URLs.
  static const String walletAzureUrl = 'https://wallet-app.purplebush-0b07dd2d.eastus2.azurecontainerapps.io';
  static const String authAzureUrl = 'https://auth-app.purplebush-0b07dd2d.eastus2.azurecontainerapps.io';

  /// Development host.
  /// Use 'localhost' or '10.0.2.2' for simulator testing.
  /// Replace this with your computer's local IP (e.g. '192.168.1.15') if running on a physical Android/iOS phone.
  static const String devHost = '192.168.0.20';

  /// Evaluated wallet service URL based on environment target.
  static String get walletUrl => useLocalBackend
      ? 'http://$devHost:8002'
      : walletAzureUrl;

  /// Evaluated authentication service URL based on environment target.
  static String get authUrl => useLocalBackend
      ? 'http://$devHost:8001'
      : authAzureUrl;
}
