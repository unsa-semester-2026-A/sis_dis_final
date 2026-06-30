#import "../slides.typ": slide-page
#import "../style.typ" as style

#slide-page[
  #place(top + left, dx: 80pt, dy: 55pt)[
    #text(size: 58pt, weight: "bold", fill: style.theme.text-dark)[TWO PHASE COMMIT]
  ]

  #place(top + left, dx: 120pt, dy: 135pt)[
    #box(width: 760pt, height: 480pt)[
      #image("../src/fig/diagrams/twopc.png", fit: "contain")
    ]
  ]

  #place(top + left, dx: 940pt, dy: 170pt)[
    #box(width: 360pt)[
      #text(size: 25pt, weight: "bold")[Coordinación distribuida]
      #v(18pt)
      #text(size: 19pt, fill: style.theme.text-muted)[
        El coordinador solicita a los bancos preparar la operación.
      ]

      #v(24pt)

      #text(size: 25pt, weight: "bold")[Confirmación o reversión]
      #v(18pt)
      #text(size: 19pt, fill: style.theme.text-muted)[
        Si todos aceptan, se confirma. Si algún nodo falla, se ejecuta rollback.
      ]
    ]
  ]

  #place(top + left, dx: 120pt, dy: 665pt)[
    #rect(width: 1160pt, height: 58pt, fill: style.theme.primary, radius: 8pt)[
      #align(center + horizon)[
        #text(size: 24pt, weight: "bold")[Prepare → Vote → Commit / Rollback]
      ]
    ]
  ]
]