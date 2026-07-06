#import "../slides.typ": slide-grid-list

#slide-grid-list(
  title: "USER STORY MAPPING",
  body: [
    El *Backbone* define las actividades esenciales del cliente de izquierda a derecha. Cada columna apila historias de usuario priorizadas en *releases* semanales.
  ],
  items: (
    ("1", "Acceder al Sistema", "Autenticación federada: login con teléfono y PIN desde cualquier nodo bancario del consorcio."),
    ("2", "Gestionar Cuentas", "Visualización consolidada de saldos y cálculo del saldo real disponible (Safe-to-Spend)."),
    ("3", "Mover Dinero", "Operaciones transaccionales distribuidas y consistentes (retiros, depósitos y transferencias)."),
    ("4", "Control y Análisis", "Presupuestos mensuales automáticos, corrección retroactiva de gastos y reporte consolidado por netting."),
  ),
  columns: 2
)
