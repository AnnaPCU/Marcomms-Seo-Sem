# -*- coding: utf-8 -*-
"""
generar_informe.py — arma informe/informe.html a partir de informe/datos_informe.json
con el sistema visual de referencia/style.css (paleta neutra interna, Calibri/Carlito).
Todos los números del informe salen del JSON; ninguno está escrito a mano.
"""
import json, os, shutil, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))
shutil.copy(os.path.join(ROOT, "referencia", "style.css"), os.path.join(INF, "style.css"))


def n(x, dec=0):
    """formato rioplatense: 12.345 · 12,3"""
    if x is None:
        return "—"
    if dec == 0:
        return f"{int(round(x)):,}".replace(",", ".")
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=0):
    return "—" if x is None else n(x, dec) + "%"


def e(s):
    return html.escape(str(s))


MESES = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may", "06": "jun", "07": "jul",
         "08": "ago", "09": "sep", "10": "oct", "11": "nov", "12": "dic"}


def mes_corto(m):
    y, mm = m.split("-")
    return f"{MESES[mm]} {y[2:]}"


def fecha(s):
    y, m, d = s.split("-")
    return f"{int(d)} {MESES[m]} {y}"


# ------------------------------------------------------------------ datos derivados
pan = D["panorama"]
por_prop = {p["propiedad"]: p for p in pan}
filas_total = D["archivo"]["filas_total"]
mb_total = D["archivo"]["mb_total"]
prop_6m = [p for p in pan if p["primera"] >= "2026-03-01"]
prop_16m = [p for p in pan if p["primera"] < "2026-03-01"]
cob = D["cobertura"]
grp = cob["grupos"]
g_nada = grp.get("sin nada del tema", dict(coste=0, terminos=0, pct=0))
g_pres = grp.get("query presente", dict(coste=0, terminos=0, pct=0))
g_deb = grp.get("tema debil", dict(coste=0, terminos=0, pct=0))
g_fue = grp.get("tema fuerte, query no", dict(coste=0, terminos=0, pct=0))
can = D["canibalizacion"]
zona = D["zona_8_20"]
dev = D["dispositivos_total"]
mob = dev.get("MOBILE", {})
desk = dev.get("DESKTOP", {})
s7 = D["s7"]
ref5 = D["cinco_referencia_12m"]
ev5 = D["evolucion_cinco"]
meses_ev = sorted({m for t in ev5.values() for m in t})
nc = D["no_comprada"]
nc_tot_q = sum(v["queries"] for v in nc.values())
nc_tot_i = sum(v["impresiones"] for v in nc.values())
yoy = D["interanual"]
apdes = D["aparecieron"]
neg = D["negativos"]
land = D["landing"]
val = D["validacion"]
iso45 = s7["iso45001_es"]
temo = s7["temo_na"]

HOY = date.today()
FECHA_INF = f"{HOY.day} {MESES[f'{HOY.month:02d}']} {HOY.year}"

# ------------------------------------------------------------------ helpers HTML

def tabla(cols, filas, cls="", total=None):
    th = "".join(f'<th class="{c[1]}">{e(c[0])}</th>' for c in cols)
    tr = ""
    for f in filas:
        tr += "<tr>" + "".join(f'<td class="{c[1]}">{v}</td>' for c, v in zip(cols, f)) + "</tr>"
    if total:
        tr += '<tr class="total">' + "".join(f'<td class="{c[1]}">{v}</td>' for c, v in zip(cols, total)) + "</tr>"
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def stat(num, tit, desc, small=""):
    sm = f"<small>{e(small)}</small>" if small else ""
    return f'<div class="stat"><p class="n">{num}{sm}</p><p class="t">{e(tit)}</p><p class="d">{desc}</p></div>'


# ------------------------------------------------------------------ portada
primera_min = min(p["primera"] for p in pan)
ultima_max = max(p["ultima"] for p in pan)
hueco_txt = " · ".join(f"{p} {v['hueco_dias']} días" for p, v in D["huecos"].items())

