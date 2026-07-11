#import "../slides.typ": slide-page
#import "../style.typ" as style

#slide-page[
  #place(top + left, dx: 80pt, dy: 55pt)[
    #text(size: 58pt, weight: "bold", fill: style.theme.text-dark)[NODE + VECTOR]
  ]

  #place(top + left, dx: 90pt, dy: 150pt)[
    #box(width: 760pt, height: 460pt)[
      #image("../src/fig/diagrams/node-vector.png", fit: "contain")
    ]
  ]

  #place(top + left, dx: 900pt, dy: 160pt)[
    #box(width: 410pt)[
      #text(size: 25pt, weight: "bold")[Modelo como grafo]
      #v(14pt)
      #text(size: 19pt, fill: style.theme.text-muted)[
        El sistema modela las finanzas como nodos conectados por movimientos.
      ]

      #v(24pt)

      #text(size: 25pt, weight: "bold")[Node]
      #v(14pt)
      #text(size: 19pt, fill: style.theme.text-muted)[
        Representa cuentas, fuentes, deudas o categorías.
      ]

      #v(24pt)

      #text(size: 25pt, weight: "bold")[Vector]
      #v(14pt)
      #text(size: 19pt, fill: style.theme.text-muted)[
        Representa movimientos inmutables dentro del ledger append-only.
      ]
    ]
  ]
]