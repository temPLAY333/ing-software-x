# Assets (imágenes y archivos estáticos)

## Dónde guardar

- **Ruta en el proyecto:** `frontend/src/assets/`
- En la app se referencian con la ruta **`assets/nombre-del-archivo`** (sin `src/`).

Ejemplo: si guardas `frontend/src/assets/default-avatar.png`, en el HTML/TS usas:
```html
src="assets/default-avatar.png"
```

## Avatar por defecto

Para evitar el 404 del avatar, añade una imagen en esta carpeta con el nombre:

- **`default-avatar.png`** (recomendado)

Así la usarán los componentes de mensajes privados cuando el usuario no tenga `fotoUsuario`.

## Fotos en la base de datos

Las fotos de perfil **no se guardan como archivo en la BD**, sino como **URL** en el campo `fotoUsuario` del usuario:

1. El usuario sube una imagen con **POST** `/api/upload/avatar` (backend guarda el archivo en el servidor).
2. El backend devuelve la URL (p. ej. `http://localhost:5000/uploads/avatars/abc123.png`).
3. Se actualiza el perfil con **PATCH** `/api/usuarios/me` y `{ "fotoUsuario": "esa URL" }`.
4. En la app se usa `usuario.fotoUsuario` en `<img [src]="...">`; si está vacío, se usa `assets/default-avatar.png`.

## Formatos recomendados

| Uso              | Formato | Notas                                      |
|------------------|---------|--------------------------------------------|
| Avatares / fotos | **PNG** o **JPEG** | PNG si quieres transparencia, JPEG si solo foto |
| Iconos           | PNG o SVG | PNG para bitmap, SVG para escalar sin perder calidad |

- **PNG:** buena calidad, soporta transparencia, algo más pesado.
- **JPEG (JPG):** fotos, menor tamaño, sin transparencia.
- **WebP:** buen equilibrio tamaño/calidad; comprueba soporte en navegadores si lo usas.

Tamaño razonable para avatares: entre 100×100 y 400×400 px.
