# Guión de Exposición — Spondylus (Hito 2)
**Tiempo Total Estimado:** 5 Minutos (aprox. 1 minuto por integrante, ~120-150 palabras cada uno)

---

## 🎙️ Minuto 1: Cielo Cristal Meza Vizcarra
### Diapositivas: [1. Portada] y [2. Enfoque y Contexto]

> **[Slide 1 - Portada]**
> *"Buenas tardes, profesora Maribel Molina y compañeros. Nosotros somos el equipo de Sistemas Distribuidos y hoy presentaremos el Hito 2 de nuestro proyecto: **Spondylus**, una billetera digital interoperable pensada para resolver la fragmentación financiera de los usuarios en el Perú."*

> **[Slide 2 - Enfoque y Contexto]**
> *"Nuestro enfoque es riguroso. Spondylus funciona como un agregador de finanzas personales que consolida cuentas bancarias de múltiples entidades, interactuando con la infraestructura TAPP del BCRP para la liquidación interoperable.*
> *Para este desarrollo, nos basamos en tres pilares: primero, la gestión de requerimientos usando **User Story Mapping** para asegurar entregas continuas de valor; segundo, un núcleo matemático robusto con contabilidad de partida doble bitemporal y grafos dirigidos; y tercero, prácticas de calidad rigurosas que incluyen flujos estrictos en Git, revisión por pares en Pull Requests y arquitectura limpia."*

---

## 🎙️ Minuto 2: Rafael Diego Nina Calizaya
### Diapositiva: [3. User Story Mapping]

> **[Slide 3 - User Story Mapping]**
> *"Para organizar y priorizar nuestras metas de desarrollo en este MVP de 6 semanas, implementamos la metodología de **Jeff Patton: User Story Mapping**. Dividimos el viaje del cliente en un Backbone de cuatro actividades esenciales:*
> *1. **Acceso Unificado**, que permite un login seguro mediante teléfono y PIN y federa las identidades entre nodos.*
> *2. **Gestión de Cuentas**, para consolidar saldos reales y calcular el Safe-to-Spend.*
> *3. **Movimiento de Dinero**, que constituye el corazón distribuido del sistema mediante depósitos, retiros y transferencias.*
> *4. **Control y Análisis**, permitiendo presupuestar y corregir transacciones de forma retroactiva sin corromper el balance bancario.*
> *Este mapa nos permite cortar horizontalmente el backlog en **sprints semanales**, asegurando que cada incremento sea completamente funcional de extremo a extremo."*

---

## 🎙️ Minuto 3: Joe Daniel Flores Choquehuanca
### Diapositivas: [4. Diagrama de Contexto] y [5. Diagrama de Contenedores]

> **[Slide 4 - Diagrama de Contexto (C4)]**
> *"Para documentar el sistema adoptamos el **Modelo C4**. Aquí vemos el **Diagrama de Contexto**: Spondylus se sitúa en el centro, interactuando directamente con el Cliente para solicitudes de pago e informes. Externamente, interactuamos con la infraestructura TAPP del BCRP, la cual valida consentimientos y actúa como pasarela de compensación interoperable frente a los Bancos del Consorcio, quienes custodian los fondos reales."*

> **[Slide 5 - Diagrama de Contenedores (C4)]**
> *"Al bajar un nivel al **Diagrama de Contenedores**, observamos la separación de responsabilidades:*
> *El cliente interactúa con la **App Móvil (Flutter)**, la cual se comunica vía HTTPS con el **API Gateway**. Éste enruta las peticiones de identidad al **auth-service** (que aísla las credenciales) y las operaciones de negocio al **wallet-service**. Ambos consumen una base de datos **Azure SQL** para datos estructurados e idempotencia, mientras que el historial transaccional append-only se guarda en **Azure Cosmos DB**.*
> *Además, incluimos **Azure Service Bus** para el procesamiento asíncrono de eventos transaccionales y el contenedor **tapp-mock** para simular las APIs del BCRP en esta fase del MVP."*

---

## 🎙️ Minuto 4: Alvaro Raul Quispe Condori (Backend / Lógica de Negocio)
### Diapositiva: [6. Backend y Lógica de Negocio]

> **[Slide 6 - Backend y Lógica de Negocio]**
> *"En la parte del backend, implementamos la lógica de negocio bajo una **arquitectura hexagonal plana** para blindar nuestro modelo de dominio de cualquier tecnología externa.*
> *El dominio está modelado matemáticamente como un **grafo dirigido** donde las cuentas son **Nodos** y los movimientos son **Vectores**. El balance de una cuenta es simplemente la suma de sus vectores incidentes. Esto asegura que el ledger sea **append-only** e inmutable.*
> *También desarrollamos dos motores lógicos clave: primero, el **Netting Engine**, que agrupa transacciones a través de un `lineage_token` único y cancela movimientos lógicos temporales para mostrar reportes limpios y sin duplicaciones; y segundo, el algoritmo de **Safe-to-Spend**, que descuenta presupuestos comprometidos del saldo real para darle al usuario una visibilidad real de su liquidez disponible sin romper las invariants del banco."*

---

## 🎙️ Minuto 5: Rodrigo Alexander Fernandez Huarca (Infraestructura / App Distribuida)
### Diapositivas: [7. Infraestructura y App Distribuida] y [8. Aplicación Móvil]

> **[Slide 7 - Infraestructura y App Distribuida]**
> *"Como encargado de la app distribuida y DevOps, diseñé el aprovisionamiento elástico usando **Terraform** como Infraestructura como Código (IaC) para Azure Container Apps. ACA nos permite correr contenedores FastAPI sin la complejidad de AKS.*
> *Para facilitar el desarrollo y asegurar la consistencia, configuré un archivo **Docker Compose** local que orquesta el `auth-service`, `wallet-service` y `tapp-mock` de idéntica forma al entorno de la nube, permitiendo ejecutar pruebas de integración complejas en local con un solo comando."*

> **[Slide 8 - Aplicación Móvil]**
> *"En la aplicación móvil, utilizamos **Flutter** estructurado por características (Feature-First) siguiendo Clean Architecture:*
> *Implementamos Riverpod para el estado, y un `ClockInterceptor` personalizado en el cliente HTTP Dio para propagar y sincronizar **relojes lógicos de Lamport**, garantizando la ordenación causal de transacciones en la red distribuida.*
> *Además, adoptamos **pruebas co-localizadas** (donde los tests residen en la misma carpeta que el código) garantizando alta mantenibilidad. Ya contamos con los flujos de login, balance de cuentas y transferencias atómicas listos para demostración."*

---

## 🎙️ Minuto 5:15 - Cierre (Cielo o Alvaro)
### Diapositivas: [9. Estado de Avance y Roadmap] y [10. Referencias]

> **[Slide 9 - Estado de Avance y Roadmap]**
> *"Para cerrar, nuestro roadmap de avance muestra que completamos la **Semana 1** (la fundación distribuida con lectura federada). Actualmente estamos en la **Semana 2**, implementando transferencias atómicas interbancarias y el protocolo 2PC.*
> *La siguiente semana abarcaremos la **Semana 3** con presupuestos automatizados y el motor de netting, culminando en la **Semana 4** con pruebas de carga distribuidas."*

> **[Slide 10 - Referencias (IEEE)]**
> *"Estas son las referencias académicas y de la industria en las que nos hemos basado para asegurar la consistencia formal y el cumplimiento normativo. Quedamos abiertos a sus preguntas. Muchas gracias."*
