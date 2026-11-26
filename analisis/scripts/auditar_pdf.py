# -*- coding: utf-8 -*-
"""
auditar_pdf.py — rasteriza cada página del PDF y cuenta píxeles de los tres colores
de marca prohibidos en piezas internas (CLAUDE.md §8):
  Cyan  #3eb2ed (Control Union)
  Aqua  #44cbce (Peterson Solutions)
  Yellow #f1e747 (Peterson Solutions)
Cuenta coincidencia exacta y también una banda de tolerancia (±12 por canal) por si
el antialiasing genera tonos vecinos. Además lista los colores más frecuentes.
"""
import sys, pathlib
from collections import Counter
import pymupdf
from PIL import Image

PROHIBIDOS = {"Cyan CU #3eb2ed": (0x3e, 0xb2, 0xed),
              "Aqua PS #44cbce": (0x44, 0xcb, 0xce),
              "Yellow PS #f1e747": (0xf1, 0xe7, 0x47)}
TOL = 12

pdf = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "informe/informe.pdf")
# pieza de una sola marca: se permite su color y se prohíben los de la otra
if "--marca" in sys.argv:
    marca = sys.argv[sys.argv.index("--marca") + 1]
    if marca == "cu":
        PROHIBIDOS = {k: v for k, v in PROHIBIDOS.items() if k.startswith("Aqua") or k.startswith("Yellow")}
    elif marca == "ps":
        PROHIBIDOS = {k: v for k, v in PROHIBIDOS.items() if k.startswith("Cyan")}
doc = pymupdf.open(pdf)
exacto = Counter(); banda = Counter(); paleta = Counter(); total = 0
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=110, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = img.getdata()
    total += len(px)
    c = Counter(px)
    paleta.update(c)
    for nombre, (r, g, b) in PROHIBIDOS.items():
        exacto[nombre] += c.get((r, g, b), 0)
        banda[nombre] += sum(n for (pr, pg, pb), n in c.items()
                             if abs(pr - r) <= TOL and abs(pg - g) <= TOL and abs(pb - b) <= TOL)
print(f"{pdf.name}: {len(doc)} páginas, {total:,} píxeles analizados a 110 dpi")
ok = True
for nombre in PROHIBIDOS:
    print(f"  {nombre:<20} exacto={exacto[nombre]:>6}   banda ±{TOL}={banda[nombre]:>6}")
    ok &= exacto[nombre] == 0 and banda[nombre] == 0
print("\nColores más frecuentes:")
for (r, g, b), n in paleta.most_common(12):
    print(f"  #{r:02x}{g:02x}{b:02x}  {n / total * 100:6.2f}%")
print("\nRESULTADO:", "OK — cero píxeles de colores de marca" if ok else "FALLA — hay color de marca")
sys.exit(0 if ok else 1)
