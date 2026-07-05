#import "../slides.typ": slide-page
#import "../style.typ" as style
#import "../components.typ" as comp

#slide-page[
  // Fondo amarillo lateral, como otras diapositivas
  #place(top + left, dx: 0pt, dy: 0pt)[
    #rect(width: 360pt, height: 810pt, fill: style.theme.primary, stroke: none)
  ]

  // Decoración de puntos
  #comp.dot-grid(
    1030pt,
    30pt,
    320pt,
    120pt,
    cols: 12,
    rows: 5,
    dot-radius: 2.2pt,
    dot-color: style.theme.text-dark,
  )

  // Título lateral
  #place(top + left, dx: 65pt, dy: 265pt)[
    #box(width: 250pt)[
      #text(size: 43pt, weight: "bold", fill: style.theme.text-dark)[
        #set par(leading: 0.35em)
        BACKEND \
        HEXAGONAL
      ]

      #v(28pt)

      #text(size: 18pt, fill: style.theme.text-dark)[
        Separación entre dominio, casos de uso, puertos y adaptadores.
      ]
    ]
  ]

  // Diagrama centrado en el área blanca
  #place(top + left, dx: 455pt, dy: 105pt)[
    #box(width: 760pt, height: 500pt)[
      #image("../src/fig/diagrams/hexagonal.png", fit: "contain")
    ]
  ]

  // Frase inferior tipo cierre
  #place(top + left, dx: 455pt, dy: 640pt)[
    #box(width: 760pt)[
      #text(size: 21pt, fill: style.theme.text-muted)[
        Arquitectura basada en puertos y adaptadores para desacoplar la lógica de negocio de la infraestructura.
      ]
    ]
  ]
]