### **TAPP bcrp**

Presentacion de la 4ta fase: [https://www.bcrp.gob.pe/tapp/iniciacion-de-pagos.html](https://www.bcrp.gob.pe/tapp/iniciacion-de-pagos.html)

### **Estado Actual (Junio 2026\)**

* **No hay APIs públicas, contratos de datos (JSON/XML), documentación técnica detallada, sandbox ni especificaciones para desarrolladores disponibles públicamente.** El proyecto está en fase de implementación/piloto (iniciado alrededor de 2024-2025 con colaboración de NPCI de India). El lanzamiento operativo completo se prevé para **fines de 2026**.

**Modelo centralizado de Iniciación de Pagos (Open Payments):**

* **Roles especializados** (promueve competencia y especialización):  
  * **Proveedor de Cuentas (PC)**: Bancos, cajas, EEDEs (mantienen fondos y autentican).  
  * **Proveedor de Acceso (PAC)**: Enrutan pagos (bancos, adquirentes, telcos).  
  * **Proveedor de Aplicaciones / Iniciador de Pagos (PSIP/TPAP)**: Fintechs, bigtechs, telcos, billeteras (interfaz con usuario; **no custodian fondos**).

**Flujo típico** (basado en descripciones oficiales y modelo UPI):

1. Usuario en app de iniciador (ej. fintech) selecciona cuenta (de otro banco), autoriza (consentimiento expreso \+ autenticación fuerte, probablemente con redirección o decoupled auth al banco/PC).  
2. Iniciador envía orden a TAPP (plataforma central).  
3. TAPP enruta a PC (proveedor de cuenta) vía CCE (Cámara de Compensación Electrónica) o riel propio para ejecución en tiempo real (\<10 seg, 24/7).  
4. Confirmación a todos.

**Estado de las Interfaces y Contratos (Avances al Primer Trimestre del 2025):**

Segun declaraciones del BCRP en su documento “Principales Avances al Primer Semestre del 2025 ” (Página 22, 23, 24): [https://www.bcrp.gob.pe/docs/Sistema-Pagos/articulos/estrategia-de-interoperabilidad-2025-1.pdf](https://www.bcrp.gob.pe/docs/Sistema-Pagos/articulos/estrategia-de-interoperabilidad-2025-1.pdf)

a) Definición de iniciación de pagos (Mayo 2024\) 

* Se deben definir **estándares de APIs, las cuales deben operar en un esquema 24/7 y estar disponibles al 99,9 por ciento.**

d) Ciberseguridad y fraude (Noviembre 2024\) 

* El uso de estándares OAuth2, OpenID Connect y mTLS es recomendable para una implementación inicial ágil, antes de adoptar FAPI 2.0.

e) Monetización y estructura de costos (Enero 2025\) 

* Se discutieron tres modelos de monetización según el cobro que realizaría la entidad proveedora de cuentas al PSIP por consultas a las APIs: gratuitas, freemium (cobro a partir de cierto umbral) y pago por consumo. 

f) Gobernanza (Febrero 2025\) 

* **El modelo de gobernanza híbrida** se eligió como el más conveniente ya que equilibra la supervisión regulatoria con la flexibilidad del sector privado e innovación. • El BCRP debe establecer estándares técnicos y operativos obligatorios y debe disponibilizar espacios de prueba regulatorios (sandboxes). 

f) Estándares de APIs (Marzo 2025\)  
Se identificó la **operación centralizada con alta estandarización** como la opción más  
conveniente y se lograron consensos técnicos respecto a los **principales estándares** a  
implementar:

* **RESTful, mensajería JSON y documentación OAS3 como base técnica.**  
* **ISO 20022 como base semántica.**  
* **TLS y mTLS como capa de transporte.**  
* **JWT, JWS y JWE para contenido del mensaje.**  
* **OAuth 2.0 con Authorization Code \+ PKCE y OpenID para autenticación.**  
* **API de consentimiento, con registro por usuario, opción de limitarlo por periodo y capacidad auditable.**

### **Fuentes y Justificación de los Contratos del Mock**

Dado que **el BCRP aún no ha publicado especificaciones técnicas detalladas, contratos JSON ni sandbox público** (a junio 2026), los mocks de API se construyeron tomando como **principal referencia** el documento:

