#import "../slides.typ": slide-timeline

#slide-timeline(
  title: "SISTEMAS\nDISTRIBUIDOS",
  card-title: "2 PHASE COMMIT",
  card-body: [
    Para transferencias entre bancos, el sistema debe coordinar nodos y garantizar que la operación se confirme en todos o se revierta.
  ],
  items: (
    ("01", "Prepare", "El coordinador consulta si los nodos pueden ejecutar la operación."),
    ("02", "Vote", "Cada banco responde si está listo o si debe abortar."),
    ("03", "Commit", "Si todos aceptan, se confirma la transacción."),
    ("04", "Rollback", "Si un nodo falla, se revierte la operación.")
  )
)