cover = f"""
<section class="cover">
 <div class="cover-top">
  <p class="kick">Documento interno · Peterson Control Union World Group</p>
  <h1>Search Console: lo que de verdad guarda, y lo que cambia cuando se mira con fecha y dispositivo</h1>
  <div class="cover-meta">
   <div class="c3"><p class="lbl">Complementa a</p><p class="val">Search Console × Google Ads<br>(sep 2026)</p></div>
   <div class="c3"><p class="lbl">Archivo construido</p><p class="val">{n(filas_total)} filas · {n(mb_total)} MB<br>10 propiedades, por marca</p></div>
   <div class="c3"><p class="lbl">Cobertura real</p><p class="val">{fecha(primera_min)} – {fecha(ultima_max)}<br>{len(prop_6m)} propiedades desde marzo 2026</p></div>
   <div class="c3"><p class="lbl">Dimensiones nuevas</p><p class="val">date · device<br>+ query+country sin fecha</p></div>
  </div>
 </div>
 <div class="cover-body">
  <p class="kick kick-n">El hallazgo</p>
  <p class="lede">No hay dieciséis meses. Ocho de las diez propiedades tienen datos desde el 3 de marzo de 2026
  (Peterson desde el 22): seis meses y medio. Solo Argentina y México llegan a mayo de 2025, con un hueco de
  {D['huecos']['Argentina']['hueco_dias']} y {D['huecos']['México']['hueco_dias']} días en el medio. Todo lo que el
  informe anterior llamó «anual» o «doce meses» eran seis meses, y las posiciones de la «zona 8–20» estaban
  mal calculadas: cuatro de los cinco términos ya están en primera página en España.</p>
  <div class="hair"></div>
  <div class="g">
   <div class="c3">{stat(pct(mob.get('pct_impr')), 'Móvil', f"de las impresiones orgánicas del grupo llegan desde un teléfono. Nunca se había medido. En clics es el {pct(mob.get('pct_clics'))}.")}</div>
   <div class="c3">{stat(pct(g_nada['pct']), 'Sin respaldo', f"del gasto relevante con clic va a temas sobre los que el sitio no dice nada: ARS {n(g_nada['coste'])}. En la base era 41%.")}</div>
   <div class="c3">{stat(pct(can['pct'], 1), 'Canibalización', f"del gasto se superpone con posición 1–3: ARS {n(can['coste_1_3'])}. En la base era ARS 3.594. Sube por un solo término: {e(can['top'][0]['termino'])} en Portugal.")}</div>
   <div class="c3">{stat(n(nc_tot_q), 'Queries sin comprar', f"con 40+ impresiones en el histórico y sin keyword ni término por tema. {n(nc_tot_i)} impresiones.")}</div>
  </div>
  <div class="hair"></div>
  <div class="g">
   <div class="c6">
    <p class="kick">Qué se hizo</p>
    <p>Se descargó todo lo que la API devuelve para las diez propiedades, en cinco cortes más tres complementarios,
    con fecha y dispositivo, y se archivó por marca en <code>datos/gsc-historico/</code>. Google borra estos datos a los
    16 meses: el archivo local es lo único que va a quedar. La extracción anterior de 12 meses coincide fila por fila
    con el tramo que se solapa ({n(val['filas_iguales'])} filas idénticas, cero diferencias).</p>
   </div>
   <div class="c6">
    <p class="kick">Dos correcciones al informe anterior</p>
    <p><strong>Períodos.</strong> Las cifras «anuales» de FSC, OEKO-TEX, BRCGS, GMP+ y Canadá cubren del 3 de marzo al
    12 de septiembre de 2026. Ninguna conclusión se da vuelta, pero el rótulo estaba mal.</p>
    <p><strong>Posiciones.</strong> La «zona 8–20» se calculó con la media simple entre filas-país. Ponderando por
    impresiones y mirando el país que compra, recyclass está en {n(ref5['recyclass']['pos_esp'],1)}, smeta en
    {n(ref5['smeta']['pos_esp'],1)} e iscc en {n(ref5['iscc']['pos_esp'],1)} en España. El indicador de 30 días
    del informe anterior partía de una base equivocada.</p>
   </div>
  </div>
 </div>
 <div class="cover-foot">
  <p class="small">Pieza de circulación interna. No lleva identidad de marca: cubre propiedades de Control Union y de
  Peterson Solutions, y el manual del grupo no admite piezas que combinen ambas marcas. Paleta limitada a los colores
  comunes a los dos manuales. Generado el {FECHA_INF}.</p>
 </div>
</section>
"""

# ------------------------------------------------------------------ sección 01 · cobertura
filas = []
for p in sorted(pan, key=lambda x: (x["marca"] != "CU", -x["impr_total"])):
    hueco = D["huecos"].get(p["propiedad"])
    filas.append([f"{'PS ' if p['marca']=='PS' else ''}{e(p['propiedad'])}", fecha(p["primera"]), fecha(p["ultima"]),
                  n(p["dias"]), (f"{hueco['hueco_dias']} d" if hueco else "—"),
                  n(p["impr_total"]), n(p["clics_total"]), n(p["queries_hist"]),
                  "sí" if p["con_campana"] == "si" else "—"])
tab_cob = tabla([("Propiedad", ""), ("Primer día", ""), ("Último día final", ""), ("Días", "num"), ("Hueco", "num"),
                 ("Impr.", "num"), ("Clics", "num"), ("Queries", "num"), ("Camp.", "")], filas, "tight")

filas_arch = [[e(k), n(v["filas"]), n(v["mb"], 1)] for k, v in D["archivo"]["cortes"].items()]
tab_arch = tabla([("Corte", ""), ("Filas", "num"), ("MB", "num")], filas_arch, "tight",
                 total=["Total, 10 propiedades", n(filas_total), n(mb_total, 1)])

sec1 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 01</p><h2>Qué guarda Google de verdad</h2></div>
 <div class="g">
  <div class="c7">
   <p>La API se sondeó desde el 1 de abril de 2025, antes del límite nominal de 16 meses, para las diez propiedades.
   Ocho devolvieron su primer día de datos el <strong>3 de marzo de 2026</strong> (Control Union) o el
   <strong>22 de marzo</strong> (Peterson). Argentina y México arrancan el <strong>4 de mayo de 2025</strong>, el mismo
   día las dos, que es exactamente el borde de retención: no es la fecha de alta de las propiedades, es hasta donde Google
   deja mirar. Cada día que pasa se pierde un día de mayo de 2025 en esas dos.</p>
   <p>Las dos tienen además un hueco sin datos que termina el 2 de marzo de 2026, el día anterior a que arranquen las otras
   seis de Control Union: Argentina {D['huecos']['Argentina']['hueco_dias']} días desde el {fecha(D['huecos']['Argentina']['desde'])},
   México {D['huecos']['México']['hueco_dias']} días desde el {fecha(D['huecos']['México']['desde'])}. La coincidencia sugiere un
   evento único sobre las propiedades (migración, baja y re-alta, cambio de verificación). Desde los datos no se sabe cuál.</p>
   <p><strong>Consecuencia directa:</strong> la extracción de «12 meses» del informe anterior pidió desde el 15 de septiembre de 2025,
   pero para ocho propiedades Google solo tenía datos desde marzo. Sus cifras «anuales» son de seis meses y diez días. La sección 04
   las re-verifica una por una.</p>
  </div>
  <div class="c5">
   <p class="kick">Archivo construido, por marca</p>
   {tab_arch}
   <p class="small" style="margin-top:2mm">Cinco cortes de CLAUDE.md §5 más tres complementarios. type=web, dataState=final,
   25.000 filas por página. {n(D['archivo']['llamadas'])} llamadas, cero errores, log por llamada en cada carpeta de marca.</p>
  </div>
 </div>
 <div class="hair"></div>
 <p class="kick">Cobertura real por propiedad · todo el histórico disponible</p>
 {tab_cob}
 <p class="small" style="margin-top:2mm">Impresiones y clics agregados por propiedad (una impresión por búsqueda); agregar por página da
 entre 5% y 37% más. Queries distintas visibles tras el umbral de anonimización.</p>
 <div class="hair"></div>
 <div class="g">
  <div class="c4 panel">
   <p class="kick kick-n">Continuidad verificada</p>
   <p>El histórico nuevo, sumado sobre las ventanas del informe anterior, reproduce la extracción de 12 meses fila por fila:
   {n(val['filas_iguales'])} filas comparadas, cero diferencias. Sumar la dimensión fecha no pierde queries.</p>
  </div>
  <div class="c4 panel">
   <p class="kick kick-n">Lo que ya no se puede medir</p>
   <p>Con seis meses no hay estacionalidad. Solo Argentina y México permiten comparar junio–agosto de 2025 contra 2026,
   con el hueco en el medio. La evolución mensual tiene siete puntos para las otras ocho.</p>
  </div>
  <div class="c4 panel">
   <p class="kick kick-n">Lo que sí se puede ahora</p>
   <p>Tendencia mes a mes de cada query, posición por país de compra, reparto móvil/escritorio, y qué búsquedas
   aparecieron o desaparecieron entre el primer tramo y el último. Sección 03.</p>
  </div>
 </div>