- **"Unified Payment Interface (UPI) \- Functional Specifications Document – Merchant Integration" (Version 3.0)** preparado por **HSBC India**. [https://develop.hsbc.com/sites/default/files/hsbc\_pdf/UPI%20Merchant%20API%20Specs\_2023.pdf](https://develop.hsbc.com/sites/default/files/hsbc_pdf/UPI%20Merchant%20API%20Specs_2023.pdf)

#### **¿Por qué es válida esta referencia?**

- TAPP es **explícitamente modelado sobre UPI de NPCI** (acuerdo de colaboración BCRP-NPCI desde 2024).  
- El documento de HSBC es una implementación real y detallada de los flujos UPI (validación de alias, Collect/Push, Post Credit, Status, Refund, etc.), lo que permite mapear directamente a la arquitectura de TAPP.  
- Se complementa con las declaraciones oficiales del BCRP sobre estándares técnicos (REST \+ JSON, ISO 20022, OAuth 2.0, mTLS, JWT, etc.).  
- Este enfoque es común en proyectos de pagos instantáneos: se usan implementaciones bancarias probadas mientras el regulador finaliza las especificaciones locales.

**Nota:** Cuando el BCRP publique sus especificaciones oficiales (esperado con el reglamento de Iniciadores de Pagos y el piloto), los mocks deberán ajustarse. Actualmente representan la mejor aproximación disponible.

## **Endpoints Principales**

### **Endpoint 1: POST /auth/oauth/token**

**(OAuth 2.0 \- Client Credentials para Iniciador PSIP)**

**Descripción**: Endpoint de autenticación principal para que los Proveedores de Servicios de Iniciación de Pagos (PSIP) obtengan un `access_token`. Utiliza el flujo **Client Credentials** (recomendado por BCRP para comunicación máquina a máquina). Es el primer paso obligatorio antes de cualquier operación en la API de TAPP.

**Request JSON Completo**

```json
{
  "grant_type": "client_credentials",
  "client_id": "psip-app-001-123456",
  "client_secret": "sk_live_8f3k9x2m7p4q9w2e5r7t8y9u0i",
  "scope": "payments:transfer payments:collect accounts:info consents:manage",
  "idempotencyKey": "auth-20260607123456789"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| grant\_type | String | Sí | Tipo de flujo de concesión OAuth 2.0. Debe ser exactamente "client\_credentials". | Estándar OAuth 2.0 declarado por el BCRP para autenticación servidor a servidor |
| client\_id | String | Sí | Identificador único del PSIP registrado durante el onboarding. | Permite identificar y autenticar al participante autorizado |
| client\_secret | String | Sí | Clave secreta proporcionada por TAPP/BCRP durante el registro del PSIP. | Garantiza confidencialidad y seguridad alta (combinado con mTLS) |
| scope | String | Sí | Lista de permisos solicitados, separados por espacio. | Control granular de acceso y principio de mínima privilegio |
| idempotencyKey | String | Recomendado | Clave única para esta solicitud de token. | Evita duplicados y soporta la alta disponibilidad 24/7 exigida por BCRP |

**Response Exitosa**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwc2lwLWFwcC0wMDEiLCJzY29wZSI6InBheW1lbnRzOnRyYW5zZmVyIiwiaWF0IjoxNzQ5MDEyNDAwLCJleHAiOjE3NDkwMTYwMDB9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "payments:transfer payments:collect accounts:info consents:manage",
  "issued_at": "2026-06-07T15:30:00Z"
}
```

**Response de Error (ejemplo)**

```json
{
  "errorCode": "AUTH-001",
  "errorMessage": "Client authentication failed",
  "details": {
    "reason": "Invalid client_id or client_secret"
  }
}
```

---

### **Endpoint 2: POST /consents**

**(Consent Management \- Clave en modelo PISP)**

**Descripción**: Crea un consentimiento para que el usuario autorice a la app (PSIP) a iniciar pagos o consultar información en su cuenta del Proveedor de Cuentas (PC). Es el corazón del modelo de Iniciación de Pagos del BCRP y garantiza el consentimiento explícito y revocable.

**Request JSON Completo**

```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "tappId": "usuario@tapp",
  "debtorAccount": {
    "alias": "usuario123",
    "bankCode": "009"
  },
  "creditor": {
    "name": "Tienda XYZ",
    "alias": "tienda@merchant.tapp"
  },
  "amount": {
    "value": 100.50,
    "currency": "PEN"
  },
  "purpose": "CPTR",
  "validUntil": "2026-06-30T23:59:59Z",
  "scopes": ["accounts:balance", "accounts:transactions", "payments:transfer"],
  "idempotencyKey": "consent-20260607123456789",
  "transRemarks": "Autorización para agregación de cuentas y pagos"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| consentId | String (UUID) | Recomendado | Identificador único del consentimiento (puede generarlo el PSIP). | Permite trazabilidad, seguimiento y revocación posterior |
| tappId | String (255) | Sí | Tapp ID del usuario que otorgará el consentimiento. | Identificador principal del usuario en el ecosistema TAPP |
| debtorAccount | Object | Sí | Información de la cuenta del pagador (alias \+ código de banco/PC). | Localiza exactamente la cuenta donde se debitrá el dinero |
| creditor | Object | Condicional | Datos del beneficiario (nombre y alias). | Información necesaria para mostrar al usuario y procesar el pago |
| amount | Object | Condicional | Monto específico del consentimiento (útil para pagos únicos). | Control de límites y transparencia en el consentimiento |
| purpose | String (ISO 20022\) | Recomendado | Código de propósito del pago según estándar ISO 20022\. | Semántica estandarizada exigida por el BCRP |
| validUntil | ISO Datetime | Sí | Fecha y hora hasta la cual es válido el consentimiento. | Garantiza que el consentimiento sea temporal y revocable |
| scopes | Array de strings | Sí | Permisos solicitados (ej: iniciar pagos, consultar saldo). | Principio de mínima privilegio y consentimiento granular |
| idempotencyKey | String | Recomendado | Clave única para evitar crear el mismo consentimiento varias veces. | Alta disponibilidad 24/7 y prevención de duplicados |
| transRemarks | String | Opcional | Comentario que se mostrará al usuario durante la autorización. | Transparencia, consentimiento informado y antifraude |

**Response Exitosa**

```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "status": "AWAITING_AUTHORISATION",
  "authUrl": "https://pc-bank.example.com/authorize?consentId=CONS-uuid-...&redirect_uri=...",
  "createdAt": "2026-06-07T15:30:00Z",
  "expiresAt": "2026-06-30T23:59:59Z"
}
```

**Response de Error (ejemplo)**

```json
{
  "errorCode": "CONS-003",
  "errorMessage": "Invalid Tapp ID",
  "status": "RJCT"
}
```

---

### **Endpoint 3: POST /payments**

**(Payment Initiation \- Push Payment)**

**Descripción**: Este endpoint permite al usuario final iniciar un pago directo (Push) desde su cuenta hacia otro Tapp ID. Es uno de los flujos más importantes para una aplicación de finanzas personales, ya que permite transferencias proactivas entre usuarios o comercios de forma instantánea. Complementa el flujo Pull (`/collects`) y es esencial para funcionalidades como "Enviar dinero", "Pagar contactos" o "Transferencias rápidas".

**Request JSON Completo**

```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "sourceTappId": "usuario123@tapp",
  "destinationTappId": "amigo456@tapp",
  "amount": {
    "value": 85.50,
    "currency": "PEN"
  },
  "transRemarks": "Pago de almuerzo compartido",
  "transType": "PAY",
  "transRefId": "REF-20260607124567",
  "addInfo1": "Categoría: Comida",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "pay-push-20260607124567890"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| consentId | String (UUID) | Sí | Identificador del consentimiento válido del usuario que autoriza el pago. | Garantiza autorización explícita y auditable del usuario |
