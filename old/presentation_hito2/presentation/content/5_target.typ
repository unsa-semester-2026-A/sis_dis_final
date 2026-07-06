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
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[MODELO C4: DIAGRAMA DE CONTENEDORES]
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
          spacing: 20pt,
          text(size: 19pt, fill: style.theme.text-muted)[
            Muestra las fronteras tecnológicas y la arquitectura de servicios distribuidos del MVP.
          ],
          [
            #set text(size: 16pt)
            #set list(marker: ([#text(fill: style.theme.primary)[•]],))
            - *App Móvil*: Cliente en Flutter con sincronización de relojes de Lamport.
            - *auth-service*: FastAPI. Maneja PIN y OTP de forma aislada.
            - *wallet-service*: FastAPI. Contiene el core del ledger.
            - *Bases de Datos*: Azure SQL para datos transaccionales y Cosmos DB para historial append-only.
            - *Mensajería*: Azure Service Bus para el flujo asíncrono de confirmación.
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
        #image("../src/fig/diagrams/Container.svg", fit: "contain")
      ]
    ]
  )
]
