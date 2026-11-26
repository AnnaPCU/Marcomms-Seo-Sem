# -*- coding: utf-8 -*-
"""
generar_informe_trafico_landings.py — arma el HTML del informe «Tráfico de landings de industrias y programas»
(Control Union, 8 sitios) a partir de informe/trafico_landings.json. Luego:
  python scripts/render_informe.py "Trafico landings industrias y programas - oct 2026.html" --marca cu
  python scripts/auditar_pdf.py "informe/Trafico landings industrias y programas - oct 2026.pdf" --marca cu
"""
import json, os, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
D = json.load(open(os.path.join(ROOT, "informe", "trafico_landings.json"), encoding="utf-8"))
CSS = open(os.path.join(ROOT, "referencia", "style.css"), encoding="utf-8").read() + open(os.path.join(ROOT, "informe", "estilo-ejecutivo.css"), encoding="utf-8").read()
ORDEN = ["northamerica", "espana", "peru", "argentina", "portugal", "brasil", "mexico", "chile"]
S = D["sitios"]; G = D["grupos"]
ROLES = ["home", "nosotros", "industrias (hub)", "programas (hub)", "academy", "vacantes", "contacto", "servicios (hub)", "certificaciones", "gestión de garantías", "inspecciones de commodities"]


def n(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(a, b):
    return f"{100 * a / b:.0f}%"


tot_sitio = sum(s["vistas_mes_sitio"] for s in S.values())
ind_pag = sum(s["industrias"]["paginas"] for s in S.values()); prg_pag = sum(s["programas"]["paginas"] for s in S.values())
ind_tot = sum(s["industrias"]["total_mes"] for s in S.values()); prg_tot = sum(s["programas"]["total_mes"] for s in S.values())
ind_5 = sum(s["industrias"]["5_a_20_mes"] + s["industrias"]["20_o_mas_mes"] for s in S.values())
prg_5 = sum(s["programas"]["5_a_20_mes"] + s["programas"]["20_o_mas_mes"] for s in S.values())
prg_20 = sum(s["programas"]["20_o_mas_mes"] for s in S.values()); ind_20 = sum(s["industrias"]["20_o_mas_mes"] for s in S.values())
ratios = [(s["industrias"]["promedio"] / s["promedio_principales"], s["programas"]["promedio"] / s["promedio_principales"]) for s in S.values()]
rmin = min(min(r) for r in ratios); rmax = max(max(r) for r in ratios)
part_prg = [s["participacion"]["programas"] for s in S.values()]; part_ind = [s["participacion"]["industrias"] for s in S.values()]

H = []
H.append(f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Tráfico de landings · industrias y programas</title>
<style>{CSS}
.site{{ break-inside:avoid; border-top:2.4pt solid var(--navy); padding-top:2.5mm; margin-bottom:5mm; }}
.site h3{{ font-size:12pt; margin-bottom:.5mm; }}
.site .meta{{ font-size:7.4pt; color:var(--grey); margin:0 0 2mm; font-variant-numeric:tabular-nums; }}
.site .meta b{{ color:var(--navy); }}
.site table{{ font-size:7.2pt; table-layout:fixed; }} .site td{{ padding:1.1mm 1.2mm; overflow:hidden; }} .site th{{ padding:1.3mm 1.2mm; font-size:6pt; letter-spacing:.03em; white-space:nowrap; }}
.site td.num{{ padding-left:.5mm; }}
.site .top{{ font-size:7.3pt; line-height:1.4; margin:2mm 0 0; color:var(--ink); }}
.site .top b{{ color:var(--navy); }}
.matrix td, .matrix th{{ padding:1.5mm 1.6mm; font-size:7.6pt; }}
.verdict{{ display:grid; grid-template-columns:34mm 1fr; gap:5mm; padding:2.8mm 0; border-top:.5pt solid var(--hair); break-inside:avoid; }}
.lim{{ margin:0; padding:0 0 0 4mm; font-size:8.3pt; line-height:1.45; }} .lim li{{ margin-bottom:1.6mm; }}
.verdict .lvl{{ font-size:15pt; font-weight:700; color:var(--navy); line-height:1; letter-spacing:-.02em; }}
.verdict .lvl span{{ display:block; font-size:6.6pt; letter-spacing:.14em; text-transform:uppercase; color:var(--grey); font-weight:700; margin-top:1.5mm; }}
.verdict p{{ font-size:8.6pt; line-height:1.46; margin:0; }}
</style></head><body>

<section class="cover">
 <div class="cover-top">
  <p class="kick">Control Union · MarComms · Análisis de tráfico web</p>
  <h1>Tráfico de las landings de industrias y de programas de certificación</h1>
  <div class="cover-meta">
   <div class="c3"><p class="lbl">Sitios</p><p class="val">8 subdominios de controlunion.com</p></div>
   <div class="c3"><p class="lbl">Fuente</p><p class="val">Google Analytics 4 · vistas de página</p></div>
   <div class="c3"><p class="lbl">Período</p><p class="val">1 dic 2025 – 22 oct 2026 ({D['meses']:.1f} meses)</p></div>
   <div class="c3"><p class="lbl">Fecha</p><p class="val">{dt.date.today():%d/%m/%Y} · documento interno</p></div>
  </div>
 </div>
 <div class="cover-body">
  <p class="lede" style="max-width:160mm;margin-bottom:9mm">La pregunta es si vale la pena sumar un formulario de contacto de HubSpot a cada landing de industria y a cada landing de programa de certificación. Para responderla medimos cuánto tráfico recibe cada una frente a las landings principales del sitio (home, nosotros, contacto, servicios, certificaciones, etc.) y frente al resto de las páginas.</p>
  <div class="g">
   <div class="c3 stat"><p class="t">Landings medidas</p><p class="n">{ind_pag + prg_pag}</p><p class="d">{ind_pag} de industrias y {prg_pag} de programas, en idioma local, según el sitemap del 22 oct 2026.</p></div>
   <div class="c3 stat"><p class="t">Una landing típica recibe</p><p class="n">{rmin*100:.0f}<small>–{rmax*100:.0f}%</small></p><p class="d">de lo que recibe una landing principal del mismo sitio. Por página, el tráfico es bajo.</p></div>
   <div class="c3 stat"><p class="t">Programas, en bloque</p><p class="n">{n(prg_tot)}</p><p class="d">vistas/mes en los 8 sitios: entre el {min(part_prg):.0f}% y el {max(part_prg):.0f}% de cada sitio. Medio-alto.</p></div>
   <div class="c3 stat"><p class="t">Industrias, en bloque</p><p class="n">{n(ind_tot)}</p><p class="d">vistas/mes en los 8 sitios: entre el {min(part_ind):.0f}% y el {max(part_ind):.0f}% de cada sitio. Bajo.</p></div>
  </div>
  <div class="hair" style="margin:9mm 0 5mm"></div>
  <div class="g">
   <div class="c4"><p class="kick">Respuesta corta</p><p style="font-size:8.8pt;line-height:1.46">Por landing, bajo: la mitad de las páginas de programas no llega a 2–4 vistas por mes y solo {prg_5} de {prg_pag} superan las 5. En bloque, los programas pesan tanto como la home en varios sitios. Las industrias son bajas en los dos sentidos.</p></div>
   <div class="c4"><p class="kick">Recomendación</p><p style="font-size:8.8pt;line-height:1.46">Formulario en todas las landings de programas si se implementa por plantilla (un cambio cubre las {prg_pag}); si es página por página, solo en las {prg_5} con 5 o más vistas/mes, empezando por las {prg_20} que superan 20. Industrias: por plantilla sí, a mano no.</p></div>
   <div class="c4"><p class="kick">Cómo leer los números</p><p style="font-size:8.8pt;line-height:1.46">Todo está en vistas de página por mes. Cerca del 45% de las vistas no tienen interacción (bots, visitas de segundos); el ranking se mantiene midiendo solo sesiones con interacción, pero los valores absolutos son más chicos.</p></div>
  </div>
 </div>
</section>
""")

# ---- 1. Qué se midió
H.append(f"""<section>
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">01</span> &nbsp; Qué se midió</p><h2>Tres conjuntos de páginas por sitio, misma métrica</h2></div>
 <div class="g">
  <div class="c4 panel-line"><h4>Landings principales</h4><p style="font-size:8.4pt">Las once que estructuran el sitio: home, nosotros, el listado de industrias, el listado de programas, academy, vacantes, contacto, el listado de servicios, certificaciones y verificaciones, gestión de garantías e inspecciones de commodities. No todos los sitios tienen las once (España, Perú, Portugal y México no tienen gestión de garantías). Su promedio es la vara de comparación.</p></div>
  <div class="c4 panel-line"><h4>Landings de industrias y de programas</h4><p style="font-size:8.4pt">Las sublandings que cuelgan de los dos listados, identificadas por el sitemap de cada sitio el 22 oct 2026 (tipos de contenido <code>industry</code> y <code>certi_program</code>). Se cuentan en idioma local; las copias en inglés (<code>/en/</code>) se midieron aparte y no llegan a 1–2 vistas/mes de mediana.</p></div>
  <div class="c4 panel-line"><h4>Resto del sitio</h4><p style="font-size:8.4pt">Todas las demás rutas con tráfico: insights, vacantes individuales, páginas de servicio, gracias, etc. Sirve para saber si industrias y programas están por encima o por debajo de la página típica del sitio.</p></div>
 </div>
 <div class="hair"></div>
 <p style="font-size:8.6pt">Fuente: API de Google Analytics 4, dimensión <code>pagePath</code>, métrica <code>screenPageViews</code>, del 1 dic 2025 (inicio del histórico disponible) al 22 oct 2026. Las vistas se dividen por {D['meses']:.1f} meses para expresarlas por mes. Scripts: <code>ga4_paginas.py</code> (extracción) y <code>analisis_trafico_landings.py</code> (clasificación).</p>
 <h3 style="margin:5mm 0 2.5mm">Landings por sitio</h3>
 <table class="tight"><thead><tr><th>Sitio</th><th class="num">Vistas/mes del sitio</th><th class="num">Rutas con tráfico</th><th class="num">Industrias</th><th class="num">Programas</th><th class="num">Prom. de una principal</th><th class="num">Home</th><th class="num">Contacto</th></tr></thead><tbody>""")
for k in ORDEN:
    s = S[k]; p = s["principales"]
    H.append(f"<tr><td><strong>{s['nombre']}</strong></td><td class='num'>{n(s['vistas_mes_sitio'])}</td><td class='num'>{s['rutas_con_trafico']}</td><td class='num'>{s['industrias']['paginas']}</td><td class='num'>{s['programas']['paginas']}</td><td class='num'>{n(s['promedio_principales'],1)}</td><td class='num'>{n(p['home']['vistas_mes'],1)}</td><td class='num'>{n(p['contacto']['vistas_mes'],1)}</td></tr>")
H.append(f"<tr class='total'><td>8 sitios</td><td class='num'>{n(tot_sitio)}</td><td class='num'>{sum(s['rutas_con_trafico'] for s in S.values())}</td><td class='num'>{ind_pag}</td><td class='num'>{prg_pag}</td><td></td><td></td><td></td></tr></tbody></table>")
H.append("<p class='small' style='margin-top:2mm'>Programas: Perú tiene 57 en el listado del sitio y 56 en el sitemap en español (falta la versión en español de ISO 22000); se midieron 56. Brasil: 42 en portugués de Brasil; el sitemap suma 33 copias <code>/pt-pt/</code> de Portugal que no se cuentan.</p></section>")

# ---- 2. Resumen por grupo
H.append("""<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">02</span> &nbsp; Resultado</p><h2>Por landing es bajo; en bloque, los programas son medio-alto</h2></div>
 <table><thead><tr><th>Grupo · sitio</th><th class="num">Prom. principal</th><th class="num">Industria: prom. / pág.</th><th class="num">mediana</th><th class="num">total /mes</th><th class="num">Programa: prom. / pág.</th><th class="num">mediana</th><th class="num">total /mes</th><th class="num">Ind. ≥5</th><th class="num">Prog. ≥5</th></tr></thead><tbody>""")
for gn, g in G.items():
    H.append(f"<tr class='total'><td>{gn}</td><td class='num'>{n(g['promedio_principales'])}</td><td class='num'>{n(g['industrias']['promedio'],1)}</td><td></td><td class='num'>{n(g['industrias']['total_mes'])}</td><td class='num'>{n(g['programas']['promedio'],1)}</td><td></td><td class='num'>{n(g['programas']['total_mes'])}</td><td class='num'>{g['industrias']['5_o_mas']}/{g['industrias']['paginas']}</td><td class='num'>{g['programas']['5_o_mas']}/{g['programas']['paginas']}</td></tr>")
    for k in g["sitios"]:
        s = S[k]; gi, gp = s["industrias"], s["programas"]
        H.append(f"<tr><td style='padding-left:6mm'><strong>{s['nombre']}</strong></td><td class='num'>{n(s['promedio_principales'])}</td>"
                 f"<td class='num'>{n(gi['promedio'],1)} <span class='small'>({pct(gi['promedio'], s['promedio_principales'])})</span></td><td class='num'>{n(gi['mediana'],1)}</td><td class='num'>{n(gi['total_mes'])}</td>"
                 f"<td class='num'>{n(gp['promedio'],1)} <span class='small'>({pct(gp['promedio'], s['promedio_principales'])})</span></td><td class='num'>{n(gp['mediana'],1)}</td><td class='num'>{n(gp['total_mes'])}</td>"
                 f"<td class='num'>{gi['5_a_20_mes'] + gi['20_o_mas_mes']}/{gi['paginas']}</td><td class='num'>{gp['5_a_20_mes'] + gp['20_o_mas_mes']}/{gp['paginas']}</td></tr>")
H.append("</tbody></table><p class='small' style='margin-top:2mm'>Vistas de página por mes. La fila azul de cada grupo lleva los totales del grupo. Entre paréntesis, el promedio de una landing como porcentaje del promedio de una landing principal del mismo sitio. «≥5»: landings con 5 o más vistas por mes.</p>")

H.append(f"""
 <div class="g" style="margin-top:6mm">
  <div class="c12">
   <div class="verdict"><div class="lvl">Bajo<span>una landing frente a una principal</span></div><p>Una landing de industria o de programa recibe entre el {rmin*100:.0f}% y el {rmax*100:.0f}% de lo que recibe una landing principal del mismo sitio. Frente a la página de contacto, la referencia natural para un formulario, la relación es parecida: Argentina 74 vistas/mes en Contacto contra 5 en un programa típico; Perú 67 contra 8; España 40 contra 6. La mitad de las landings de programas recibe menos de 2 a 4 vistas por mes. De las {prg_pag} landings de programas, {prg_5} superan las 5 vistas/mes y {prg_20} superan las 20; de las {ind_pag} industrias, {ind_5} superan las 5 y {ind_20} las 20.</p></div>
   <div class="verdict"><div class="lvl">Medio-alto<span>los programas, sumados</span></div><p>Las landings de programas pesan entre el {min(part_prg):.0f}% y el {max(part_prg):.0f}% de todas las vistas de cada sitio: {n(prg_tot)} vistas/mes en los 8 sitios. En España los programas juntos reciben {n(S['espana']['programas']['total_mes'])} vistas/mes, más del doble que la home ({n(S['espana']['principales']['home']['vistas_mes'])}); en Perú {n(S['peru']['programas']['total_mes'])} contra una home de {n(S['peru']['principales']['home']['vistas_mes'])}; en Norteamérica {n(S['northamerica']['programas']['total_mes'])} contra {n(S['northamerica']['principales']['home']['vistas_mes'])}.</p></div>
   <div class="verdict"><div class="lvl">Bajo<span>las industrias, sumadas</span></div><p>Las industrias pesan entre el {min(part_ind):.0f}% y el {max(part_ind):.0f}% del sitio: {n(ind_tot)} vistas/mes en total, un cuarto de lo que reciben los programas. Ninguna industria de Brasil, Chile ni Portugal pasa de 6 vistas/mes. Son páginas de navegación, no de intención de compra.</p></div>
   <div class="verdict"><div class="lvl">Medio<span>frente al resto del sitio</span></div><p>Comparadas con las demás páginas (insights, vacantes, servicios), cuya mediana es de 0,5 vistas/mes, las landings de industrias y programas están por encima: no son las páginas olvidadas del sitio. Son medias dentro del sitio y bajas frente a las principales.</p></div>
  </div>
 </div>
</section>""")

# ---- 3. Concentración
top20 = []
for k in ORDEN:
    for grupo, et in (("programas", "Programa"), ("industrias", "Industria")):
        for r, v in S[k][grupo]["top"]:
            if v >= 15:
                top20.append((v, S[k]["nombre"], et, r))
top20.sort(reverse=True)
H.append("""<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">03</span> &nbsp; Concentración</p><h2>Pocas landings cargan casi todo el tráfico</h2></div>
 <div class="g"><div class="c7">
 <table class="tight"><thead><tr><th class="num">Vistas/mes</th><th>Sitio</th><th>Tipo</th><th>Landing</th></tr></thead><tbody>""")
for v, nom, et, r in top20:
    H.append(f"<tr><td class='num'><strong>{n(v,1)}</strong></td><td>{nom}</td><td>{et}</td><td><code>{r.rstrip('/').split('/')[-1]}</code></td></tr>")
H.append(f"""</tbody></table><p class="small" style="margin-top:2mm">Landings de industrias y programas con 15 o más vistas por mes, los 8 sitios.</p></div>
 <div class="c5">
  <p style="font-size:8.8pt;line-height:1.48">Las que mandan son landings de campaña o de programas con demanda real: ISO 27001 en España (la landing de la campaña de Search), Orgánico en Perú, USDA Organic en Norteamérica, ISO 27001 y VISEC en Argentina, Orgánico en México. Sin ellas, el promedio por página de los programas cae a la mitad.</p>
  <p style="font-size:8.8pt;line-height:1.48">Eso tiene dos lecturas. La primera: un formulario en una landing de 2 vistas/mes genera, con suerte, un contacto cada dos años. La segunda: las landings de campaña ya reciben visitas con intención y hoy mandan a la persona a Contacto, donde se pierde el dato de qué programa le interesaba.</p>
  <div class="panel" style="margin-top:4mm"><p class="kick">Distribución de las {prg_pag} landings de programas</p>
  <table class="tight" style="font-size:7.8pt"><tbody>
   <tr><td>Menos de 1 vista/mes</td><td class="num"><strong>{sum(s['programas']['menos_1_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>Entre 1 y 5</td><td class="num"><strong>{sum(s['programas']['1_a_5_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>Entre 5 y 20</td><td class="num"><strong>{sum(s['programas']['5_a_20_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>20 o más</td><td class="num"><strong>{prg_20}</strong></td></tr></tbody></table>
  <p class="kick" style="margin-top:3mm">Las {ind_pag} de industrias</p>
  <table class="tight" style="font-size:7.8pt"><tbody>
   <tr><td>Menos de 1 vista/mes</td><td class="num"><strong>{sum(s['industrias']['menos_1_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>Entre 1 y 5</td><td class="num"><strong>{sum(s['industrias']['1_a_5_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>Entre 5 y 20</td><td class="num"><strong>{sum(s['industrias']['5_a_20_mes'] for s in S.values())}</strong></td></tr>
   <tr><td>20 o más</td><td class="num"><strong>{ind_20}</strong></td></tr></tbody></table></div>
 </div></div>
</section>""")

# ---- 4. Por sitio
H.append("""<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">04</span> &nbsp; Sitio por sitio</p><h2>Industrias y programas frente al resto de cada sitio</h2></div>
 <div class="g">""")


def fila(et, g, part):
    return (f"<tr><td>{et} <span class='small'>({g['paginas']} pág.)</span></td><td class='num'>{n(g['total_mes'])}</td><td class='num'>{n(g['promedio'],1)}</td><td class='num'>{n(g['mediana'],1)}</td>"
            f"<td class='num'>{g['menos_1_mes']}</td><td class='num'>{g['1_a_5_mes']}</td><td class='num'>{g['5_a_20_mes']}</td><td class='num'>{g['20_o_mas_mes']}</td><td class='num'>{part}</td></tr>")


for k in ORDEN:
    s = S[k]; p = s["principales"]; gi, gp, re_ = s["industrias"], s["programas"], s["resto"]
    top_i = " · ".join(f"{r.split('/')[-1]} {n(v,1)}" for r, v in gi["top"][:3])
    top_p = " · ".join(f"{r.split('/')[-1]} {n(v,1)}" for r, v in gp["top"][:3])
    H.append(f"""<div class="c6 site"><h3>{s['nombre']}</h3>
    <p class="meta"><b>{n(s['vistas_mes_sitio'])}</b> vistas/mes · promedio de una principal <b>{n(s['promedio_principales'],1)}</b> · home {n(p['home']['vistas_mes'])} · contacto {n(p['contacto']['vistas_mes'])} · listado de programas {n(p['programas (hub)']['vistas_mes'])}</p>
    <table><thead><tr><th style="width:25mm"></th><th class="num">Total</th><th class="num">Prom.</th><th class="num">Med.</th><th class="num">&lt;1</th><th class="num">1–5</th><th class="num">5–20</th><th class="num">≥20</th><th class="num">%</th></tr></thead><tbody>
    {fila('Industrias', gi, f"{s['participacion']['industrias']:.0f}%")}{fila('Programas', gp, f"{s['participacion']['programas']:.0f}%")}
    <tr><td>Resto <span class='small'>({re_['paginas']} pág.)</span></td><td class='num'></td><td class='num'>{n(re_['promedio'],1)}</td><td class='num'>{n(re_['mediana'],1)}</td><td colspan='5'></td></tr></tbody></table>
    <p class="top"><b>Industrias:</b> {top_i}<br><b>Programas:</b> {top_p}</p></div>""")
H.append("</div><p class='small'>Total, promedio y mediana en vistas por mes. Columnas &lt;1, 1–5, 5–20 y ≥20: cantidad de landings por tramo de vistas por mes. «%»: participación del grupo en todas las vistas del sitio. Top 3 por grupo con sus vistas/mes.</p></section>")

# ---- 5. Matriz de principales
H.append("""<section style="margin-top:8mm">
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">05</span> &nbsp; Referencia</p><h2>Las landings principales, sitio por sitio</h2></div>
 <table class="matrix" style="break-inside:avoid"><thead><tr><th>Landing</th>""" + "".join(f"<th class='num'>{S[k]['nombre']}</th>" for k in ORDEN) + "</tr></thead><tbody>")
for rol in ROLES:
    H.append(f"<tr><td><strong>{rol}</strong></td>" + "".join(f"<td class='num'>{n(S[k]['principales'][rol]['vistas_mes'],1) if rol in S[k]['principales'] else '—'}</td>" for k in ORDEN) + "</tr>")
H.append("<tr class='total'><td>Promedio</td>" + "".join(f"<td class='num'>{n(S[k]['promedio_principales'],1)}</td>" for k in ORDEN) + "</tr>")
H.append("<tr><td>Promedio sin home</td>" + "".join(f"<td class='num'>{n(S[k]['promedio_principales_sin_home'],1)}</td>" for k in ORDEN) + "</tr>")
H.append("<tr><td>Una industria típica (promedio)</td>" + "".join(f"<td class='num'>{n(S[k]['industrias']['promedio'],1)}</td>" for k in ORDEN) + "</tr>")
H.append("<tr><td>Un programa típico (promedio)</td>" + "".join(f"<td class='num'>{n(S[k]['programas']['promedio'],1)}</td>" for k in ORDEN) + "</tr>")
H.append("</tbody></table><p class='small' style='margin-top:2mm'>Vistas de página por mes. «—»: el sitio no tiene esa landing. En Portugal la landing viva de certificaciones es <code>/certificacoes</code>; <code>/service/certification</code> quedó huérfana con 1 vista/mes.</p>")
H.append("<div style='break-inside:avoid'><h3 style='margin:6mm 0 2mm'>Rutas por sitio</h3><table class='tight'><thead><tr><th>Sitio</th><th>Listado de industrias</th><th>Listado de programas</th><th>Contacto</th><th>Certificaciones</th></tr></thead><tbody>")
for k in ORDEN:
    p = S[k]["principales"]
    H.append(f"<tr><td><strong>{S[k]['nombre']}</strong></td><td><code>{p['industrias (hub)']['ruta']}</code></td><td><code>{p['programas (hub)']['ruta']}</code></td><td><code>{p['contacto']['ruta']}</code></td><td><code>{p['certificaciones']['ruta']}</code></td></tr>")
H.append("</tbody></table></div></section>")

# ---- 6. Conclusión
g1, g2, g3 = (G[k]["programas"]["total_mes"] for k in G)
H.append(f"""<section style="margin-top:9mm">
 <div class="sec-head"><div class="rule"></div><p class="kick"><span class="kick-n">06</span> &nbsp; Conclusión</p><h2>Qué hacer con los formularios de HubSpot</h2></div>
 <div class="dec"><div class="g">
  <div class="c3"><p class="dec-num">1</p><h3>Programas: sí, a todos, si va por plantilla</h3></div>
  <div class="c9"><p>En WordPress los programas son un tipo de contenido propio (<code>certi_program</code>). Si el formulario se incorpora a la plantilla, es un solo cambio que cubre las {prg_pag} landings y el costo por página es cero. Con {n(prg_tot)} vistas/mes agregadas y una conversión conservadora del 1–2%, el potencial es de {prg_tot*0.01:.0f} a {prg_tot*0.02:.0f} contactos por mes en los 8 sitios. Para dimensionarlo: en el tercer trimestre de 2026 Control Union midió 600 conversiones web en el trimestre, unas 200 por mes.</p>
  <p>El programa es además el punto de mayor intención: quien llega a «certificación ISO 27001» sabe qué quiere, y hoy lo mandamos a Contacto, donde se pierde el dato de qué programa le interesaba. Un solo formulario de HubSpot con un campo oculto con el nombre del programa resuelve atribución y contacto en un paso. Las landings de campaña (ISO 27001 en España y Argentina, VISEC, Orgánico en Perú y México) lo necesitan primero.</p></div>
 </div></div>
 <div class="dec"><div class="g">
  <div class="c3"><p class="dec-num">2</p><h3>Si es página por página, no en las {prg_pag}</h3></div>
  <div class="c9"><p>Una landing con 2 vistas por mes no justifica trabajo manual. En ese caso la prioridad son las {prg_5} landings de programas con 5 o más vistas/mes, y antes que nada las {prg_20} que superan las 20, que incluyen las landings de campaña. Por grupo: el 1 (Norteamérica, España, Perú) es donde más sentido tiene, con {n(g1)} vistas/mes en programas; el 2 (Argentina, Portugal, Brasil) tiene {n(g2)}, con Argentina cargando casi la mitad; el 3 (México, Chile) {n(g3)}, y Chile tiene una sola landing de programa por encima de 10 vistas/mes.</p></div>
 </div></div>
 <div class="dec"><div class="g">
  <div class="c3"><p class="dec-num">3</p><h3>Industrias: por plantilla sí, a mano no</h3></div>
  <div class="c9"><p>Son páginas de navegación, no de intención, con un cuarto del tráfico de los programas ({n(ind_tot)} vistas/mes en total). Las únicas que justificarían el esfuerzo manual son Forestry en Norteamérica (32/mes), Seguridad alimentaria en España (29), Orgánico y Agri-GAP en Perú (28 y 20) y Huella de carbono en Argentina (23). Las versiones en inglés de los sitios en español y portugués no justifican nada: mediana de 1 vista/mes.</p></div>
 </div></div>
 <div class="hair" style="margin:6mm 0 4mm"></div>
 <p class="kick">Límites de los datos</p>
 <ul class="lim">
  <li>Cerca del 45% de las vistas no tienen interacción (bots, visitas de segundos, revisiones internas). El ranking se rehízo con sesiones con interacción y el orden se mantiene; los valores absolutos son, de mínima, un 40% más chicos.</li>
  <li>Las landings creadas después de diciembre de 2025 están subestimadas: sus vistas se dividen por los {D['meses']:.1f} meses del período completo.</li>
  <li>GA4 no ve el envío de un formulario de HubSpot embebido en iframe. Si se implementan, se miden por las páginas de gracias, como ya está definido para el reporte trimestral.</li>
  <li>El sitemap lista lo publicado; no confirma que Google tenga indexada cada página.</li>
 </ul>
</section>
</body></html>""")

ruta = os.path.join(ROOT, "informe", "Trafico landings industrias y programas - oct 2026.html")
open(ruta, "w", encoding="utf-8").write("\n".join(H))
print("HTML ->", ruta)
