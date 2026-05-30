---
name: Solicitud de funcionalidad
about: Proponer una nueva característica o mejora
title: "[Feature]: "
labels: enhancement
assignees: ""
---

## Descripción de la Funcionalidad
[Una descripción clara y concisa de la nueva característica que se desea implementar.]

### Historia de Usuario
- **Como** [ej. Ingeniero de soporte / Usuario final]
- **Quiero** [ej. poder pausar la carga de archivos grandes]
- **Para** [ej. no perder el progreso si mi conexión es inestable].

---

## Criterios de Aceptación (Definición de Hecho)
[Lista de condiciones obligatorias que debe cumplir la funcionalidad para considerarse terminada.]
- [ ] El usuario debe ver un botón de "Pausar" visible durante la carga.
- [ ] Al reanudar, la carga debe continuar desde el último bloque guardado.
- [ ] Se deben incluir pruebas unitarias para el estado de pausa.
- [ ] La documentación de la API debe actualizarse.

---

## Propuesta Técnica (Opcional)
[Si ya tienes una idea de cómo resolverlo a nivel de arquitectura, librerías o base de datos, agrégala aquí.]
- Modificar el controlador `UploadController` para manejar estados de `PAUSED`.
- Usar la librería X para el manejo de chunks en el frontend.

---

## Diseño / UI (Si aplica)
[Mockups, bocetos o referencias visuales de cómo debería verse en la interfaz.]
- *Arrastra aquí tus imágenes o diagramas.*

## Contexto Adicional
[Cualquier otra información relevante, dependencias con otros Issues o fechas límite.]