#import "../slides.typ": slide-pills-list

#slide-pills-list(
  title: "ARQUITECTURA GENERAL",
  body: [
    La solución se plantea como un sistema distribuido pequeño y realista para el alcance del curso.
  ],
  pills: (
    "Mobile App → API Gateway",
    "Auth Service + Wallet Service",
    "TAPP Mock como dependencia externa",
    "Azure SQL, Cosmos DB y Service Bus",
  ),
  image: image("../src/fig/diagrams/arquitectura.png", fit: "contain")
)