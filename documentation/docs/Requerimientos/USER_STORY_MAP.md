---
icon: lucide/map
---

# User Story Map

> Metodología: **Jeff Patton — User Story Mapping**  
> Fecha de corte: 2026-06-22  
> Horizonte: **4 semanas** (avance académico)  
> Stack previsto: Flutter (mobile-first) · Python/FastAPI (backend) · Sistema Distribuido (3 nodos-banco)

---

## ¿Por qué un Story Map?

Patton propone organizar el trabajo en dos ejes:

- **Eje horizontal (Backbone):** las actividades del usuario de izquierda a derecha, en el orden en que ocurren. Representan el "viaje" completo.
- **Eje vertical (slice):** las historias se apilan bajo cada actividad, de mayor a menor prioridad. Los cortes horizontales forman **releases** o **sprints**.

El mapa completo es la narrativa de uso del sistema; los slices verticales son las entregas iterativas.

---

## Usuarios del sistema

| Actor | Descripción |
|---|---|
| **Cliente** | Persona con cuentas en uno o más bancos del consorcio. |
| **Sistema Distribuido** | Conjunto de tres nodos-banco interconectados que procesan transacciones de forma coordinada. |

> El único actor relevante para el story map es el **Cliente**. El Sistema Distribuido es infraestructura, no un actor con intenciones.

---

## Backbone — Actividades del usuario

Las actividades son los pasos de alto nivel que cualquier cliente realiza al usar el sistema. Se leen de izquierda a derecha como una historia coherente.

```
[ Acceder al sistema ] → [ Gestionar cuentas ] → [ Mover dinero ] → [ Controlar gastos ] → [ Revisar y entender ]
```

---

## Story Map completo

Las filas coloreadas marcan los **slices de entrega** para las 4 semanas.

---

### 🗂 Actividad 1 — Acceder al sistema

> El usuario se identifica y el sistema lo reconoce independientemente de en qué banco-nodo inicia sesión.

| Prioridad | Historia de usuario |
|---|---|
| ⭐ Esencial | **Como cliente**, quiero iniciar sesión con mi número de teléfono y PIN, **para** acceder a todas mis cuentas desde cualquier banco. |
| ⭐ Esencial | **Como cliente**, quiero que el sistema me muestre todas mis cuentas (de cualquier banco del consorcio) al iniciar sesión, **para** tener una vista unificada de mi patrimonio. |
| ○ Deseable | **Como cliente**, quiero que mi sesión persista de forma segura entre bancos, **para** no re-autenticarme si cambio de nodo de acceso. |

---

### 🗂 Actividad 2 — Gestionar cuentas

> El usuario registra, consulta y organiza sus cuentas reales y sus nodos lógicos internos.

| Prioridad | Historia de usuario |
|---|---|
| ⭐ Esencial | **Como cliente**, quiero registrar mis cuentas bancarias reales (de cualquier banco del consorcio), **para** que el sistema pueda rastrear mi saldo real y reconciliar diferencias. |
| ⭐ Esencial | **Como cliente**, quiero ver el saldo actual de cada cuenta, **para** saber cuánto dinero tengo disponible en cada banco. |
| ⭐ Esencial | **Como cliente**, quiero ver un "dinero libre" (Safe-to-Spend) que descuente compromisos de presupuesto, **para** no gastar dinero que ya está asignado. |
| ○ Deseable | **Como cliente**, quiero crear una cuenta virtual dedicada a un objetivo de ahorro, **para** aislar dinero destinado a una meta específica. |

---

### 🗂 Actividad 3 — Mover dinero

> El usuario realiza transacciones: retiros, depósitos, transferencias entre cuentas de distintos bancos. Este es el núcleo del requisito de sistemas distribuidos.

| Prioridad | Historia de usuario |
|---|---|
| ⭐ Esencial | **Como cliente**, quiero depositar dinero en una cuenta desde cualquier banco-nodo, **para** que la operación se refleje como si fuera local aunque mis cuentas estén en otro banco. |
| ⭐ Esencial | **Como cliente**, quiero retirar dinero de una cuenta, **para** disminuir mi saldo y registrar el movimiento. |
| ⭐ Esencial | **Como cliente**, quiero transferir dinero entre dos de mis cuentas (en distintos bancos del consorcio) en una sola operación, **para** no hacer retiro y depósito por separado. |
| ⭐ Esencial | **Como cliente**, quiero consultar el historial de mis transacciones, **para** saber qué operaciones realicé y cuándo. |
| ○ Deseable | **Como cliente**, quiero registrar un pago fraccionado en una sola operación, **para** que el sistema sepa el destino real de cada parte (ej. 100 PEN comida + 100 PEN adelantados a un amigo). |
| ○ Deseable | **Como cliente**, quiero registrar que le presté dinero a un amigo y luego que me pagó, **para** que mi patrimonio neto no cambie pero mi liquidez sí. |