| sourceTappId | String (255) | Sí | Tapp ID de la cuenta origen (del usuario que envía el dinero). | Identifica claramente la cuenta de origen |
| destinationTappId | String (255) | Sí | Tapp ID del destinatario (persona o comercio que recibe el dinero). | Identificador principal del beneficiario en TAPP |
| amount | Object | Sí | Monto a transferir con valor y moneda (PEN). | Define el valor exacto de la transacción |
| transRemarks | String (1-50) | Sí | Descripción del pago que verán ambas partes. | Transparencia y contexto para el usuario y antifraude |
| transType | String | Sí | Tipo de transacción. Debe ser "PAY" para pagos Push. | Diferenciación clara entre flujos Push y Pull |
| transRefId | String (35) | Opcional | Referencia adicional (útil para QR o pagos específicos). | Soporte a diferentes canales de pago |
| addInfo1 a addInfo10 | String (0-50) | Opcional | Campos libres para información adicional (categoría, referencia interna, etc.). | Flexibilidad para funcionalidades de finanzas personales |
| idempotencyKey | String | Recomendado | Clave única para evitar pagos duplicados. | Seguridad y prevención de duplicados en entorno 24/7 |

**Response Exitosa**

```json
{
  "transId": "TAPP-PAY-9876543210ABCDEF12345",
  "transRRN": "701524566521",
  "transAmount": 85.50,
  "transAuthDateTime": "2026-06-07T12:45:22Z",
  "transStatus": "S",
  "transMessage": "Payment Successful",
  "sourceTappId": "usuario123@tapp",
  "destinationTappId": "amigo456@tapp",
  "respCode": "00",
  "addInfo1": "Categoría: Comida"
}
```