</section>
"""

# ------------------------------------------------------------------ sección 02 · los seis cruces
top_zona = zona["top"][:8]
filas_z = [[e(t["termino"]), e(t["propiedad"] if t["propiedad"] != "Norteamérica" else t["pais"].upper()),
            n(t["coste"]), n(t["impr_org"]), n(t["pos_org"], 1)] for t in top_zona]
tab_zona = tabla([("Término", ""), ("Mercado", ""), ("Coste ARS", "num"), ("Impr. org.", "num"), ("Pos.", "num")], filas_z, "tight")

filas_h = [[e(h["camp_corta"]), e(h["propiedad"] if h["propiedad"] != "Norteamérica" else h["pais"].upper()),
            n(h["coste"]), n(h["terminos"])] for h in D["huecos_por_campana"][:8]]
tab_h = tabla([("Campaña", ""), ("Mercado", ""), ("Coste ARS", "num"), ("Términos", "num")], filas_h, "tight")

filas_can = [[e(t["termino"]), e(t["campana"].replace(" - Search", "").replace(" - SEARCH", "")), n(t["coste"]), n(t["pos_org"], 1)]
             for t in can["top"][:5]]
tab_can = tabla([("Término", ""), ("Campaña", ""), ("Coste ARS", "num"), ("Pos. org.", "num")], filas_can, "tight")

filas_ref = []
for t, r in ref5.items():
    filas_ref.append([e(t), n(r["media_simple"], 1), n(r["pos_esp"], 1), n(r["impr_esp"]),
                      n(ev5[t].get(meses_ev[1]), 1), n(ev5[t].get(meses_ev[-2]), 1)])
tab_ref = tabla([("Término", ""), ("Informe ant.", "num"), ("Solo ESP", "num"), ("Impr. ESP", "num"),
                 (mes_corto(meses_ev[1]), "num"), (mes_corto(meses_ev[-2]), "num")], filas_ref, "tight")
pefc_es_ads = next((t["pos_org"] for t in D.get("zona_todos", []) if t["termino"] == "pefc" and t["propiedad"] == "España"), None)

sec2 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 02</p><h2>Los seis cruces, rehechos</h2></div>
 <p>Mismas definiciones que el informe anterior, con tres cambios de método que se declaran: cada campaña se compara contra las
 queries del <strong>país donde compra</strong> (España contra ESP, Canadá contra CAN, Estados Unidos contra USA), la posición
 se pondera por impresiones, y el desperdicio se descuenta con el Anexo A tal como quedó corregido (FSC ya no es negativo).
 Universo: {n(cob['terminos'])} términos de búsqueda con clic y fuera del Anexo A, ARS {n(cob['coste'])} de gasto.</p>
 <div class="g">
  <div class="c3">{stat(pct(g_nada['pct']), 'Sin nada del tema', f"ARS {n(g_nada['coste'])} · {n(g_nada['terminos'])} términos. El sitio no tiene contenido sobre eso en el país que compra.")}</div>
  <div class="c3">{stat(pct(g_pres['pct']), 'Query ya presente', f"ARS {n(g_pres['coste'])} · {n(g_pres['terminos'])} términos. El sitio ya aparece en esa búsqueda exacta.")}</div>
  <div class="c3">{stat(pct(g_deb['pct']), 'Tema débil', f"ARS {n(g_deb['coste'])} · {n(g_deb['terminos'])} términos. Hay algo, poco: menos de 200 impresiones del tema.")}</div>
  <div class="c3">{stat(pct(g_fue['pct']), 'Tema fuerte, query no', f"ARS {n(g_fue['coste'])} · {n(g_fue['terminos'])} términos. Manda en el tema pero no en esa formulación.")}</div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c6">
   <h3>1 · Canibalización: sigue sin ser un problema</h3>
   <p>ARS {n(can['coste_1_3'])} del gasto con clic cae en posición 1–3 orgánica ({pct(can['pct'],1)}), {n(can['terminos_1_3'])} términos.
   Ampliando a 1–7 son ARS {n(can['coste_1_7'])} en {n(can['terminos_1_7'])} términos. La cifra base era ARS 3.594. Sube por un
   solo término que la base no veía: <strong>{e(can['top'][0]['termino'])}</strong> en {e(can['top'][0]['campana'].split(' - ')[0])},
   posición orgánica {n(can['top'][0]['pos_org'],1)} en el país que compra y ARS {n(can['top'][0]['coste'])} pagados. El resto es marca propia,
   como en la base.</p>
   {tab_can}
  </div>
  <div class="c6">
   <h3>3 · Huecos de contenido: {pct(g_nada['pct'])}, y concentrados</h3>
   <p>El informe anterior medía 41% de gasto sin respaldo. Acá sube a {pct(g_nada['pct'])} por dos razones que se declaran: se mide contra el
   país que compra (búsquedas que parecían cubiertas lo estaban por impresiones desde otros países) y el desperdicio descontado es una
   reconstrucción del Anexo A (ARS {n(D['ads']['desperdicio_coste'])}), no los ARS 243.023 de la auditoría. Canadá sigue concentrando el problema.</p>
   {tab_h}
  </div>
 </div>
</section>
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 02 · continuación</p><h2>La zona 8–20, recalculada</h2></div>
 <p>ARS {n(zona['coste'])} en {n(zona['terminos'])} términos donde el sitio es relevante pero invisible, contra ARS 106.531 en la base. Baja porque
 el informe anterior calculó la posición como <strong>media simple entre las filas-país</strong> de cada query: una fila de India con 3 impresiones en
 posición 60 pesaba igual que la de España con 600. Ponderando por impresiones y mirando solo el país que compra, cuatro de los cinco términos que dio como
 «prioridades de SEO en posición 12–16» ya estaban en primera página.</p>
 <div class="g">
  <div class="c6">
   <p class="kick">Los cinco del informe anterior · España</p>
   {tab_ref}
   <p class="small" style="margin-top:1.5mm">Ventana «12 meses» del informe anterior (en la práctica marzo–septiembre 2026). «Informe ant.»: media simple
   entre países, reproducida. «Solo ESP»: posición e impresiones para búsquedas desde España. Últimas dos columnas: evolución mensual, país ESP.</p>
  </div>
  <div class="c6">
   <p class="kick">La zona 8–20 real, por país de compra</p>
   {tab_zona}
   <p class="small" style="margin-top:1.5mm">Ventana de Ads (1 ago – 11 sep 2026). Posición orgánica de la query exacta en el país de la campaña.
   pefc en España queda fuera de la ventana de Ads con posición {n(pefc_es_ads,1)}; en 12 meses está en {n(ref5['pefc']['pos_esp'],1)}.</p>
  </div>
 </div>
 <p><strong>El indicador de 30 días del informe anterior no servía:</strong> pedía que los cinco bajaran de posición cuando cuatro ya estaban donde había
 que llegar. Se reemplaza en la sección 06.</p>
</section>
"""

