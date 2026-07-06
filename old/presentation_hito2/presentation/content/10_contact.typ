#import "../slides.typ": slide-page
#import "../style.typ" as style
#import "../components.typ" as comp

#slide-page[
  #if true {
    comp.bottom-left-decoration()
  }

  // Título de la diapositiva
  #place(
    top + left,
    dx: 81pt,
    dy: 55pt,
    [
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[REFERENCIAS (IEEE)]
    ]
  )

  // Referencias en dos columnas
  #place(
    top + left,
    dx: 81pt,
    dy: 170pt,
    [
      #grid(
        columns: (600pt, 600pt),
        column-gutter: 80pt,
        [
          #set text(size: 17pt)
          #stack(
            spacing: 24pt,
            [
              #text(weight: "bold", fill: style.theme.primary)[[1]] 
              S. Brown, _Software Architecture for Developers: Visualise, Document and Explore Your Software Architecture_, 2018.
            ],
            [
              #text(weight: "bold", fill: style.theme.primary)[[2]] 
              M. Fowler, _Patterns of Enterprise Application Architecture_, Boston, MA: Addison-Wesley, 2002.
            ],
            [
              #text(weight: "bold", fill: style.theme.primary)[[3]] 
              J. Patton, _User Story Mapping: Discover the Whole Story, Build the Right Product_, Sebastopol, CA: O'Reilly Media, 2014.
            ]
          )
        ],
        [
          #set text(size: 17pt)
          #stack(
            spacing: 24pt,
            [
              #text(weight: "bold", fill: style.theme.primary)[[4]] 
              M. T. Özsu and P. Valduriez, _Principles of Distributed Database Systems_, 4th ed., Springer, 2020.
            ],
            [
              #text(weight: "bold", fill: style.theme.primary)[[5]] 
              E. Evans, _Domain-Driven Design: Tackling Complexity in the Heart of Software_, Boston, MA: Addison-Wesley, 2003.
            ],
            [
              #text(weight: "bold", fill: style.theme.primary)[[6]] 
              Banco Central de Reserva del Perú, _Reglamento de Interoperabilidad de los Servicios de Pago_, Lima, Perú, 2022.
            ]
          )
        ]
      )
    ]
  )
]
