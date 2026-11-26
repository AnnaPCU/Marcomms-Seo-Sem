# -*- coding: utf-8 -*-
"""
generar_mejoras_marca.py — el plan de mejoras partido en dos piezas de marca, cada una con su
identidad completa (logo, tipografía, paleta, tagline) y un gráfico de gasto por campaña:
  informe/mejoras-cu.html   Control Union: España, Portugal, Canadá, Estados Unidos, Argentina + mercados CU
  informe/mejoras-ps.html   Peterson Solutions: Argentina + Iberia
Reutiliza el contenido de generar_mejoras.py (mismos números, ya verificados).
"""
import os, json
import plotly.graph_objects as go
import generar_mejoras as M
from informe_util import n, ars, pct, e, hoy

INF = M.INF
C, U, S, s7 = M.C, M.U, M.S, M.s7
HOY = hoy()


# ------------------------------------------------------------------ gráfico de gasto por campaña
def grafico(unidades, col_gasto, col_fuera, archivo, familia):
    filas = []
    for u in unidades:
        corto = u["nombre"].replace("Control Union ", "").replace("Peterson Solutions ", "")
        for c in u["campanas"]:
            if c["coste"] > 0:
                filas.append((f"{corto} · {c['camp_corta']}", c["coste"], c["desperdicio"]))
    filas = sorted(filas, key=lambda x: x[1])[-12:]
    labels = [f[0] for f in filas]
    fig = go.Figure()
    fig.add_bar(y=labels, x=[f[1] for f in filas], orientation="h", name="Gasto", marker_color=col_gasto,
                text=[f"ARS {int(round(f[1])):,}".replace(",", ".") for f in filas], textposition="outside", textfont=dict(size=15, color="#4f6566"))
    fig.add_bar(y=labels, x=[f[2] for f in filas], orientation="h", name="Fuera de foco (gasto visible)", marker_color=col_fuera)
    fig.update_layout(barmode="overlay", template="simple_white", height=400, width=1000, margin=dict(l=10, r=110, t=10, b=40),
                      font=dict(family=familia, size=15, color="#4f6566"), showlegend=True,
                      legend=dict(orientation="h", y=-0.1, x=0, font=dict(size=14)),
                      xaxis=dict(showgrid=True, gridcolor="#e8ecee", zeroline=False, tickformat=",.0f", title=None, showticklabels=False, range=[0, max(f[1] for f in filas) * 1.28]),
                      yaxis=dict(title=None, tickfont=dict(size=14, color="#1b1e42")))
    ruta = os.path.join(INF, archivo)
    fig.write_image(ruta, format="svg")
    svg = open(ruta, encoding="utf-8").read()
    return svg[svg.index("<svg"):]


def head(logo, doc):
    return f'<div class="brandhead"><img src="{logo}" alt=""><div class="doc">{doc}</div></div>'


def move(i, t, p):
    return f'<div class="move"><div class="num">{i}</div><div><h3>{t}</h3><p>{p}</p></div></div>'


def mercado(p, txt):
    s = S[p]
    return f'<div><h4>{e(p)}</h4><div class="d"><b>{n(s["clics"])} clics orgánicos sin invertir</b>{txt}</div></div>'


# ================================================================== CONTROL UNION
cu_units = [U[k] for k in (("España", "esp"), ("Portugal", "prt"), ("Norteamérica", "can"), ("Norteamérica", "usa"), ("Argentina", "arg"))]
cu_gasto = sum(u["ads"]["gasto"] for u in cu_units); cu_clics = sum(u["ads"]["clics"] for u in cu_units)
cu_conv = sum(u["ads"]["conv"] for u in cu_units); cu_desp = sum(u["ads"]["desperdicio"] for u in cu_units)
cu_mudas = sum(u["ads"]["sin_impr"] for u in cu_units)
cu_chart = grafico(cu_units, "#799495", "#3eb2ed", "grafico-cu.svg", "Calibri")
fo = M.camp(U[("Norteamérica", "can")], "Forestry"); aq = M.camp(U[("Norteamérica", "can")], "Aqua / Fisheries")