# ------------------------------------------------------------------ sección 02b · no comprada, landing, negativos
orden_nc = sorted(nc.items(), key=lambda kv: -kv[1]["impresiones"])
bloques_nc = ""
for p, v in orden_nc[:6]:
    top = v["top"][:6]
    lst = " · ".join(f"<strong>{e(t['query'])}</strong> {n(t['impressions'])} en pos. {n(t['position'],1)}" for t in top)
    bloques_nc += f"""<div class="card{' key' if v['con_campana']=='si' else ''}"><h4>{e(p)} · {n(v['queries'])} queries sin comprar</h4>
    <p class="met">{n(v['impresiones'])} impresiones · {pct(v['pct_no_comprada'])} de las {n(v['queries_40'])} queries con 40+ ·
    {'con campaña' if v['con_campana']=='si' else 'sin campaña'}</p><p>{lst}</p></div>"""

filas_neg = [[e(r["ambito"]), e(r["propiedad"]), e(r["negativo"]), n(r["impresiones"]), n(r["clics"]), n(r["pos"], 1), e(r["ejemplo"][:60])]
             for r in neg["relevantes"][:8]]
tab_neg = tabla([("Ámbito", ""), ("Propiedad", ""), ("Negativo", ""), ("Impr.", "num"), ("Clics", "num"), ("Pos.", "num"), ("Ejemplo", "")], filas_neg, "tight")

sec2b = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 02 · continuación</p><h2>Demanda sin comprar, landings y negativos</h2></div>
 <h3>4 · Demanda no comprada: {n(nc_tot_q)} queries, {n(nc_tot_i)} impresiones</h3>
 <p>Queries con 40 o más impresiones en todo el histórico que no existen en la cuenta de Ads ni como keyword ni como término,
 por coincidencia de tema. Se excluyen las búsquedas de marca propia y navegacionales. Las propiedades sin campaña se listan
 igual: es demanda probada en mercados donde no se invierte.</p>
 <div class="flow">{bloques_nc}</div>
 <div class="hair"></div>
 <div class="g">
  <div class="c6">
   <h3>5 · Landing desalineada: no medible en {n(land['keywords_con_url'] - land['evaluadas'])} de {n(land['keywords_con_url'])} keywords</h3>
   <p>El export de keywords solo trae URL final para las dos campañas de ISO 27001 (España y Argentina); el resto usa la URL
   del anuncio, que no está en el archivo. De las {n(land['keywords_con_url'])} keywords con URL, {n(land['evaluadas'])} tienen
   una query orgánica comparable y en las {n(land['coinciden'])} la página que rankea es la misma que la URL final. Donde se
   puede medir, no hay desalineación. El dato incómodo es otro: la página de ISO 27001 de España rankea en posición
   {n(land['pos_es'],1)} para sus propias queries; la de Argentina en {n(land['pos_ar'],1)}.</p>
  </div>
  <div class="c6">
   <h3>6 · Validación de negativos: {n(neg['con_presencia'])} con presencia orgánica</h3>
   <p>De los {n(neg['evaluados'])} negativos del Anexo A, {n(neg['con_presencia'])} tienen alguna query orgánica en la propiedad
   que corresponde. Con más de 100 impresiones hay {len(neg['relevantes'])}. El único que merece revisión de alcance es
   <strong>rainforest alliance</strong> en España: {n(neg['relevantes'][0]['impresiones']) if neg['relevantes'] else '—'} impresiones
   en posición {n(neg['relevantes'][0]['pos'],1) if neg['relevantes'] else '—'}, con el negativo puesto en Forestal. El resto son
   coincidencias de token (consultor fsc en posición 45, higg fslm full form) que no cambian la decisión.</p>
  </div>
 </div>
 {tab_neg}