---

### 🗂 Actividad 4 — Controlar gastos

> El usuario organiza sus gastos con presupuestos, categorías y correcciones. Implementa el motor lógico (Layer 2 del core).

| Prioridad | Historia de usuario |
|---|---|
| ⭐ Esencial | **Como cliente**, quiero categorizar cada gasto al registrarlo, **para** saber a dónde va mi dinero. |
| ⭐ Esencial | **Como cliente**, quiero crear un presupuesto mensual para una categoría, **para** tener un límite de gasto. |
| ⭐ Esencial | **Como cliente**, quiero que los presupuestos se creen automáticamente cada mes, **para** no repetir la misma tarea manualmente. |
| ⭐ Esencial | **Como cliente**, quiero corregir la categoría de un gasto registrado (incluso una semana después), **para** que los reportes reflejen lo real sin alterar el balance bancario. |
| ○ Deseable | **Como cliente**, quiero registrar un gasto imprevisto (multa) sin crear un presupuesto para ese tipo, **para** no contaminar mi estructura de categorías. |
| ○ Deseable | **Como cliente**, quiero activar un presupuesto acumulativo, **para** que el saldo no gastado del mes anterior se sume al límite del mes siguiente. |
| ○ Deseable | **Como cliente**, quiero definir un presupuesto anual para un gasto único, **para** que el sistema no lo compare con mi límite mensual normal. |

---

### 🗂 Actividad 5 — Revisar y entender

> El usuario consulta reportes. Esta actividad usa el motor de netting y los tags ortogonales.

| Prioridad | Historia de usuario |
|---|---|
| ⭐ Esencial | **Como cliente**, quiero ver un reporte de mis ingresos del mes, **para** saber cuánto dinero entró al sistema. |
| ⭐ Esencial | **Como cliente**, quiero ver un reporte de mis gastos agrupados por categoría, **para** saber a dónde se fue mi dinero. |
| ○ Deseable | **Como cliente**, quiero etiquetar gastos con un contexto de viaje, **para** ver un reporte total de ese viaje aunque los gastos estén en categorías distintas. |
| ○ Deseable | **Como cliente**, quiero que el sistema me ayude a "balancear" gastos no registrados, **para** reconciliar la diferencia entre mi saldo lógico y el saldo real del banco. |

---

## Slices de entrega — 4 semanas

> Siguiendo a Patton: cada slice debe ser un corte horizontal del mapa que entrega **valor real al usuario**, no componentes técnicos aislados.

```
Semana 1         Semana 2          Semana 3         Semana 4
──────────       ──────────        ──────────       ──────────
Fundación        Dinero            Control          Cierre
distribuida      distribuido       de gastos        académico
```

---

### Semana 1 — Fundación distribuida

**Meta:** El usuario puede autenticarse y ver sus cuentas. Los 3 nodos-banco están operativos con archivos como storage.

**Conceptos de sistemas distribuidos aplicados:**
- 📁 **Sistema de archivos distribuidos:** cada nodo-banco almacena sus propias cuentas en archivos locales; lectura federada al hacer login.
- 🔒 **Coordinación:** directorio central o elección de líder para federar identidades entre los tres bancos.

| Actividad | Historia |
|---|---|
| Acceder | Login con teléfono y PIN → JWT válido en cualquier nodo |
| Acceder | Vista unificada de todas las cuentas del cliente al iniciar sesión |
| Gestionar cuentas | Registrar una cuenta real (banco + número de cuenta) |
| Gestionar cuentas | Consultar saldo de cada cuenta |

**Criterios de aceptación:**
- Un cliente con cuentas en los 3 bancos puede hacer login en el banco A y ver sus 3 cuentas.
- Los datos de cuentas se leen desde archivos en cada nodo (no desde una DB centralizada).
- El sistema federa la respuesta correctamente.

---

### Semana 2 — Dinero distribuido

**Meta:** El usuario puede mover dinero entre cuentas de distintos bancos. El sistema garantiza consistencia transaccional.

