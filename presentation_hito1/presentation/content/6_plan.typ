#import "../slides.typ": slide-page
#import "../style.typ" as style

#slide-page[
  #place(top + left, dx: 80pt, dy: 60pt)[
    #text(size: 58pt, weight: "bold", fill: style.theme.text-dark)[BACKEND HEXAGONAL]
  ]

  #place(top + left, dx: 210pt, dy: 155pt)[
    #box(width: 1020pt, height: 420pt)[
      #image("../src/fig/diagrams/hexagonal.png", fit: "contain")
    ]
  ]

  #place(top + left, dx: 120pt, dy: 610pt)[
    #grid(
      columns: (1fr, 1fr, 1fr),
      column-gutter: 36pt,
      [
        #text(size: 25pt, weight: "bold")[Dominio]
        #text(size: 17pt, fill: style.theme.text-muted)[Node y Vector forman el núcleo financiero.]
      ],
      [
        #text(size: 25pt, weight: "bold")[Casos de uso]
        #text(size: 17pt, fill: style.theme.text-muted)[CreateNode, EmitVector y EvaluateBalance.]
      ],
      [
        #text(size: 25pt, weight: "bold")[Adaptadores]
        #text(size: 17pt, fill: style.theme.text-muted)[REST, File Store y puertos de infraestructura.]
      ],
    )
  ]
]