#!/usr/bin/env python3
"""Genera ghl/landing-ghl.html a partir de index.html: un solo bloque para pegar en un
elemento Custom Code de GoHighLevel.

- Todos los selectores quedan dentro de .tls (GHL usa clases como .btn o .container).
- Imágenes y fuentes con URL absoluta a Cloudflare Pages (las fuentes necesitan el CORS de _headers).
- El bloque rompe el ancho de la sección de GHL y quita su padding y su fondo.
- El libro fijo y el grano se recortan al borde de la landing, y la cabecera se oculta cuando
  la landing sale de pantalla, para no tapar otras secciones de la página de GHL.

Uso: python3 ghl/build.py   (volver a ejecutarlo después de cambiar index.html)
"""
import re
from pathlib import Path

BASE = 'https://todolosabia.pages.dev'
ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'index.html').read_text()

css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
body = re.search(r'<body>(.*?)</body>', src, re.S).group(1).strip()
ld = re.search(r'<script type="application/ld\+json">.*?</script>', src, re.S).group(0)


def scope(sel):
    sel = sel.strip()
    if sel.startswith('html'):
        return sel
    if sel in (':root', 'body'):
        return '.tls'
    if sel.startswith('body'):
        return '.tls' + sel[len('body'):]
    return '.tls ' + sel


def prefix(text):
    """Antepone .tls a cada selector; respeta @media y deja intactos @font-face y @keyframes."""
    out, i = [], 0
    while i < len(text):
        j = text.find('{', i)
        if j < 0:
            out.append(text[i:]); break
        head = text[i:j].strip()
        depth, k = 1, j + 1
        while depth:
            depth += {'{': 1, '}': -1}.get(text[k], 0); k += 1
        inner = text[j + 1:k - 1]
        if head.startswith('@media') or head.startswith('@supports'):
            out.append(head + '{' + prefix(inner) + '}')
        elif head.startswith('@'):
            out.append(head + '{' + inner + '}')
        else:
            out.append(','.join(scope(s) for s in head.split(',')) + '{' + inner + '}')
        i = k
    return '\n'.join(out)


css = css.replace('url("/assets/', f'url("{BASE}/assets/')
css = css.replace('html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;background:var(--ink)}', 'html{scroll-behavior:smooth}')
css = prefix(css)
css += '''
/* GoHighLevel: ancho completo, sin el padding ni el fondo blanco de la sección */
html,body{background:#0B0A09!important;overflow-x:clip}
.tls{position:relative;isolation:isolate;display:block;width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;padding:0!important;text-align:left}
body :has(> .tls){padding-left:0!important;padding-right:0!important;background:transparent!important;max-width:none!important;border:0!important;box-shadow:none!important}
.tls::before,.tls::after,.tls .stage,.tls .dots{clip-path:inset(var(--ct,0px) 0 var(--cb,0px) 0)}
.tls.out::before,.tls.out::after,.tls.out .stage,.tls.out .bar,.tls.out .dots{visibility:hidden}'''

body = body.replace('src="/assets/', f'src="{BASE}/assets/')
assert '="/' not in body, 'quedan rutas relativas a la raíz'

# El JS busca solo dentro de la landing y la apaga cuando sale de pantalla
js_old = "  const $ = (s, c = document) => c.querySelector(s);\n  const $$ = (s, c = document) => [...c.querySelectorAll(s)];"
js_new = ("  const root = document.getElementById('tls');\n"
          "  if (!root || root.dataset.on) return; root.dataset.on = '1';\n"
          "  // Las secciones y filas de GHL que contienen la landing pierden padding, fondo y transform (rompería el libro fijo)\n"
          "  for (let el = root.parentElement, n = 0; el && el !== document.body && n < 8; el = el.parentElement, n++) {\n"
          "    for (const p of ['padding-left', 'padding-right', 'padding-top', 'padding-bottom']) el.style.setProperty(p, '0', 'important');\n"
          "    el.style.setProperty('max-width', 'none', 'important');\n"
          "    el.style.setProperty('background-color', 'transparent', 'important');\n"
          "    el.style.setProperty('transform', 'none', 'important');\n"
          "  }\n"
          "  const $ = (s, c = root) => c.querySelector(s);\n"
          "  const $$ = (s, c = root) => [...c.querySelectorAll(s)];")
assert body.count(js_old) == 1
body = body.replace(js_old, js_new)
frame_old = "    const sy = scrollY;\n"
frame_new = ("    const sy = scrollY;\n"
             "    const rr = root.getBoundingClientRect();\n"
             "    root.classList.toggle('out', rr.bottom < 0 || rr.top > innerHeight);\n"
             "    // El libro y el fondo fijos se recortan al borde de la landing (no tapan las secciones de GHL)\n"
             "    root.style.setProperty('--ct', Math.max(0, rr.top) + 'px');\n"
             "    root.style.setProperty('--cb', Math.max(0, innerHeight - rr.bottom) + 'px');\n")
assert body.count(frame_old) == 1
body = body.replace(frame_old, frame_new)

out = f'''<!-- Todo lo sabía · landing para GoHighLevel (elemento Custom Code).
     Generado con ghl/build.py a partir de index.html: no editar a mano. -->
<style>
{css}
</style>
{ld}
<div class="tls" id="tls">
{body}
</div>
'''
(ROOT / 'ghl' / 'landing-ghl.html').write_text(out)
print('ghl/landing-ghl.html', len(out), 'bytes')