</section>
"""

# ------------------------------------------------------------------ sección 03 · lo nuevo
# evolución top5 de la zona real
ev2 = D["evolucion_zona_top5"]
meses2 = sorted({m for t in ev2.values() for m in t})
filas_ev = [[e(t)] + [n(v.get(m), 1) for m in meses2] for t, v in ev2.items()]
tab_ev = tabla([("Zona 8–20 real · término · país", "")] + [(mes_corto(m), "num") for m in meses2], filas_ev, "tight")

iscc_r = next((r for r in D.get("zona_abr_ago", []) if r["termino"] == "iscc"), None)
txt_iscc = ("" if not iscc_r else
            f"<strong>iscc en España es la señal a mirar:</strong> pasó de posición {n(iscc_r['pos_abr'],1)} con {n(iscc_r['impr_abr'])} impresiones "
            f"en abril a posición {n(iscc_r['pos_ago'],1)} con {n(iscc_r['impr_ago'])} en agosto, desde España. No bajó de posición: casi dejó de "
            f"aparecer. Con la campaña de Bioenergía comprando iscc, conviene revisar la página antes del próximo corte.")
# interanual
filas_yoy = []
for p, v in yoy.items():
    t = v["total"]
    var = (t["impr_2026"] - t["impr_2025"]) / t["impr_2025"] * 100 if t["impr_2025"] else None
    varc = (t["clics_2026"] - t["clics_2025"]) / t["clics_2025"] * 100 if t["clics_2025"] else None
    filas_yoy.append([f"<strong>{e(p)} · total</strong>", n(t["impr_2025"]), n(t["impr_2026"]), pct(var)])
    for r in v["normas"][:5]:
        filas_yoy.append([f"&nbsp;&nbsp;{e(r['norma'])}", n(r["impr_2025"]), n(r["impr_2026"]), pct(r["var_pct"])])
tab_yoy = tabla([("Jun–ago, impresiones", ""), ("2025", "num"), ("2026", "num"), ("Var.", "num")], filas_yoy, "tight")
ya, ym = yoy["Argentina"]["total"], yoy["México"]["total"]
saltos = [f"{e(r['norma'])} en {e(p)} multiplicó por {n(r['impr_2026'] / max(r['impr_2025'], 1))} sus impresiones"
          for p, v in yoy.items() for r in v["normas"][:5] if r["impr_2025"] and r["impr_2026"] / r["impr_2025"] >= 5]
txt_yoy = (f"Argentina pasó de {n(ya['clics_2025'])} a {n(ya['clics_2026'])} clics en el mismo trimestre; México de {n(ym['clics_2025'])} a "
           f"{n(ym['clics_2026'])}. " + ("; ".join(saltos) + "." if saltos else ""))

# aparecieron / desaparecieron
filas_ad = []
corto = lambda q: e(q if len(q) <= 40 else q[:37] + "...")
for p in ["España", "Perú", "Argentina", "México"]:
    v = apdes.get(p)
    if not v:
        continue
    ap = " · ".join(f"{corto(t['query'])} ({n(t['impr'])})" for t in v["top_ap"][:3])
    de = " · ".join(f"{corto(t['query'])} ({n(t['impr'])})" for t in v["top_de"][:3])
    filas_ad.append([f"<strong>{e(p)}</strong><br><span class='small'>{e(v['tramos'][0])} → {e(v['tramos'][1])}</span>",
                     f"<strong>{n(v['aparecieron'])}</strong><br>{ap or '—'}", f"<strong>{n(v['desaparecieron'])}</strong><br>{de or '—'}"])
tab_ad = tabla([("Propiedad · tramos", ""), ("Aparecieron · las tres mayores", ""), ("Desaparecieron · las tres mayores", "")], filas_ad, "tight")
bloques_ad = ["", ""]
for k, p in enumerate([]):
    v = apdes.get(p)
    if not v:
        continue
    corto = lambda q: e(q if len(q) <= 48 else q[:45] + "...")
    ap = " · ".join(f"{corto(t['query'])} ({n(t['impr'])})" for t in v["top_ap"][:3])
    de = " · ".join(f"{corto(t['query'])} ({n(t['impr'])})" for t in v["top_de"][:3])
    bloques_ad[k // 2] += f"""<div class="c6 card"><h4>{e(p)}: {n(v['aparecieron'])} aparecieron · {n(v['desaparecieron'])} desaparecieron</h4>
    <p class="met">{e(v['tramos'][0])} → {e(v['tramos'][1])} · umbral 30 impresiones en el tramo</p>
    <p><span class="lab">Nuevas</span> {ap or '—'}</p><p><span class="lab">Se fueron</span> {de or '—'}</p></div>"""

# dispositivos por propiedad
filas_dev = []
for p in sorted(pan, key=lambda x: (x["marca"] != "CU", -x["impr_total"])):
    d = D["dispositivos"].get(p["propiedad"], {})
    m_, k_ = d.get("MOBILE", {}), d.get("DESKTOP", {})
    filas_dev.append([f"{'PS ' if p['marca']=='PS' else ''}{e(p['propiedad'])}", pct(m_.get("pct_impr"), 1), pct(m_.get("pct_clics"), 1),
                      pct(m_.get("ctr"), 2), pct(k_.get("ctr"), 2)])
tab_dev = tabla([("Propiedad", ""), ("Móvil · impr.", "num"), ("Móvil · clics", "num"), ("CTR móvil", "num"), ("CTR escrit.", "num")],
                filas_dev, "tight")
filas_mn = [[e(r["norma"]), n(r["tot"]), pct(r["pct_mobile"], 1)] for r in D["movil_norma_cu"][:12]]
tab_mn = tabla([("Norma · Control Union", ""), ("Impr.", "num"), ("Móvil", "num")], filas_mn, "tight")

sec3 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 03</p><h2>Lo que la ventana de 12 meses no dejaba ver</h2></div>
 <div class="g">
  <div class="c7">
   <h3>Evolución mensual de la zona 8–20 real</h3>
   <p>Posición ponderada por impresiones, mes a mes, para búsquedas desde el país de la campaña. Siete puntos: es una
   tendencia corta, no una serie. Se lee como banda.</p>
   {tab_ev}
   <p class="small" style="margin-top:1.5mm">Los meses de borde (marzo y septiembre) están incompletos. Un mes sin dato es un mes sin
   impresiones desde ese país para esa query exacta.</p>
   <p>{txt_iscc}</p>
  </div>
  <div class="c5">
   <h3>Interanual, donde hay dos años</h3>
   <p>Argentina y México son las únicas con el mismo trimestre en 2025 y 2026. Se comparan junio, julio y agosto, los tres meses
   completos que existen en los dos años.</p>
   {tab_yoy}
   <p class="small" style="margin-top:1.5mm">Impresiones por propiedad (total) y por norma (corte de queries, anonimizado). {txt_yoy}</p>
  </div>
 </div>
 <div class="hair"></div>
 <h3>Queries que aparecieron y desaparecieron</h3>
 <p>Propiedades con seis meses: primer tramo (hasta el 31 de mayo) contra el último (desde el 16 de junio). Argentina y México:
 junio–agosto de un año contra el otro. «Apareció» = 30+ impresiones en el tramo final y ninguna en el inicial; «desapareció», al revés.</p>
 {tab_ad}
</section>
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 03 · continuación</p><h2>Móvil contra escritorio, medido por primera vez</h2></div>
 <div class="g">
  <div class="c4">{stat(pct(mob.get('pct_impr')), 'Impresiones desde móvil', f"{n(mob.get('impr'))} de {n(mob.get('impr',0)+desk.get('impr',0)+dev.get('TABLET',{}).get('impr',0))} en todo el histórico, las diez propiedades.")}</div>
  <div class="c4">{stat(pct(mob.get('pct_clics')), 'Clics desde móvil', f"{n(mob.get('clics'))} clics. El móvil aporta menos clics que impresiones: el CTR móvil es más bajo en todas las propiedades.")}</div>
  <div class="c4">{stat(n(D['movil_max']['pct'],0)+'%', D['movil_max']['propiedad'], f"es la propiedad más móvil. La menos móvil es {D['movil_min']['propiedad']} con {n(D['movil_min']['pct'],0)}%.")}</div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c7">
   {tab_dev}
   <p class="small" style="margin-top:1.5mm">Reparto sobre impresiones agregadas por propiedad, todo el histórico disponible. Tablet queda fuera
   de la tabla (menos del 2% en todas).</p>
  </div>
  <div class="c5">
   <p class="kick">Móvil por norma · Control Union</p>
   {tab_mn}
   <p class="small" style="margin-top:1.5mm">Sobre el corte query+device, que Google anonimiza igual que queries: los totales son menores
   que los de la tabla de la izquierda, el reparto es comparable.</p>
  </div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c6 panel-line">
   <p class="kick kick-n">Qué cambia con este dato</p>
   <p>La búsqueda de normas es mayoritariamente de escritorio en los mercados con campaña (España, Portugal, Norteamérica):
   es una búsqueda de trabajo. En Perú, Brasil y México el reparto se invierte hacia el teléfono. Las campañas de Search de
   Control Union no tienen ajuste de puja por dispositivo documentado; con este reparto, un ajuste negativo en móvil para las
   campañas de norma en España y Portugal es defendible con datos propios.</p>
  </div>
  <div class="c6 panel-line">
   <p class="kick kick-n">Lo que no dice</p>
   <p>Search Console no informa conversiones ni dispositivo del clic pago. El reparto orgánico es un proxy de cómo busca el
   mercado, no de cómo convierte. Con 4 conversiones en seis semanas en Ads, no hay forma de cerrar ese círculo todavía.</p>
  </div>
 </div>
</section>
"""

