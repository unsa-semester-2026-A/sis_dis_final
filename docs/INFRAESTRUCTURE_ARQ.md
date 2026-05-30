## 🧩 Visión general del sistema (MVP escalable)

El presente documento muestra la organizacion sobre infraestructura del proyecto
Esta aplicacion es un **agregador de finanzas personales** que, mediante la infraestructura TAPP del BCRP, permite a los usuarios pagar desde cualquiera de sus cuentas (bancos, billeteras como Yape/Plin) y organizar sus gastos en un solo lugar.

**Clave:** el usuario **nunca** comparte sus credenciales bancarias con tu app. La autenticación financiera la maneja el BCRP; tu app solo autentica el acceso a la propia plataforma con un PIN.

---

## 🔐 1. Capa de autenticación (doble capa)

| Capa | ¿Quién la maneja? | ¿Qué método usa? |
|------|-------------------|------------------|
| **Acceso a la app** | Tu backend (`AuthService`) | Número de teléfono + PIN de 4-6 dígitos. Verificación de OTP al registrarse. |
| **Vinculación de cuentas / pagos** | Plataforma TAPP del BCRP | Flujos estándar de TAPP (probablemente OAuth2 + consentimiento). Tu app redirige al usuario al entorno seguro de TAPP. |

**Flujo completo**:

1. **Registro/Login en tu app**:
   - Usuario ingresa número de celular.
   - Recibe OTP por SMS (Azure Communication Services o similar).
   - Define un PIN (hash bcrypt almacenado en Azure SQL).
   - El backend emite un JWT firmado (clave en Key Vault).
2. **Uso diario**:
   - El usuario abre la app e ingresa el PIN (o usa biometría local para desbloquear un token almacenado de forma segura).
   - El backend valida el JWT en cada petición.
3. **Al agregar una cuenta bancaria**:
   - Tu frontend llama a `POST /accounts/link` (necesita JWT).
   - El backend redirige al usuario a la URL de autorización de TAPP.
   - TAPP se encarga de autenticar al usuario en su banco/billetera y pide consentimiento para compartir datos o iniciar pagos.
   - TAPP devuelve un token de acceso que tu backend almacena (encriptado) para futuras consultas.

---

## 🧱 2. Monolito modular (estructura interna)

Para el MVP, todo el backend vive en **un solo proceso** desplegado como un Azure Container App. El código está organizado en módulos con límites claros, listos para extraerse como microservicios en el futuro.

```
/backend
  /src
    /Api                (Program.cs, controladores finos)
    /Modules
      /Auth             (registro, OTP, login, JWT)
      /AccountLink      (integración TAPP: vinculación, consulta saldos)
      /Payments         (iniciación de pagos vía TAPP)
      /Finance          (categorización, historial, presupuestos)
    /Infrastructure     (DbContext SQL, CosmosClient, Redis, TAPIClient)
```

Comunicación entre módulos: **llamadas directas a servicios en memoria** (vía DI). Para el flujo de pago → organización financiera, se puede usar un patrón de publicación interna (por ejemplo, MediatR) que, en el futuro, se reemplazará por Azure Service Bus.

---

## 📊 3. Base de datos y almacenamiento

| Base de datos | Uso |
|---------------|-----|
| **Azure SQL Database** | Datos relacionales: usuarios (hash PIN, teléfono), cuentas vinculadas (tokens cifrados), presupuestos, categorías por usuario. |
| **Azure Cosmos DB (SQL API)** | Transacciones (pagos realizados), eventos de historial, rápidos de consultar y escalar. |
| **Azure Cache for Redis** | Caché de saldos consultados (evita llamadas repetitivas a TAPP), sesiones temporales de pago. |
| **Azure Key Vault** | Secretos: clave de firma JWT, cadena de conexión a bases de datos, credenciales de TAPP. |

---

## 🌐 4. Integración con TAPP (BCRP)

