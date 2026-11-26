# -*- coding: utf-8 -*-
"""render_informe.py — HTML -> PDF con Playwright/Chromium.
uso: python render_informe.py [archivo.html] ["texto del pie"] [--marca cu|ps]

Sin --marca: pie neutro (texto + numeración), como referencia/render.py.
--marca cu : barra celeste superior a todo el ancho (dispositivo gráfico 1 del Style Guide), tagline
             THE PROOF TO YOUR PROMISE al pie y barra azul inferior desde la derecha (dispositivo 2).
--marca ps : tagline «For the world, for ourselves, for our families» al pie, con acento aqua."""
import pathlib, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
INF = HERE.parent / "informe"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
marca = sys.argv[sys.argv.index("--marca") + 1] if "--marca" in sys.argv else None
html = INF / (args[0] if args else "informe.html")
pie = args[1] if len(args) > 1 else "Search Console · Histórico y móvil · Documento interno"
pdf = html.with_suffix(".pdf")
BASE = "font-family:Carlito,Calibri,sans-serif;-webkit-print-color-adjust:exact;"

if marca == "cu":
    header = f'<div style="width:100%;height:4.5mm;background:#3eb2ed;{BASE}"></div>'
    footer = f"""<div style="width:100%;{BASE}padding:0 15mm;">
  <div style="display:flex;justify-content:space-between;align-items:center;font-size:7pt;color:#799495;">
   <span style="letter-spacing:.2em;text-transform:uppercase;font-size:7pt;color:#1b1e42;font-weight:700;">The proof to your promise</span>
   <span style="color:#1b1e42;font-weight:700;"><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>
  <div style="margin:2.5mm 0 0 auto;width:70mm;height:2.8mm;background:#1b1e42;"></div></div>"""
    margin = {"top": "22mm", "bottom": "22mm", "left": "15mm", "right": "15mm"}
elif marca == "ps":
    header = "<div></div>"
    footer = f"""<div style="width:100%;{BASE}padding:0 15mm;display:flex;justify-content:space-between;align-items:center;
     font-size:7pt;color:#799495;border-top:1.2pt solid #44cbce;padding-top:2.5mm;">
   <span style="font-size:7.4pt;color:#1b1e42;font-weight:700;">For the world, for ourselves, for our families</span>
   <span style="color:#1b1e42;font-weight:700;"><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>"""
    margin = {"top": "20mm", "bottom": "22mm", "left": "15mm", "right": "15mm"}
else:
    header = "<div></div>"
    footer = f"""<div style="width:100%;{BASE}font-size:7pt;color:#799495;padding:0 16mm;display:flex;justify-content:space-between;
     align-items:center;border-top:.5pt solid #d7dee0;padding-top:2mm;">
  <span style="letter-spacing:.12em;text-transform:uppercase;font-size:6.2pt;">{pie}</span>
  <span style="color:#1b1e42;font-weight:700;"><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>"""
    margin = {"top": "17mm", "bottom": "20mm", "left": "16mm", "right": "16mm"}

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page()
    pg.goto(html.resolve().as_uri(), wait_until="networkidle")
    pg.pdf(path=str(pdf), format="A4", print_background=True, display_header_footer=True,
           header_template=header, footer_template=footer, margin=margin)
    b.close()
print("PDF ->", pdf)