cu_cover = f'''<div class="cover">
 {head("../marca/cu/logos/control-union.svg", "Plan de mejoras · campañas de búsqueda<br>Septiembre 2026")}
 <div class="hero">
  <div class="eyebrow">Control Union · España · Portugal · Canadá · Estados Unidos · Argentina</div>
  <h1>Qué está mal en cada campaña y qué se hace con eso</h1>
  <p class="sub">Cinco unidades con inversión, {sum(len(u["campanas"]) for u in cu_units)} campañas de búsqueda. Un pain point por problema y una mejora por pain point, verificados contra Google Ads y Search Console.</p>
  <div class="hero-nums">
   <div><div class="n">{ars(cu_gasto)}</div><div class="l">gasto en seis semanas</div></div>
   <div><div class="n">{n(cu_conv)}</div><div class="l">conversiones</div></div>
   <div><div class="n">{ars(cu_desp)}</div><div class="l">gasto visible fuera de foco</div></div>
   <div><div class="n">{n(cu_mudas)}</div><div class="l">keywords que nunca se activaron</div></div>
  </div>
 </div>
 <div class="top5"><h2>Las cinco mejoras que más pesan</h2>
  {move(1, "Pausar Forestry y Aqua en Canadá", f"{ars(fo['coste'] + aq['coste'])} sobre un sitio sin contenido forestal ni acuícola. El presupuesto pasa a TEMO, que sí tiene página y demanda.")}
  {move(2, "Abrir ISO 45001 en España", f"{n(s7['iso45001_es']['impresiones'])} búsquedas orgánicas con página propia y ninguna keyword. Es la demanda más grande sin comprar.")}
  {move(3, "Negativos a nivel cuenta: consultant, consultoría, advisor", "Control Union certifica, audita, inspecciona y verifica; no asesora. Ya costó ARS 20.951 en un solo término de PrimusGFS.")}
  {move(4, "Corregir FSC: grupo propio en España y Portugal", "La auditoría proponía negativizarlo. Las dos filiales certifican FSC y tienen página; el clic hoy cae en PEFC.")}
  {move(5, "Campaña SMETA en Argentina", "SMETA se compra en España, Portugal y Canadá y no en Argentina, donde multiplicó por 19 sus búsquedas en un año.")}
 </div>
 <p class="foot">Documento interno de Control Union. Fuentes: Google Ads (1 ago – 11 sep 2026) y Search Console (histórico completo). Los números están verificados contra los archivos de origen. Generado el {HOY}.</p>
</div>'''

