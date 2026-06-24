#import "../slides.typ": slide-pills-list

#slide-pills-list(
  title: "ARQUITECTURA GENERAL",
  body: [
    La solución se plantea como un sistema distribuido pequeño y realista para el alcance del curso.
  ],
  pills: (
    "MOBILE APP → API GATEWAY",
    "AUTH SERVICE + WALLET SERVICE",
    "TAPP MOCK COMO DEPENDENCIA EXTERNA",
    "AZURE SQL, COSMOS DB Y SERVICE BUS",
  ),
  image: image("../src/fig/fixed/unsa.png", fit: "contain")
)