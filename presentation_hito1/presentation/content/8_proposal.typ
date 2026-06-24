#import "../slides.typ": slide-stacked-cards

#slide-stacked-cards(
  title: "MODELO\nFINANCIERO",
  subtitle: "Node + Vector",
  body: [
    La lógica del sistema modela las finanzas como un grafo dirigido.
    Los nodos representan actores financieros y los vectores representan movimientos inmutables.
  ],
  cards: (
    "NODE: ASSET, LIABILITY, SOURCE Y SINK",
    "VECTOR: MOVIMIENTO APPEND-ONLY",
    "LINEAGE TOKEN PARA AUDITORÍA Y REPORTES",
  )
)