**Conceptos de sistemas distribuidos aplicados:**
- 🔄 **Transacciones distribuidas:** protocolo 2PC para garantizar atomicidad entre nodos.
- ⚖️ **Control de concurrencia:** tokens de idempotencia para evitar doble gasto.
- 📋 **Coordinación:** log de operaciones distribuido append-only replicado entre nodos.

| Actividad | Historia |
|---|---|
| Mover dinero | Depositar en una cuenta desde cualquier nodo |
| Mover dinero | Retirar de una cuenta |
| Mover dinero | Transferir entre dos cuentas de distintos bancos |
| Mover dinero | Consultar historial de transacciones |

**Criterios de aceptación:**
- Una transferencia del banco A al banco C es atómica: o se completa en ambos, o se revierte en ambos.
- Dos transferencias simultáneas sobre la misma cuenta no corrompen el saldo.

---

### Semana 3 — Control de gastos

**Meta:** El usuario puede categorizar gastos y crear presupuestos. El motor lógico (Layer 1 y 2 del core) está operativo.

**Conceptos de sistemas distribuidos aplicados:**
- 🕑 **Consistencia eventual:** la corrección tardía de un gasto propaga el cambio a todos los nodos que replican el log.
- 🔑 **Idempotencia:** los vectores correctivos usan el mismo `lineage_token`, garantizando que una corrección aplicada dos veces no genera doble efecto.

| Actividad | Historia |
|---|---|
| Controlar gastos | Categorizar un gasto al registrarlo |
| Controlar gastos | Crear presupuesto mensual para una categoría |
| Controlar gastos | Activar auto-creación de presupuestos mensuales |
| Controlar gastos | Corregir la categoría de un gasto pasado (con fecha efectiva) |
| Revisar | Reporte de ingresos del mes |
| Revisar | Reporte de gastos por categoría |

**Criterios de aceptación:**
- Corregir la categoría de un gasto de 7 días atrás no altera el balance del banco, solo el reporte.
- El presupuesto mensual de "Comida" se auto-crea el 1 de cada mes sin acción del usuario.
- El motor de netting devuelve el origen y destino real del dinero, colapsando pasos intermedios.

---

### Semana 4 — Cierre académico

**Meta:** Pulir, integrar conceptos pendientes y preparar todos los entregables.

**Historias incluidas (deseables realistas):**

| Actividad | Historia |
|---|---|
| Mover dinero | Registrar préstamo a un amigo y su devolución |
| Controlar gastos | Registrar gasto imprevisto sin presupuesto asociado |
| Revisar | Etiquetar gastos por contexto (viaje) y ver reporte agrupado |
| Gestionar cuentas | Consultar Safe-to-Spend (dinero libre descontando compromisos) |

**Entregables académicos:**
- Informe con capturas de pantalla.
- Artículo de síntesis.
- Video de demostración (todos los integrantes participan).
- Diapositivas de presentación.

---

## Historias excluidas del avance (backlog futuro)

| Historia | Razón de exclusión |
|---|---|
| Asistente de balance automático (AI) | Requiere integración externa fuera del alcance del curso |
| Presupuesto acumulativo | Deseable; implementable si sobra tiempo en Semana 4 |
| Presupuesto anual para pago único | Deseable; la base de Semana 3 lo soporta parcialmente |
| Cuenta virtual dedicada | Requiere UI adicional no prioritaria |
| Pago fraccionado (split payment) | Complejo en UI mobile; la lógica ya está en el core |
| Automatizaciones avanzadas (cron distribuido) | Fuera del scope del avance |

---

## Relación con los criterios de evaluación

| Criterio (puntaje) | Semana | Concepto aplicado |
|---|---|---|
| Sistema de archivos distribuidos (4 pts) | Semana 1 | Archivos por nodo, lectura federada |
| Coordinación y acuerdo (4 pts) | Semanas 1–2 | Elección de líder, 2PC, log distribuido |
| Transacción y concurrencia (4 pts) | Semanas 2–3 | 2PC, idempotencia, consistencia eventual |
| Implementación general (16 pts) | Semanas 1–4 | Todas las historias ⭐ Esencial |
| Aportes e informe (4 pts) | Semana 4 | Historias ○ Deseable + entregables |

---

> **Nota de scope:** Las historias ⭐ son el **MVP mínimo evaluable**. Las ○ añaden puntaje en "Aportes". Si el tiempo apremia, se prioriza siempre el backbone completo con ⭐ antes de profundizar en ○.
