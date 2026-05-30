## Convenciones de Commit

## 1. **Usa un formato claro y consistente para tus mensajes de commit**
- **feat**: Una nueva característica para el usuario.
- **fix**: Arregla un bug que afecta al usuario.
- **perf**: Cambios que mejoran el rendimiento del sitio.
- **build**: Cambios en el sistema de build, tareas de despliegue o instalación.
- **ci**: Cambios en la integración continua.
- **docs**: Cambios en la documentación.
- **refactor**: Refactorización del código como cambios de nombre de variables o funciones.
- **style**: Cambios de formato, tabulaciones, espacios o puntos y coma, etc; no afectan al usuario.
- **test**: Añade tests o refactoriza uno existente.
 
## 2. Referencia issues y pull requests en tus commits
Cuando trabajas en un proyecto con issues, puedes referenciar el issue en el mensaje del commit. Esto crea un vínculo entre el commit y el issue en GitHub, y permite **cerrar issues automáticamente** al hacer merge a la rama principal.

**a. Para referenciar un issue sin cerrarlo, usa el símbolo `#` seguido del número:**

```
git commit -m "feat: add search by category #123"
```

**b. Para cerrar el issue automáticamente cuando el commit llegue a la rama principal, usa palabras clave especiales:**

```
git commit -m "fix: correct typo in register form closes #123"
```