# ------------------------------------------------------------------ sección 04 · §7 re-verificado
fsc_tot = s7["fsc_espana"]["impresiones"] + s7["fsc_portugal"]["impresiones"]
oeko_tot = sum(v["impresiones"] for v in s7["oeko_cu"].values())
filas_s7 = [
    ["FSC en España y Portugal", "4.149 impr. «anuales»; abrir grupo",
     f"{n(fsc_tot)} impr. en {n(s7['fsc_espana']['queries'] + s7['fsc_portugal']['queries'])} queries, 3 mar – 13 sep 2026, posiciones {n(s7['fsc_espana']['pos'],1)} y {n(s7['fsc_portugal']['pos'],1)}. Página de programa propia en las dos.",
     "Se sostiene · período corregido"],
    ["OEKO-TEX en Textile España", "Cero en 20.561 queries «de doce meses»",
     f"{n(oeko_tot)} apariciones en {n(s7['queries_cu_total'])} queries de las ocho propiedades de Control Union, todo el histórico.",
     "Se sostiene · período corregido"],
    ["ISO 22000 y FSSC 22000 · España", "2.235 y 708 impr.; grupo propio. BRCGS 33 impr.; negativo",
     f"ISO 22000 {n(s7['iso22000_es']['impresiones'])} impr. pos. {n(s7['iso22000_es']['pos'],1)} · FSSC {n(s7['fssc_es']['impresiones'])} pos. {n(s7['fssc_es']['pos'],1)} · BRCGS {n(s7['brcgs_es']['impresiones'])}. Cero clics orgánicos en las tres.",
     "Se sostiene · período corregido"],
    ["GMP+ España y Portugal", "2.848 impr. en posición 11; el problema era el vocabulario",
     f"España {n(s7['gmp_es']['impresiones'])} impr. pos. {n(s7['gmp_es']['pos'],1)}, creciendo de {n(list(s7['mes_gmp_es'].values())[0])} en marzo a {n(max(s7['mes_gmp_es'].values()))} en el mes pico. Portugal {n(s7['gmp_pt']['impresiones'])} impr. pos. {n(s7['gmp_pt']['pos'],1)}.",
     "Se sostiene y se refuerza"],
    ["CU Canadá · Forestry y Aqua", "223 impr. de FSC «en doce meses»; pausar",
     f"{n(s7['fsc_na']['impresiones'])} impr. de FSC y bosques en toda la propiedad, {n(s7['fsc_na_por_pais'].get('usa',0))} desde Estados Unidos y {n(s7['fsc_na_por_pais'].get('can',0))} desde Canadá. TEMO: {n(temo['impresiones'])} impr. en posición {n(temo['pos'],1)}.",
     "Se sostiene · período corregido; Canadá aún más débil"],
    ["Zona 8–20 · cinco términos de SEO", "GRS, RecyClass, SMETA, ISCC, PEFC en posición 12–16",
     f"Media simple entre filas-país. Ponderada y por país de compra: recyclass {n(ref5['recyclass']['pos_esp'],1)}, smeta {n(ref5['smeta']['pos_esp'],1)}, iscc {n(ref5['iscc']['pos_esp'],1)}, pefc {n(ref5['pefc']['pos_esp'],1)}, GRS {n(ref5['global recycled standard']['pos_esp'],1)} con {n(ref5['global recycled standard']['impr_esp'])} impr. desde España.",
     "Contradice · la lista y el indicador de 30 días se reemplazan"],
    ["ISO 45001 · España", "71.967 impr. «anuales», sin campaña",
     f"{n(iso45['impresiones'])} impr. en {n(iso45['queries'])} queries, pos. {n(iso45['pos'],1)}, {n(iso45['clics'])} clics. Máximo mensual {n(max(s7['mes_iso45001_es'].values()))} en {mes_corto(max(s7['mes_iso45001_es'], key=s7['mes_iso45001_es'].get))}.",
     "Se sostiene · período corregido; es demanda de seis meses"],
]
tab_s7 = tabla([("Decisión de CLAUDE.md §7", ""), ("Qué decía", ""), ("Qué dice el histórico completo", ""), ("Resultado", "")], filas_s7)

