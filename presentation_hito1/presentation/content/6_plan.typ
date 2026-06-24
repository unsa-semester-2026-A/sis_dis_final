#import "../slides.typ": slide-action-plan

#slide-action-plan(
  title: "AVANCE\nBACKEND",
  body: [
    Se desarrolló una base de arquitectura hexagonal para el núcleo financiero.
  ],
  items: (
    ("01", "Dominio", "Entidades Node y Vector como base del grafo financiero.", "Backend dominio"),
    ("02", "Casos de uso", "CreateNode, EmitVector y EvaluateBalance.", "Use cases"),
    ("03", "Adaptadores", "Puertos, REST/File Store y pruebas iniciales.", "Adapters")
  )
)