## 🧩 Arquitectura a nivel de servicios (MVP monolito modular)

```mermaid
graph TB
    subgraph "Cliente"
        Mobile[📱 App Móvil<br/>React Native / Flutter]
    end

    subgraph "Backend - Monolito Modular (1 Container App)"
        APIGateway[🚪 API Gateway interno<br/>Enrutamiento, autenticación JWT]
        
        AuthService[🔐 Auth Service<br/>Registro, OTP, PIN, JWT]
        AccountService[🔗 Account Service<br/>Vinculación y consulta<br/>de cuentas vía TAPP]
        PaymentService[💸 Payment Service<br/>Iniciación de pagos]
        FinanceService[📊 Finance Service<br/>Categorización, historial,<br/>presupuestos]
        
        Mediator[📨 Mediator / EventBus interno<br/>(MediatR - publicación en memoria)]
    end

    subgraph "Persistencia"
        SQL[(Azure SQL<br/>Usuarios, cuentas,<br/>presupuestos)]
        Cosmos[(Azure Cosmos DB<br/>Transacciones, eventos)]
    end

    subgraph "Externo (BCRP)"
        MockTAPP[🧪 Mock TAPP<br/>Sprint 01-02]
        RealTAPP[🏦 TAPP Real<br/>Futuro]
    end

    %% Conexiones
    Mobile -->|HTTPS + JWT| APIGateway
    APIGateway --> AuthService
    APIGateway --> AccountService
    APIGateway --> PaymentService
    APIGateway --> FinanceService

    AuthService --> SQL
    AccountService --> SQL
    AccountService -->|HTTPs| MockTAPP
    MockTAPP -.->|"reemplazo futuro"| RealTAPP

    PaymentService -->|HTTPs| MockTAPP
    PaymentService -->|"Publica evento"| Mediator
    FinanceService -->|"Escucha evento"| Mediator

    PaymentService --> Cosmos
    FinanceService --> Cosmos
    FinanceService --> SQL
```

---

## 🗂️ Responsabilidades de cada servicio (módulos)

### **1. Auth Service**
- Registro de usuario con número de teléfono.
- Generación y verificación de OTP (vía SMS).
- Creación y almacenamiento del hash del PIN (bcrypt).
- Emisión de tokens JWT para sesiones.
- Middleware de validación de JWT en cada petición.

### **2. Account Service**
- Orquestar la vinculación de cuentas con el flujo OAuth2/consentimiento de TAPP.
- Almacenar los tokens de acceso de TAPP (encriptados en Azure SQL).
- Consultar saldos de cuentas vinculadas a través de TAPP (y refrescar tokens).
- En Sprint 01, se conecta al Mock TAPP que devuelve datos ficticios.

### **3. Payment Service**
- Recibir solicitudes de pago desde el móvil.
- Validar los datos (monto, cuenta origen, destino).
- Enviar la orden de inicio de pago a TAPP (Mock TAPP en MVP).
- Al confirmarse, publicar internamente el evento `PaymentCompleted`.

### **4. Finance Service**
- Suscriptor del evento `PaymentCompleted` (vía MediatR interno).
- Almacenar la transacción en Cosmos DB con categoría automática.
- Exponer APIs de historial y presupuestos.
- Actualizar el progreso de presupuestos en Azure SQL.

### **5. API Gateway interno**
- Un simple middleware dentro de la misma aplicación que enruta las rutas (`/auth/*`, `/accounts/*`, `/payments/*`, `/transactions/*`, `/budgets/*`) a los controladores correspondientes.
- Aplica la validación del JWT.

---

## 🔄 Comunicación entre servicios

| Origen | Destino | Mecanismo |
|--------|---------|-----------|
| Móvil → Backend | API Gateway | HTTPS + JWT |
| API Gateway → Módulos | Llamadas directas a controladores | En memoria |
| Account Service → Mock TAPP | Cliente HTTP | HTTPS |
| Payment Service → Mock TAPP | Cliente HTTP | HTTPS |
| Payment Service → Finance Service | Evento `PaymentCompleted` | MediatR (publicación/en-memoria) |
| Todos los módulos → SQL o Cosmos | Repositorios compartidos | Conexión directa |

---

## 🧪 Evolución futura

- **MediatR → Azure Service Bus**: cuando necesites desacoplar completamente pagos y finanzas, podés cambiar la implementación del publicador sin tocar la lógica de negocio.
- **Módulos → Container Apps separados**: extraés cada módulo a su propio contenedor, con comunicación HTTP/Service Bus.
- **Mock TAPP → TAPP real**: solo cambia la URL y credenciales en Key Vault.

---

## ✅ Resumen visual

El gráfico muestra que tienes un **único backend con 4 servicios internos claramente separados**, dos bases de datos especializadas y una integración simulada con el BCRP. Esto te permite empezar a desarrollar ya, sin Redis ni sobrecarga de infraestructura, manteniendo un diseño limpio y listo para escalar.
