---
icon: lucide/home
---

# Billetera Digital - Documentación del Proyecto

Bienvenido a la documentación oficial del proyecto de la **Billetera Digital**. Este es un agregador de finanzas personales que se integra con la infraestructura TAPP del Banco Central de Reserva del Perú (BCRP) en su última fase de interoperabilidad.

## Propósito del Proyecto

Permitir a los usuarios consolidar y pagar desde cualquiera de sus cuentas (bancos, billeteras como Yape/Plin) y organizar sus gastos en un solo lugar de manera segura, sin tener que compartir sus credenciales bancarias directamente con la aplicación.

---

## Estructura de la Documentación

### 📐 Decisiones de Arquitectura
En esta sección se documentan las propuestas de diseño del sistema, tanto a nivel de infraestructura como de servicios.

* **Primera Propuesta (MVP Monolito Modular):**
    * [Arquitectura de Infraestructura (MVP)](first_proposal/INFRAESTRUCTURE_ARQ.md): Detalla el uso de contenedores en Azure, bases de datos (SQL y Cosmos), caché de Redis y el Mock de TAPP.
    * [Arquitectura de Servicios (MVP)](first_proposal/SERVICES_ARQ.md): Define las responsabilidades de cada módulo interno (Auth, Account, Payment, Finance) y la comunicación mediante MediatR.

---

## 🛠️ Comandos de Zensical

Esta documentación está construida y servida usando **Zensical**, un generador de sitios estáticos de alto rendimiento.

* `uv run zensical serve` - Inicia el servidor de desarrollo local en `http://localhost:8000`.