cu_mercados = f'''<div class="page">
 <div class="chart"><h3>Dónde está el gasto y cuánto de él está fuera de foco</h3>
  <p class="cap">Las doce campañas de mayor inversión, 1 ago – 11 sep 2026. La barra celeste es la porción del gasto visible que va a búsquedas que no corresponden al servicio.</p>{cu_chart}</div>
 <h2 class="sec-title">Donde no se invierte y ya se rinde</h2>
 <p class="sec-sub">Cuatro propiedades de Control Union sin campaña trajeron {n(sum(S[p]["clics_ads"] for p in ("Perú","Brasil","México","Chile")))} clics orgánicos en las seis semanas del informe, más que las cinco unidades con campaña juntas. La mejora es la misma en todas: pauta de defensa chica donde la posición ya está ganada.</p>
 <div class="mk">
  {mercado("Perú", "koa certification, haccp y rainforest alliance (posición 3,4) en primera página. Defensa en exacta sobre esos tres.")}
  {mercado("México", "grs: la mayor demanda de GRS de toda la red, en posición 7,5. Un grupo GRS en exacta.")}
  {mercado("Brasil", "obp, grs y gmp+ en primera página. Extender la campaña GMP+ rehecha cuando exista.")}
  {mercado("Chile", "bap y asc con posición ganada. Todavía sin pauta: primero ordenar la búsqueda de marca.")}
 </div>
 <h2 class="sec-title" style="margin-top:5mm">Orden de ejecución</h2>
 <div class="steps">
  <div><div class="w">Esta semana · sin riesgo</div><h4>Cerrar lo que sobra</h4><ul>
   <li>Negativos de cada unidad, y consultant / consultoría / advisor a nivel cuenta.</li>
   <li>Pausar Forestry y Aqua en Canadá.</li>
   <li>Cortar marca propia de USDA NOP y Textile.</li>
   <li>Limpiar las {n(cu_mudas)} keywords sin impresión.</li></ul></div>
  <div><div class="w">Próximas dos semanas</div><h4>Comprar lo que se busca</h4><ul>
   <li>Exactas donde hoy se entra por variante: IFS, ISO 27001 (ES y AR), GOTS/GRS, CanadaGAP, PrimusGFS, NOP.</li>
   <li>Grupos FSC en España y Portugal. ISO 22000 y FSSC en España.</li>
   <li>Campañas nuevas: ISO 45001 (ES), SMETA (AR), TEMO (CA). GMP+ rehecha en ES y PT.</li>
   <li>recyclass Portugal a exacta con tope; medir 30 días.</li></ul></div>
  <div><div class="w">Requiere decisión</div><h4>Lo que no se resuelve con datos</h4><ul>
   <li>Presupuesto para Perú, México, Brasil y Chile.</li>
   <li>Contenido forestal para Canadá antes de volver a comprar FSC.</li>
   <li>Estado real de la keyword «Usda nop».</li></ul></div>
 </div>
 <div class="navy-box"><h4>Cómo saber si funcionó, en 30 días</h4>
  <p>Desperdicio visible en el informe de términos de búsqueda por debajo del <b>10%</b> (hoy {pct(round(U[("España","esp")]["ads"]["desperdicio"] / U[("España","esp")]["ads"]["visible"] * 100))} en España, {pct(round(U[("Norteamérica","usa")]["ads"]["desperdicio"] / U[("Norteamérica","usa")]["ads"]["visible"] * 100))} en Estados Unidos). Y que ISO 45001, SMETA Argentina y TEMO tengan clics con intención de certificación antes de hablar de conversiones.</p></div>
</div>'''

cu_doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan de mejoras · Control Union</title>
<link rel="stylesheet" href="../marca/cu/estilo-cu.css"></head><body>
{cu_cover}
<div class="page">{M.es}</div>
<div class="page">{M.pt}{M.ar}</div>
<div class="page">{M.ca}{M.us}</div>

{cu_mercados}
</body></html>'''
open(os.path.join(INF, "mejoras-cu.html"), "w", encoding="utf-8").write(cu_doc)

# ================================================================== PETERSON SOLUTIONS
ps_u = U[("Américas", "arg")]; a = ps_u["ads"]
ag = M.camp(ps_u, "Agricultura regenerativa"); hc = M.camp(ps_u, "Huella de carbono / GEI")
ps_chart = grafico([ps_u], "#1b1e42", "#44cbce", "grafico-ps.svg", "Calibri")
ib = S["Iberia"]

ps_cover = f'''<div class="cover">
 {head("../marca/ps/logos/peterson-solutions-color.svg", "Plan de mejoras · campañas de búsqueda<br>Septiembre 2026")}
 <div class="hero">
  <div class="eyebrow">Peterson Solutions · Argentina e Iberia</div>
  <h1>Qué está mal en nuestras campañas y qué hacemos con eso</h1>
  <p class="sub">Ocho campañas de búsqueda en Argentina. Un pain point por problema y una mejora por pain point, para que cada peso acompañe a un cliente que de verdad nos busca.</p>
  <div class="hero-nums">
   <div><div class="n">{ars(a["gasto"])}</div><div class="l">gasto en seis semanas</div></div>
   <div><div class="n">{n(a["clics"])}</div><div class="l">clics</div></div>
   <div><div class="n">{n(a["conv"])}</div><div class="l">conversiones</div></div>
   <div><div class="n">{ars(a["desperdicio"])}</div><div class="l">gasto visible fuera de foco</div></div>
  </div>
 </div>
 <div class="top5"><h2>Las cinco mejoras que más pesan</h2>
  {move(1, "Sacar la amplia de Agricultura regenerativa", f"Una sola keyword trae 219 de los {n(ag['clics'])} clics de la campaña: marcas del agro, agtech y agronomía de nicho. Exactas y negativos.")}
  {move(2, "Cerrar el mercado de bonos de carbono", f"{pct(hc['pct_fuera'])} del gasto visible de Huella de carbono compra otro negocio. Negativos, amplias a frase, y las búsquedas de consultoría ambiental que sí son nuestras.")}
  {move(3, "Huella de agua: vocabulario corporativo", "Hoy el 100% del gasto visible va a tratamiento de efluentes y calculadoras gratis.")}
  {move(4, "Pausar Bioenergía y CeSu", "No hay demanda de servicio con ese vocabulario. Antes de rehacer Bioenergía sobre ISCC hay que definir el corte con Control Union, que ya lo compra.")}
  {move(5, "Páginas en español para Argentina", f"Argentina es el {M.SEO['Américas']['pct_pais']}% de las impresiones del sitio y casi toda la visibilidad está en páginas en inglés. Sin eso, cada campaña compite sola.")}
 </div>
