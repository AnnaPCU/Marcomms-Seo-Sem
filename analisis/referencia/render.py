from playwright.sync_api import sync_playwright
import pathlib
src = pathlib.Path('informe.html').resolve().as_uri()
foot = """
<div style="width:100%;font-family:Carlito,Calibri,sans-serif;font-size:7pt;color:#799495;
     padding:0 16mm;display:flex;justify-content:space-between;align-items:center;
     border-top:.5pt solid #d7dee0;padding-top:2mm;-webkit-print-color-adjust:exact;">
  <span style="letter-spacing:.12em;text-transform:uppercase;font-size:6.2pt;">
    Search Console × Google Ads · Documento interno</span>
  <span style="color:#1b1e42;font-weight:700;"><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>"""
blank = "<div></div>"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page()
    pg.goto(src, wait_until="networkidle")
    pg.pdf(path="informe.pdf", format="A4", print_background=True,
           display_header_footer=True, header_template=blank, footer_template=foot,
           margin={"top":"17mm","bottom":"20mm","left":"16mm","right":"16mm"})
    b.close()
print("listo")
