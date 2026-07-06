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
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[APLICACIÓN MÓVIL (FLUTTER)]
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
            Cliente móvil desarrollado en Flutter aplicando Clean Architecture y estructurado por características (Feature-First).
          ],
          [
            #set text(size: 17pt)
            #set list(marker: ([#text(fill: style.theme.primary)[•]],))
            - *Capas de la Arquitectura*: Separación estricta entre la capa de Presentación (widgets y Riverpod), Dominio (entidades y contratos) y Datos (orígenes y modelos Freezed).
            - *Sincronización por Lamport*: Integración de `ClockInterceptor` en Dio para mantener la consistencia temporal lógica en peticiones distribuidas.
            - *Pruebas Co-localizadas*: Pruebas ubicadas junto al código que testean (ej. `user_test.dart`) garantizando alta cohesión y mantenibilidad.
            - *Módulos Implementados*: Login con PIN y SMS (`auth`), listado de cuentas (`accounts`), inicio de transferencias (`transactions`) y presupuestos (`budget`).
          ]
        )
      ]
    ]
  )

  // Imagen de la aplicación móvil a la derecha
  #place(
    top + left,
    dx: 720pt,
    dy: 160pt,
    [
      #box(width: 640pt, height: 500pt)[
        #align(center + horizon)[#image("../../1.png", fit: "contain")]
      ]
    ]
  )
]
