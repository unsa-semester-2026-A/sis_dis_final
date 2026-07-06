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
      #text(size: 48pt, weight: "bold", fill: style.theme.text-dark)[INFRAESTRUCTURA Y APP DISTRIBUIDA]
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
            Infraestructura elástica y automatizada diseñada para dar soporte al entorno distribuido de microservicios.
          ],
          [
            #set text(size: 17pt)
            #set list(marker: ([#text(fill: style.theme.primary)[•]],))
            - *Azure Container Apps*: Servidor serverless para ejecutar contenedores FastAPI y mock-TAPP de manera segura y escalable sin la sobrecarga de AKS.
            - *Infraestructura como Código (IaC)*: Terraform automatiza el despliegue del API Gateway, bases de datos (SQL y Cosmos) y Key Vault.
            - *Orquestación Local*: Archivo Docker Compose unificado para levantar de extremo a extremo los servicios y realizar pruebas de integración de manera ágil.
            - *Simulación Externa*: Contenedor `tapp-mock` para aislar dependencias del BCRP y habilitar pruebas del ciclo de vida del pago.
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
        #image("../src/fig/diagrams/arquitectura.png", fit: "contain")
      ]
    ]
  )
]