Tu backend se comunica con TAPP a través de un cliente HTTP dedicado (`TappApiClient`), que maneja:
- Autenticación mutua (mTLS) y tokens de acceso.
- Descubrimiento de cuentas (`GET /accounts`).
- Vinculación (`POST /consent`).
- Iniciación de pagos (`POST /payments`).

**Mock para el Sprint 01**: un servicio falso que responde JSON predefinido, permitiendo desarrollar sin depender del BCRP.

---

## 📱 5. Capa móvil

- **React Native / Flutter**
- Librería de almacenamiento seguro para guardar el JWT (react-native-keychain, flutter_secure_storage).
- Pantallas: Login (teléfono, PIN, OTP), Home (cuentas vinculadas), Pagos (QR, monto), Historial, Presupuestos.
- Integración con cámara para leer códigos QR TAPP en el futuro.

---

## 🏗️ 6. Infraestructura en Azure

**Entorno MVP (Azure Container Apps)**:
- **Container App Environment**: aloja el monolito (1 contenedor).
- **Container Registry** (ACR): imágenes Docker.
- **CI/CD con GitHub Actions**: build, test, push al ACR, deploy al Container App.

**Recursos PaaS**:
- Azure SQL Database (plan serverless en desarrollo).
- Azure Cosmos DB (modo de capacidad aprovisionada baja).
- Azure Cache for Redis (plan básico).
- Azure Key Vault (estándar).
- Application Insights (monitoreo unificado).

La seguridad entre servicios se maneja con **Managed Identities** y reglas de firewall interno.

---

## 🖼️ Diagrama de arquitectura (versión actualizada)

```mermaid
graph TB
    User(("👤 Usuario"))
    Mobile[📱 App Móvil]
    
    subgraph "Azure (MVP)"
        APIM[API Management<br/>Punto único de entrada]
        Backend[🧩 Monolito Modular<br/>Container App<br/>Auth, AccountLink, Payments, Finance]
        SQL[(Azure SQL<br/>Usuarios, cuentas,<br/>presupuestos)]
        Cosmos[(Cosmos DB<br/>Transacciones,<br/>historial)]
        Redis[(Redis<br/>Caché saldos)]
        KV[Key Vault<br/>Secretos]
        Insights[Application Insights]
        
        MockTAPP[Mock TAPP<br/>(Sprint 01)]
    end
    
    subgraph "Plataforma BCRP (futuro)"
        TAPP[🏦 TAPP real]
        Banks[🏧 Bancos / Billeteras]
    end
    
    User -->|PIN / Huella| Mobile
    Mobile -->|HTTPS + JWT| APIM
    APIM --> Backend
    
    Backend --> SQL
    Backend --> Cosmos
    Backend --> Redis
    Backend --> KV
    
    Backend -->|Link / Pagos| MockTAPP
    MockTAPP -.->|futuro| TAPP
    
    TAPP --> Banks
    
    Backend -.-> Insights
```

---

## 🚀 Camino de evolución futura

1. **MVP (1 mes)**: monolito modular en 1 Container App. Mock TAPP.
2. **Post-MVP**: se extrae `FinanceOrganizer` como Azure Function independiente, suscrita a un Service Bus donde `Payments` publica eventos.
3. **Escalamiento**: se migran los módulos críticos a Container Apps separados o AKS, cada uno con su propia base de datos.
4. **Seguridad avanzada**: se integra biometría local como método de desbloqueo del token JWT almacenado.

---

## ✅ Resumen final

- **Autenticación propia** (teléfono + PIN + JWT) dentro del monolito; **BCRP maneja lo bancario**.
- **Monolito modular** (1 solo contenedor) en Azure Container Apps.
- **Dos bases de datos**: SQL para usuarios/presupuestos, Cosmos DB para transacciones.
- **Mock TAPP** para empezar a desarrollar ya, sin esperar al BCRP.
- **Listo para escalar** a microservicios reales cuando la validación lo justifique.
