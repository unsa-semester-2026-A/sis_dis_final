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
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[BACKEND Y LÓGICA DE NEGOCIO]
    ]
  )

  // Explicación lateral izquierda
  #place(
    top + left,
    dx: 81pt,
    dy: 170pt,
    [
      #box(width: 580pt)[
        #stack(
          spacing: 20pt,
          text(size: 21pt, fill: style.theme.text-muted)[
            Implementado bajo una arquitectura hexagonal plana, desacoplando el núcleo de dominio de la infraestructura de almacenamiento.
          ],
          [
            #set text(size: 17pt)
            #set list(marker: ([#text(fill: style.theme.primary)[•]],))
            - *Modelo de Grafo Dirigido*: Las finanzas del cliente se representan mediante *Nodos* (Asset, Liability, Source, Sink) y *Vectores* (mutaciones de valor inmutables).
            - *Ledger Append-Only*: Garantiza la trazabilidad e inmutabilidad requerida por la integración con TAPP del BCRP.
            - *Motor de Netting*: Reduce y consolida movimientos lógicos utilizando un `lineage_token` único para reportes limpios libres de duplicación.
            - *Safe-To-Spend*: Algoritmo que descuenta compromisos de presupuestos pasivos de los saldos líquidos reales para prevenir el sobregasto.
          ]
        )
      ]
    ]
  )

  // Imagen del diagrama a la derecha
  #place(
    top + left,
    dx: 720pt,
    dy: 160pt,
    [
      #box(width: 640pt, height: 500pt)[
        #image("../src/fig/diagrams/node-vector.png", fit: "contain")
      ]
    ]
  )
]
