# Todo lo sabía · David de Loro

Landing del libro *Todo lo sabía* (Círculo Rojo Editorial, ISBN 979-13-7016975-6). Web estática: un solo `index.html` con el CSS y el JS dentro, sin compilación.

El libro 3D se monta con CSS a partir de sus caras reales (`assets/img/libro/`: portada, contraportada, lomo y canto). Al hacer scroll baja y gira sobre sí mismo entre secciones; cada sección fija su pose en el atributo `data-pose` (giro Y, giro X, giro Z, desplazamiento vertical en vh, escala y brillo rojo del fondo).

## Estructura

```
index.html               La landing
assets/img/libro/        Caras del libro, retrato del autor, render 3/4 e imagen para compartir (og.jpg)
assets/fonts/            Bebas Neue, Caveat, Fraunces cursiva e Inter (autoalojadas)
favicon.png              Iconos
_headers                 Caché de Cloudflare Pages
```

## Ver en local

```bash
python3 -m http.server 8080
```

## Publicar en Cloudflare Pages

Workers & Pages → Create → Pages → Connect to Git → `angelpaesamarketing/todolosabia`.
Production branch `main`, Framework preset **None**, Build command vacío, Build output directory `/`.

## Pendientes

- Botones de compra: buscan por ISBN en Amazon, Fnac, El Corte Inglés y Casa del Libro. Cambiarlos por el enlace directo de cada ficha cuando exista.
- Proyecto educativo: el botón lleva a Instagram @todolosabia; poner un correo o formulario para centros si se prefiere.
- Confirmar los teléfonos de ayuda de la sección de acoso (ANAR 900 20 20 10 y 024).
- Si se usa un dominio propio, cambiar `todolosabia.pages.dev` en `og:image` y en el JSON-LD de `index.html`.