</div>'''

ps_cierre = f'''<div class="page">
 <div class="chart"><h3>Dónde está el gasto y cuánto de él está fuera de foco</h3>
  <p class="cap">Las ocho campañas, 1 ago – 11 sep 2026. La barra aqua es la porción del gasto visible que va a búsquedas que no corresponden al servicio.</p>{ps_chart}</div>
 <h2 class="sec-title">Iberia: demanda sin campaña</h2>
 <p class="sec-sub">El sitio de Iberia trajo {n(ib["clics"])} clics orgánicos en el histórico sin un peso de pauta. csrd (1.456 impresiones, posición 21,5), cbam services (posición 28,6) y finanzas sostenibles (25,4) tienen página y están en página dos y tres de Google. Es nuestro territorio, no el de Control Union: primero contenido para llevar esas páginas a primera página, después una campaña propia.</p>
 <h2 class="sec-title" style="margin-top:8mm">Orden de ejecución</h2>
 <div class="steps">
  <div><div class="w">Esta semana · sin riesgo</div><h4>Cerrar lo que sobra</h4><ul>
   <li>Negativos de Agricultura regenerativa, Huella de carbono, ESG y Huella de agua.</li>
   <li>Eliminar la amplia «agricultura regenerativa en argentina» y «gestion del agua industrial».</li>
   <li>Limpiar las {n(a["sin_impr"])} keywords sin impresión.</li></ul></div>
  <div><div class="w">Próximas dos semanas</div><h4>Comprar lo que sí es nuestro</h4><ul>
   <li>Exactas: [agricultura regenerativa], [ganadería regenerativa argentina], [consultoria ambiental], [iso 14064], [csrd], [estandar gri], [consultora esg], [huella hidrica corporativa].</li>
   <li>Amplias de Huella de carbono a frase.</li></ul></div>
  <div><div class="w">Requiere decisión</div><h4>Lo que no se resuelve con datos</h4><ul>
   <li>Pausar Bioenergía y CeSu.</li>
   <li>Corte de marca en ISCC con Control Union.</li>
   <li>Páginas en español para los cinco servicios que se pagan.</li></ul></div>
 </div>
 <div class="navy-box"><h4>Cómo sabremos si funcionó, en 30 días</h4>
  <p>Desperdicio visible por debajo del <b>10%</b> (hoy {pct(round(a["desperdicio"] / a["visible"] * 100))}). Y que los clics que queden vengan de búsquedas de servicio, no de definiciones ni de otros negocios: con {n(a["conv"])} conversiones en seis semanas, la conversión todavía no nos dice nada.</p></div>
 <p class="foot">Documento interno de Peterson Solutions. Fuentes: Google Ads (1 ago – 11 sep 2026) y Search Console (histórico completo). Los números están verificados contra los archivos de origen. Generado el {HOY}.</p>
</div>'''

ps_doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan de mejoras · Peterson Solutions</title>
<link rel="stylesheet" href="../marca/ps/estilo-ps.css"></head><body>
{ps_cover}
<div class="page">{M.ps}</div>
{ps_cierre}
</body></html>'''
open(os.path.join(INF, "mejoras-ps.html"), "w", encoding="utf-8").write(ps_doc)
print("-> informe/mejoras-cu.html, informe/mejoras-ps.html")