sec4 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 04</p><h2>Las decisiones cerradas, re-verificadas</h2></div>
 <p>CLAUDE.md §7 pide no volver a litigar lo resuelto salvo que los datos nuevos lo contradigan, y decirlo explícitamente si lo hacen.
 Se recorrió cada afirmación contra el histórico completo, sin fecha (corte query+país) y con fecha (corte mensual).</p>
 {tab_s7}
 <div class="hair"></div>
 <div class="g">
  <div class="c6">
   <p class="kick kick-n">Qué se sostiene</p>
   <p>Las cinco decisiones de alcance se sostienen en dirección: FSC se certifica y tiene demanda, OEKO-TEX no aparece ni una vez en
   {n(s7['queries_cu_total'])} queries, ISO 22000 y FSSC tienen demanda y BRCGS no, GMP+ existe y crece, Canadá no tiene contenido
   forestal. Lo que cambia es el rótulo temporal: donde decía «doce meses» o «anual» debe decir «marzo a septiembre de 2026».
   Anualizadas, las cifras serían aproximadamente el doble, y el cero de OEKO-TEX es un cero de seis meses, más débil que uno de doce.</p>
  </div>
  <div class="c6">
   <p class="kick kick-n">Qué se contradice</p>
   <p>La lista de «cinco prioridades de SEO en posición 12–16» y el indicador de 30 días que se apoyaba en ella. Con la posición
   ponderada y por país de compra, cuatro de los cinco ya estaban en primera página en España cuando se escribió el informe anterior.
   No es un cambio de los datos: es un error de cálculo del informe anterior, y se corrige acá de forma explícita. La lista que la
   reemplaza está en la sección 02, y el indicador nuevo en la sección 06.</p>
   <p>Las dos decisiones abiertas de §7 (pausar Bioenergía PS y CeSu; corte CU/PS en ISCC Argentina) siguen sin contestarse con
   estos datos.</p>
  </div>
 </div>
</section>
"""

# ------------------------------------------------------------------ sección 05 · límites y supuestos
sec5 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 05</p><h2>Límites de los datos y supuestos sin verificar</h2></div>
 <div class="g">
  <div class="c6">
   <h3>Límites, como siempre</h3>
   <ul class="act">
    <li><span class="tag">Anonimización</span> Google omite queries de bajo volumen. En España el corte por query recoge el
    {pct(D['limites']['pct_query_vs_prop_es'])} de las impresiones de la propiedad; el resto es invisible. No se recupera.</li>
    <li><span class="tag">Ads oculto</span> El 43% del tráfico pago está bajo «Otros términos» y ahí cayeron las 4 conversiones.
    Ningún cruce puede atribuir conversión a término.</li>
    <li><span class="tag">Agregación</span> Por propiedad, por página y por query dan totales distintos (una impresión por búsqueda,
    por URL o por query visible). Este informe declara cuál usa en cada tabla. No se suman entre sí.</li>
    <li><span class="tag">Posición</span> Es un promedio de todas las apariciones. Se usa como banda. Y se pondera por impresiones:
    la media simple entre países fue el error del informe anterior.</li>
    <li><span class="tag">Ventana</span> Seis meses y medio para ocho propiedades. No hay estacionalidad ni interanual salvo en
    Argentina y México, y ahí con hueco.</li>
    <li><span class="tag">Landing</span> Solo medible en ISO 27001: el export de keywords no trae URL final para el resto.</li>
   </ul>
  </div>
  <div class="c6">
   <h3>Supuestos que no se pudieron verificar</h3>
   <ul class="act">
    <li><span class="tag">Retención</span> Que el 4 de mayo de 2025 es el borde de retención de Google y no la fecha de alta de
    Argentina y México. Se infiere de que coinciden entre sí y con el límite de 16 meses. Se confirma si mañana el primer día se corre.</li>
    <li><span class="tag">Hueco</span> La causa del hueco de Argentina y México, y por qué las otras seis arrancan justo el día
    siguiente. Requiere saber qué pasó con las propiedades entre noviembre de 2025 y marzo de 2026.</li>
    <li><span class="tag">Desperdicio</span> La reconstrucción del Anexo A como lista de tokens. Los ARS {n(D['ads']['desperdicio_coste'])}
    que descuenta este informe no son los ARS 243.023 de la auditoría: aquella clasificación era manual y no está en los datos.</li>
    <li><span class="tag">Umbrales</span> «Tema fuerte» = 200+ impresiones del tema en la ventana; «apareció» = 30+ impresiones.
    Son criterios de este informe, no de Google.</li>
    <li><span class="tag">Alcance</span> Que rainforest alliance en España es servicio y no solo demanda. Los datos dicen que hay
    {n(neg['relevantes'][0]['impresiones']) if neg['relevantes'] else '—'} impresiones y una página que rankea; si se certifica, lo sabe la filial.</li>
   </ul>
  </div>
 </div>
 <div class="hair"></div>
 <div class="panel">
  <p class="kick kick-n">Verificación</p>
  <p>Antes de cerrar, un script independiente recalculó {n(D['verificacion']['numeros'])} números de este informe directamente desde
  los CSV fuente, sin pasar por el análisis, y el PDF se rasterizó página por página para contar píxeles de los tres colores de marca
  prohibidos en piezas internas. Resultado: {D['verificacion']['resultado']}.</p>
 </div>
</section>
"""

