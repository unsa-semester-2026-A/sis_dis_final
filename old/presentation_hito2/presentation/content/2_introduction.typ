#import "../slides.typ": slide-section

#slide-section(
  title: "ENFOQUE Y CONTEXTO",
  body: [
    *Spondylus* es un agregador de finanzas personales que consolida cuentas del consorcio de bancos e interactúa con la infraestructura *TAPP del BCRP*.
    
    #v(10pt)
    El proyecto adopta un enfoque riguroso:
    - *Gestión de Requerimientos*: Guiado por *User Story Mapping* para entregas semanales de valor.
    - *Lógica de Negocio*: Modelado formal mediante un grafo dirigido inmutable y contabilidad bitemporal de partida doble.
    - *Desarrollo Ágil*: Reglas estrictas en Git, revisión por pares y diseño guiado por pruebas (TDD).
  ],
  card-title: "PROBLEMA Y PROPÓSITO",
  card-body: [
    Eliminar la fragmentación de la información financiera y habilitar transferencias inmediatas e interoperables en un entorno distribuido y altamente consistente.
  ]
)