**Response de Error (ejemplo)**

```json
{
  "errorCode": "PAY-402",
  "errorMessage": "Insufficient balance or invalid consent",
  "details": {
    "reason": "Consent does not include payments:transfer scope"
  }
}
```

---

### **Endpoint 4: GET /accounts** o **POST /accounts**

**(Consulta de Saldos y Movimientos \- Account Information)**

**Descripción**: Este endpoint permite consultar el saldo actual y/o el historial de movimientos de una cuenta previamente autorizada mediante consentimiento. Es **uno de los endpoints más importantes** para una aplicación de finanzas personales, ya que habilita la **agregación de cuentas** de múltiples bancos en un solo lugar. Se basa en el consentimiento otorgado por el usuario y sigue el modelo de Account Information Service (AIS) inspirado en Open Banking y UPI.

**Recomendación**: Usar **POST /accounts** para mayor flexibilidad (filtros complejos) o **GET /accounts/{consentId}** para consultas simples.

**Request JSON Completo (POST /accounts)**

```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "tappId": "usuario123@tapp",
  "accountAlias": "usuario123",
  "bankCode": "009",
  "queryType": "balance",          // "balance" | "transactions" | "both"
  "transactionFrom": "2026-05-01T00:00:00Z",
  "transactionTo": "2026-06-07T23:59:59Z",
  "page": 1,
  "limit": 50,
  "idempotencyKey": "acct-20260607123456789"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| consentId | String (UUID) | Sí | Identificador del consentimiento previamente otorgado por el usuario. | Garantiza que solo se acceda con autorización explícita y auditable |
| tappId | String (255) | Sí | Tapp ID del usuario titular de la cuenta. | Identificador principal del usuario en TAPP |
| accountAlias | String (255) | Sí | Alias o Tapp ID específico de la cuenta a consultar. | Permite seleccionar una cuenta específica cuando el usuario tiene varias |
| bankCode | String | Sí | Código del banco / Proveedor de Cuentas (PC). | Localiza correctamente la cuenta en el ecosistema |
| queryType | String | Sí | Tipo de consulta: "balance", "transactions" o "both". | Flexibilidad según la necesidad de la app de finanzas personales |
| transactionFrom | ISO Datetime | Opcional | Fecha inicial para filtrar movimientos. | Permite historial acotado (importante para reportes financieros) |
| transactionTo | ISO Datetime | Opcional | Fecha final para filtrar movimientos. | Control de rango temporal |
| page | Integer | Opcional | Número de página para paginación de transacciones. | Manejo eficiente de grandes volúmenes de datos |
| limit | Integer | Opcional | Cantidad de registros por página (máx. recomendado 100). | Optimización de rendimiento |
| idempotencyKey | String | Recomendado | Clave única para la solicitud. | Prevención de duplicados en entorno 24/7 |

**Response Exitosa (Ejemplo con queryType: "both")**

```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "accountAlias": "usuario123",
  "bankCode": "009",
  "accountStatus": "ACTIVE",
  "balance": {
    "value": 2450.75,
    "currency": "PEN",
    "availableBalance": 2380.50
  },
  "lastUpdated": "2026-06-07T15:45:22Z",
  "transactions": [
    {
      "transId": "TAPP-TRAN-987654321",
      "transRRN": "701524566521",
      "amount": -150.00,
      "currency": "PEN",
      "transDate": "2026-06-06T10:23:15Z",
      "transType": "DEBIT",
      "description": "Pago en Tienda XYZ",
      "status": "S"
    }
  ],
  "page": 1,
  "totalPages": 5,
  "totalRecords": 234
}
```

**Response de Error (ejemplo)**

```json
{
  "errorCode": "ACCT-403",
  "errorMessage": "Consent expired or insufficient permissions",
  "status": "RJCT",
  "details": {
    "consentId": "CONS-uuid-...",
    "reason": "Consent does not include accounts:balance scope"
  }
}
```

---

### **Notas importantes**

- Este endpoint **depende completamente** del consentimiento otorgado en `/consents`. Debes validar los `scopes` antes de llamarlo.  
- Para una buena experiencia de usuario, combina este endpoint con `/aliases/validate` al momento de vincular una nueva cuenta.

---

### **Endpoint 5: POST /aliases/validate**

**(Validación de Tapp ID / Alias \- Adaptado de Dynamic VPA \+ VPA Status Validation)**

**Descripción**: Este endpoint permite validar si un Tapp ID (alias) existe, está activo y pertenece a una cuenta válida antes de iniciar un pago Push o Collect. Se utiliza para reducir transacciones fallidas y mejorar la experiencia del usuario. Equivalente a las validaciones Dynamic VPA y VPA Status de UPI.

**Request JSON Completo (Pre-Credit style)**

```json
{
  "refNo": "12837",
  "tappId": "dynamic-part123@tapp",
  "transRemarks": "Validación pre-pago de prueba",
  "transAmount": 100.00,
  "transId": "TAPP527498730B1B1BC3E053142433823107",
  "transRRN": "717215233641",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "source": "PSIP-APP",
  "pgMerchantId": "HSB000000000001",
  "addInfo1": "Referencia interna 456",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "val-20260607123456789"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| refNo | String (6-16) | Sí | Número de referencia único generado por el merchant para esta validación. Sirve para control de duplicidad. | Control de idempotencia y trazabilidad interna del merchant |
| tappId | String (255) | Sí | Tapp ID completo o parte dinámica del pagador (ej: usuario123@tapp). Es el identificador principal del usuario en el sistema TAPP. | Reemplaza el VPA de UPI. Es el identificador central en el modelo peruano |
| transRemarks | String (1-50) | Sí | Descripción o nota de la transacción que se mostrará al usuario o para registros internos. | Proporciona contexto para antifraude, auditoría y experiencia del usuario |
| transAmount | Decimal (2 places) | Condicional | Monto que se pretende validar/cobrar. Útil para validaciones pre-autorización. | Permite al banco/PC realizar chequeos de saldo o límites antes del pago real |
| transId | String (35) | Sí | Identificador único de transacción generado por el sistema central (TAPP/BCRP). | Trazabilidad a nivel nacional. Equivalente al NPCI Trxn ID en UPI |
| transRRN | String (12) | Sí | Retrieval Reference Number (número de referencia bancaria de 12 dígitos). | Estándar de mensajería financiera para rastreo entre instituciones |
| payeeTappId | String (255) | Sí | Tapp ID del beneficiario (merchant). | Identifica claramente quién recibirá el pago |
| source | String (5-50) | Sí | Origen de la solicitud (ej: "PSIP-APP", "WEB", "MOBILE"). | Auditoría, gobernanza y control de canales |
| pgMerchantId | String (16) | Sí | ID del merchant registrado en el sistema TAPP/HSBC equivalente. | Enlace con el registro/onboarding del participante |
| addInfo1 a addInfo10 | String (0-50) | No | Campos libres para información adicional específica del negocio o futura expansión. | Flexibilidad y futura-proof sin necesidad de cambiar el contrato |
| idempotencyKey | String | Recomendado | Clave única para garantizar que la solicitud se procese solo una vez. | Prevención de duplicados en un entorno 24/7 de alta disponibilidad |

**Response Exitosa**

```json
{
  "transStatus": "S",
  "transMessage": "Success",
  "refNo": "12837",
  "transRRN": "717215233641",
  "accountDetails": {
    "tappId": "dynamic-part123@tapp",
    "accountStatus": "Success",
    "name": "Juan Pérez López"
  },
  "pgMerchantId": "HSB000000000001",
  "addInfo1": "Referencia interna 456"
}
```

**Response de Error (ejemplo)**

```json
{
  "transStatus": "F",
  "transMessage": "Tapp ID no encontrado o inactivo",
  "refNo": "12837",
  "transRRN": "",
  "accountDetails": {},
  "errorCode": "ALIAS-404"
}
```

---

### **Endpoint 6: POST /collects**

**(Payment Initiation \- Collect Request / Pull)**

**Descripción**: El merchant o PSIP solicita un cobro (pull) al pagador a través de su Tapp ID. El usuario recibirá una notificación en su app bancaria para autorizar el pago. También se puede usar **POST /payments** para pagos Push (iniciados por el pagador).

**Request JSON Completo (Collect)**

```json
{
  "pgMerchantId": "HSB000000000001",
  "meOrderNo": "ORD-20260607123456",
  "payerTappId": "usuario123@tapp",
  "payerName": "Juan Pérez López",
  "transAmount": 50.00,
  "transRemarks": "Pago de producto electrónico",
  "expiryMinutes": 1110,
  "transType": "COLLECT",
  "addInfo1": "SKU-ABC123",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "collect-20260607123456789"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| pgMerchantId | String (16) | Sí | ID del merchant registrado en TAPP. | Identificación oficial del receptor del pago |
| meOrderNo | String (6-30) | Sí | Número de orden único generado por el merchant. | Unicidad por negocio y reconciliación interna |
| payerTappId | String (255) | Sí | Tapp ID del pagador (persona que debe autorizar y pagar). | Identificador principal del deudor |
| payerName | String (100) | Opcional | Nombre del pagador (obtenido previamente de validación). | Mejora experiencia y antifraude |
| transAmount | Decimal (2 places) | Sí | Monto exacto a cobrar (en PEN, dos decimales). | Monto del pago a autorizar |
| transRemarks | String (1-50) | Sí | Descripción del cobro que verá el usuario en su app bancaria. | Transparencia y consentimiento informado |
| expiryMinutes | Integer | Sí | Tiempo de validez del cobro en minutos (máximo recomendado 64800). | Define ventana de autorización del usuario |
| transType | String | Sí | Tipo de transacción ("COLLECT" para pull, "PAY" para push). | Diferencia clara entre flujos Push y Pull |
| addInfo1 a addInfo10 | String (0-50) | Opcional | Campos adicionales para datos del producto, referencia interna, etc. | Flexibilidad para el merchant |
| idempotencyKey | String | Recomendado | Clave única para evitar cobros duplicados. | Seguridad y consistencia en sistema 24/7 |

**Response Exitosa**

```json
{
  "meOrderNo": "ORD-20260607123456",
  "transId": "TAPP9DA3B8AC7A7454290D9D956D2C3D17E",
  "transRRN": "707520002012",
  "transAmount": 50.00,
  "transAuthDateTime": "2026-06-07T15:35:22Z",
  "collStatus": "I",
  "collStatusDesc": "Transaction Initiated",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "addInfo1": "SKU-ABC123"
}
```

**Response de Error (ejemplo)**

```json
{
  "meOrderNo": "ORD-20260607123456",
  "collStatus": "F",
  "collStatusDesc": "Invalid Payer Tapp ID",
  "errorCode": "COLL-001"
}
```

---

### **Endpoint 7: POST /payments/{transId}/confirm**

**(Post Credit / Final Response-Notification API \- Callback)**

**Descripción**: Este endpoint debe ser **implementado (hosted) por el merchant o PSIP**. TAPP (o el banco agregador) lo invoca después de procesar el crédito en la cuenta del beneficiario. El merchant responde con un `confId` para confirmar recepción y cerrar la transacción. Es clave para reconciliación y reporting.

**Request JSON Completo (enviado por TAPP al Merchant)**

```json
{
  "refNo": "2394829",
  "transId": "TAPP4521EDFDF113434131442134D34D34FF",
  "transRRN": "701245124574",
  "transAmount": 100.00,
  "transAuthDateTime": "2026-06-07T15:45:22Z",
  "respCode": "00",
  "transStatus": "S",
  "transMessage": "Success",
  "transType": "PAY",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "transRemarks": "Pago de producto electrónico",
  "transRefId": "1495085619883943",
  "addInfo4": "CREDIT",
  "pgMerchantId": "HSB000000000001",
  "orderId": "ORD-20260607123456"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| refNo | String (6-16) | Sí | Referencia serial generada por el sistema para control de duplicidad. | Trazabilidad y prevención de reprocesos |
| transId | String (35) | Sí | ID único de transacción a nivel central (TAPP/BCRP). | Identificador principal de la transacción |
| transRRN | String (12) | Sí | Retrieval Reference Number de 12 dígitos. | Estándar financiero para rastreo interbancario |
| transAmount | Decimal (2 places) | Sí | Monto acreditado. | Confirmación del valor exacto procesado |
| transAuthDateTime | String | Sí | Fecha y hora de aprobación (formato dd/mm/yyyy hh:mm:ss). | Auditoría temporal precisa |
| respCode | String (2-5) | Sí | Código de respuesta (00 \= éxito). | Estándar de códigos de respuesta |
| transStatus | String (1) | Sí | Estado de la transacción (S=Success, F=Failed). | Indicador claro del resultado final |
| transMessage | String (2-100) | Sí | Descripción legible del estado. | Información humana para logs y soporte |
| transType | String (3-10) | Sí | Tipo de transacción (PAY, COLLECT, etc.). | Diferenciación de flujos |
| payerTappId | String (255) | Sí | Tapp ID del pagador. | Identificación del origen del dinero |
| payeeTappId | String (255) | Sí | Tapp ID del beneficiario (merchant). | Identificación del receptor |
| transRemarks | String (1-50) | Opcional | Notas o descripción de la transacción. | Contexto adicional |
| transRefId | String (35) | Opcional | ID de referencia adicional (útil en QR Push). | Soporte a diferentes canales |
| addInfo4 | String | Condicional | Campo especial para indicar tipo de cuenta (ej: "CREDIT"). | Manejo de casos especiales (tarjetas) |
| pgMerchantId | String (16) | Sí | ID del merchant. | Enlace con registro del participante |
| orderId | String (6-50) | Opcional | ID de orden del merchant. | Reconciliación interna del negocio |

**Response del Merchant (confirmación)**

```json
{
  "refNo": "2394829",
  "transRRN": "701245124574",
  "confStatus": "S",
  "confMessage": "SUCCESS",
  "confId": "CONF-98765432109876543210",
  "pgMerchantId": "HSB000000000001",
  "addInfo1": ""
}
```

**Response de Error (ejemplo)**

```json
{
  "confStatus": "F",
  "confMessage": "Error en registro contable",
  "errorCode": "CONF-500"
}
```

---

### **Endpoint 8: POST /payments/status**

**(Transaction Status Enquiry)**

**Descripción**: Permite consultar el estado actual de una transacción. Soporta tanto `transRRN` como `meOrderNo` para mayor flexibilidad.

**Request JSON Completo**

```json
{
  "pgMerchantId": "HSB000000000001",
  "meRefNo": "41542145156",
  "transRRN": "701524566521",
  "meOrderNo": "ORD-20260607123456"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| pgMerchantId | String (16) | Sí | ID del merchant registrado. | Autenticación y segmentación del merchant |
| meRefNo | String (6-30) | Sí | Referencia única enviada por el merchant. | Identificador interno del merchant |
| transRRN | String (12) | Condicional | Retrieval Reference Number de la transacción. | Búsqueda por referencia bancaria central |
| meOrderNo | String (6-30) | Condicional | Número de orden del merchant. | Búsqueda por referencia del negocio |

**Response Exitosa**

```json
{
  "meOrderNo": "ORD-20260607123456",
  "transAmount": 100.00,
  "transAuthDateTime": "2026-06-07T15:45:22Z",
  "transStatus": "S",
  "transMessage": "Payment Successful",
  "respCode": "00",
  "transRRN": "701524566521",
  "transId": "TAPP89DA3B8AC7A7454290D9D956D2C3D17E",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "transApprNo": "451254",
  "addInfo1": "SKU-ABC123"
}
```

**Response de Error (ejemplo)**

```json
{
  "transStatus": "E",
  "transMessage": "Transaction not found",
  "errorCode": "STATUS-404"
}
```

---

### Headers Comunes (para todos los endpoints)

- `Authorization: Bearer <JWT-access-token>`  
- `X-Idempotency-Key: string` (obligatorio en operaciones mutantes)  
- `Content-Type: application/json`  
- `Accept: application/json`  
- `X-Tapp-Version: 1.0`

### Errores Estándar (ISO 20022 inspired)

```json
{
  "errorCode": "RJCT",
  "errorMessage": "Invalid Tapp ID or insufficient permissions",
  "details": {
    "field": "tappId",
    "reason": "Not registered"
  }
}
```

## **Endpoints Opcionales/Administrativos**

### **Endpoint 9: POST /refunds**

**(Refund API)**

**Descripción**: Permite realizar reembolsos sobre transacciones originales (principalmente Collects). Crea una nueva transacción de devolución.

**Request JSON Completo**

```json
{
  "pgMerchantId": "HSB000000000001",
  "newMeOrderNo": "REF-20260607130000",
  "orgTransId": "TAPP4521EDFDF113434131442134D34D34FF",
  "orgTransRRN": "701245124574",
  "transRemarks": "Reembolso por producto defectuoso",
  "refundAmount": 50.00,
  "orgMeOrderNo": "ORD-20260607123456",
  "addInfo1": "Motivo: DEV-001",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "refund-20260607130000123"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| pgMerchantId | String (16) | Sí | ID del merchant que solicita el reembolso. | Identificación del solicitante |
| newMeOrderNo | String (6-30) | Sí | Nuevo número de orden para esta devolución. | Unicidad de la transacción de refund |
| orgTransId | String (35) | Condicional | ID original de la transacción a reembolsar. | Referencia a la operación original |
| orgTransRRN | String (12) | Condicional | RRN original de la transacción. | Trazabilidad bancaria |
| transRemarks | String (1-50) | Opcional | Motivo del reembolso (visible para el usuario). | Transparencia y registro |
| refundAmount | Decimal (2 places) | Sí | Monto a devolver (debe ser ≤ monto original). | Control del valor devuelto |
| orgMeOrderNo | String (6-30) | Condicional | Orden original del merchant. | Reconciliación cruzada |
| addInfo1-10 | String (0-50) | Opcional | Información adicional (motivo, ticket, etc.). | Flexibilidad para casos de negocio |
| idempotencyKey | String | Recomendado | Clave para evitar reembolsos duplicados. | Seguridad en operaciones financieras |

**Response Exitosa**

```json
{
  "newMeOrderNo": "REF-20260607130000",
  "orgTransId": "TAPP4521EDFDF113434131442134D34D34FF",
  "newTransId": "TAPP-REF-9876543210ABCDEF",
  "refundAmount": 50.00,
  "transAuthDateTime": "2026-06-07T13:05:45Z",
  "respCode": "00",
  "refundStatus": "S",
  "refundMessage": "Success",
  "addInfo1": "Motivo: DEV-001"
}
```

**Response de Error (ejemplo)**

```json
{
  "refundStatus": "F",
  "refundMessage": "Original transaction not refundable",
  "errorCode": "REF-003"
}
```

---

### **Endpoint 10: POST /participants/register**

**(Onboarding de Proveedor de Servicios de Iniciación de Pagos \- PSIP)**

**Descripción**: Permite el registro formal de una fintech, billetera o aplicación como PSIP ante el agregador central TAPP. Forma parte de la gobernanza híbrida del BCRP y es requisito para operar en el ecosistema.

**Request JSON Completo**

```json
{
  "participantId": "PSIP-MIFINTECH-001",
  "legalName": "Mi Fintech SAC",
  "taxId": "20601234567",
  "contactEmail": "tech@mitfintech.pe",
  "contactPhone": "+51987654321",
  "redirectUris": ["https://mitfintech.pe/callback", "https://app.mitfintech.pe/auth"],
  "publicKey": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
  "allowedScopes": ["payments:transfer", "payments:collect", "accounts:balance"],
  "webhookUrl": "https://mitfintech.pe/webhooks/tapp",
  "idempotencyKey": "onboard-20260607123456789"
}
```

**Explicación campo por campo**:

| Campo | Tipo | Obligatorio | Descripción Detallada | Por qué se incluye (UPI \+ BCRP) |
| :---- | :---- | :---- | :---- | :---- |
| participantId | String | Sí | Identificador único elegido para este PSIP. | Identificación oficial y persistente ante el BCRP |
| legalName | String | Sí | Razón social completa de la empresa. | Cumplimiento KYC, legal y regulatorio |
| taxId | String | Sí | Número de RUC de la empresa. | Verificación regulatoria ante SBS y BCRP |
| contactEmail | String | Sí | Correo electrónico de contacto técnico. | Soporte operativo y notificaciones importantes |
| contactPhone | String | Sí | Número de teléfono de contacto. | Canales de comunicación y soporte |
| redirectUris | Array de strings | Sí | URLs válidas donde se redirigirá al usuario durante el flujo de consentimiento. | Seguridad en el flujo OAuth de autorización |
| publicKey | String (PEM) | Recomendado | Clave pública del PSIP para firma y verificación de mensajes. | Seguridad avanzada de mensajes (JWS/JWE) |
| allowedScopes | Array de strings | Sí | Lista de permisos que este PSIP podrá solicitar. | Gobernanza y control de acceso por participante |
| webhookUrl | String | Recomendado | URL donde TAPP enviará notificaciones asíncronas. | Soporta el modelo asíncrono de pagos instantáneos |
| idempotencyKey | String | Recomendado | Clave única para evitar registros duplicados. | Prevención de duplicados en el proceso de onboarding |

**Response Exitosa**

```json
{
  "participantId": "PSIP-MIFINTECH-001",
  "status": "PENDING_APPROVAL",
  "registeredAt": "2026-06-07T15:30:00Z",
  "apiKey": "tapp-psip-abc123xyz789",
  "sandboxBaseUrl": "https://sandbox-tapp.bcrp.gob.pe/api/v1/",
  "message": "Registro recibido. Será aprobado en las próximas 48 horas."
}
```

**Response de Error (ejemplo)**

```json
{
  "errorCode": "REG-002",
  "errorMessage": "Tax ID already registered",
  "details": { "taxId": "20601234567" }
}
```

---
