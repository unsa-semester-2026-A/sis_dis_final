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
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[MODELO C4: DIAGRAMA DE CONTEXTO]
    ]
  )

  // Explicación lateral izquierda
  #place(
    top + left,
    dx: 81pt,
    dy: 170pt,
    [
      #box(width: 380pt)[
        #stack(
          spacing: 24pt,
          text(size: 20pt, fill: style.theme.text-muted)[
            El diagrama de contexto define los límites del sistema Spondylus y cómo se relaciona con actores y plataformas externas.
          ],
          [
            #set list(marker: ([#text(fill: style.theme.primary)[•]],))
            - *Cliente*: Actor principal. Inicia transferencias y visualiza reportes.
            - *Infraestructura TAPP*: Pasarela de pagos del BCRP para liquidación interoperable.
            - *Bancos del Consorcio*: Custodian los saldos reales de las cuentas del usuario.
          ]
        )
      ]
    ]
  )

  // Imagen del diagrama a la derecha
  #place(
    top + left,
    dx: 500pt,
    dy: 140pt,
    [
      #box(width: 860pt, height: 560pt)[
        #align(center + horizon)[#image("../src/fig/diagrams/Context.svg", fit: "contain")]
      ]
    ]
  )
]