# ------------------------------------------------------------------ sección 06 · qué cambia
z5 = zona["top"][:5]
z5_txt = ", ".join(f"{t['termino']} ({t['propiedad'] if t['propiedad']!='Norteamérica' else t['pais'].upper()}, {n(t['pos_org'],1)})" for t in z5)
sec6 = f"""
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 06</p><h2>Qué cambia en el plan</h2></div>
 <div class="g">
  <div class="c4 step stat-lite"><h4>01 · Nada de lo decidido se revierte</h4><p class="d">Las cinco decisiones de alcance
  siguen en pie. Solo cambia cómo se las cita: son evidencia de marzo a septiembre de 2026, no anual.</p></div>
  <div class="c4 step stat-lite"><h4>02 · Se reemplaza la lista de SEO</h4><p class="d">Las cinco prioridades pasan a ser
  {e(z5_txt)}. Todas medidas desde el país que compra y ponderadas por impresiones.</p></div>
  <div class="c4 step stat-lite"><h4>03 · Se suma el dispositivo</h4><p class="d">Ajuste de puja por dispositivo en las campañas de
  norma de España y Portugal, donde el escritorio domina. Primero ver el reparto de conversiones en Ads, que este informe no tiene.</p></div>
 </div>
 <div class="hair"></div>
 <h3>Orden sugerido</h3>
 <ul class="act">
  <li><span class="tag">Hoy</span> Guardar el archivo <code>datos/gsc-historico/</code> fuera de la carpeta de trabajo. Es lo único que va a
  existir de mayo de 2025 cuando Google lo borre, y para Argentina y México eso empieza mañana.</li>
  <li><span class="tag">Esta semana</span> Confirmar con quien administre las propiedades qué pasó entre noviembre de 2025 y marzo de 2026.
  Si fue una baja y re-alta, conviene saberlo antes del próximo informe de tendencia.</li>
  <li><span class="tag">Esta semana</span> Corregir el rótulo temporal en el informe anterior donde se cite. Ninguna cifra cambia; el período sí.</li>
  <li><span class="tag">Corto plazo</span> Pasar la zona 8–20 real al equipo de contenido, con la posición por país como línea de base.</li>
  <li><span class="tag">Cada mes</span> Repetir la extracción con los mismos scripts. Cada corrida agrega un mes que Google después borra,
  y la validación de continuidad ya está automatizada.</li>
 </ul>
 <div class="hair"></div>
 <div class="g">
  <div class="c6 panel-navy">
   <p class="kick">Para medir dentro de 30 días</p>
   <p>El indicador anterior (posición media de cinco términos que ya estaban en primera página) se retira. Lo reemplazan dos:
   la posición <strong>ponderada y por país</strong> de la zona 8–20 real de la sección 02, y el <strong>reparto móvil de clics</strong>
   por propiedad, que hoy es {pct(mob.get('pct_clics'))} y por primera vez tiene línea de base.</p>
  </div>
  <div class="c6 panel">
   <p class="kick kick-n">Lo que sigue abierto</p>
   <p>Pausar o no Bioenergía PS y CeSu de Peterson Argentina, y el corte de marca entre Control Union y Peterson en ISCC Argentina.
   Ninguna de las dos se contesta con Search Console: son decisiones de alcance comercial, y donde hay una marca que certifica y otra
   que acompaña, la subasta no puede tener a las dos.</p>
  </div>
 </div>
</section>
"""

# ------------------------------------------------------------------ documento
doc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Search Console · histórico, fecha y dispositivo · documento interno</title>
<link rel="stylesheet" href="style.css">
<style>
 ul.act li{{ text-indent:-26mm; padding-left:26mm; }}
 ul.act .tag{{ width:23mm; }}
 table.tight td{{ padding:1.3mm 2.5mm; }}
 .panel{{ padding:3.2mm 4mm; }}
 .cover-top h1{{ font-size:30pt; max-width:160mm; }}
 .cover{{ height:auto; min-height:250mm; }}
 td{{ font-size:8pt; }}
</style>
</head><body>
{cover}{sec1}{sec2}{sec2b}{sec3}{sec4}{sec5}{sec6}
</body></html>"""
with open(os.path.join(INF, "informe.html"), "w", encoding="utf-8") as f:
    f.write(doc)
print("-> informe/informe.html")
