# -*- coding: utf-8 -*-
"""
generar_seo.py — informe exclusivo de recomendaciones SEO para los sitios, desde Search Console.
Fuente: informe/datos_seo.json + informe/datos_informe.json. Sale a informe/seo.html
"""
import json, os
from informe_util import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
S = json.load(open(os.path.join(INF, "datos_seo.json"), encoding="utf-8"))
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))
FECHA = hoy()
ORDEN_CU = ["España", "Portugal", "Norteamérica", "Argentina", "Perú", "México", "Brasil", "Chile"]
ORDEN_PS = ["Américas", "Iberia"]
DOMINIO = {"España": "espana.controlunion.com", "Portugal": "portugal.controlunion.com", "Norteamérica": "northamerica.controlunion.com",
           "Argentina": "argentina.controlunion.com", "Perú": "peru.controlunion.com", "México": "mexico.controlunion.com",
           "Brasil": "brasil.controlunion.com", "Chile": "chile.controlunion.com", "Américas": "americas.peterson-solutions.com",
           "Iberia": "iberia.peterson-solutions.com"}

tot_impr = sum(v["impr"] for v in S.values()); tot_clics = sum(v["clics"] for v in S.values())
tot_pag = sum(v["paginas_total"] for v in S.values()); tot_pag_clic = sum(v["paginas_con_clic"] for v in S.values())
n_canib = sum(len(v["canibalizacion"]) for v in S.values())
n_low = sum(len(v["low_ctr"]) for v in S.values())
n_qw = sum(len(v["quick_wins"]) for v in S.values())
qw_impr = sum(q["impr"] for v in S.values() for q in v["quick_wins"])
low_impr = sum(q["impr"] for v in S.values() for q in v["low_ctr"])
mob = D["dispositivos_total"]["MOBILE"]


def seg(path):
    """último tramo legible de una URL"""
    if not path:
        return "—"
    partes = [x for x in path.split("/") if x]
    return e(partes[-1][:38] if partes else path)


def fila_qw(q, con_pagina=True):
    return [f"<b>{e(q['query'])}</b>", n(q["impr"]), n(q["pos"], 1), pct(q["ctr"], 2), path_corto(q.get("page_path"), 46)]


def bloque_prop(p):
    v = S[p]
    qw = v["quick_wins"][:4]; low = v["low_ctr"][:3]; can = v["canibalizacion"][:2]; per = v["perdidas"][:2]; prof = v["profundo"][:2]
    html = f'''<div class="prop">
 <div class="prop-head"><h3>{"Peterson Solutions · " if v["marca"]=="PS" else ""}{e(p)} <span class="small" style="font-weight:400">{e(DOMINIO[p])}</span></h3>
  <div class="meta">{n(v["impr"])} impr. · {n(v["clics"])} clics · CTR <b>{pct(v["ctr"],2)}</b> · pos. media <b>{n(v["pos"],1)}</b> · {n(v["paginas_con_clic"])} de {n(v["paginas_total"])} páginas con clic · móvil {pct(v["movil"]["pct"],0)} (CTR {pct(v["movil"]["ctr_m"],2)} vs {pct(v["movil"]["ctr_d"],2)})</div></div>
 <div class="g">'''
    if qw:
        html += f'''<div class="c7"><p class="kick">Quick wins · posición 8–15 desde {"/".join(x.upper() for x in v["paises"])}, 150+ impresiones</p>
        {tabla([("Query", ""), ("Impr.", "num"), ("Pos.", "num"), ("CTR", "num"), ("Página que rankea", "")], [fila_qw(q) for q in qw], "mini")}</div>'''
    else:
        html += '<div class="c7"><p class="kick">Quick wins</p><p class="small">Ninguna query con 150+ impresiones en posición 8–15 desde el país principal. La propiedad rankea poco o rankea en otros mercados.</p></div>'
    html += '<div class="c5">'
    if can:
        html += '<p class="kick">Páginas que compiten entre sí</p><ul class="acc">' + "".join(
            f'<li><span class="tag">{e(c["query"])}</span>{n(c["impr"])} impr. repartidas: ' + " · ".join(f'{seg(x["path"])} ({n(x["impr"])}, pos. {n(x["pos"],1)})' for x in c["paginas"][:2]) + '</li>' for c in can) + '</ul>'
    if low:
        html += '<p class="kick" style="margin-top:2.5mm">Primera página, CTR bajo</p><ul class="acc">' + "".join(
            f'<li><span class="tag">{pct(x["ctr"],2)}</span>{path_corto(x["path"], 40)} · {n(x["impr"])} impr., pos. {n(x["pos"],1)}</li>' for x in low) + '</ul>'
    if per:
        html += '<p class="kick" style="margin-top:2.5mm">Perdió visibilidad ({} → {})</p><ul class="acc">'.format(e(v["tramos"][0]), e(v["tramos"][1])) + "".join(
            f'<li><span class="tag">{n(x["antes"])} → {n(x["despues"])}</span><b>{e(x["query"])}</b> · {path_corto(x["page_path"], 34)}</li>' for x in per) + '</ul>'
    if prof:
        html += '<p class="kick" style="margin-top:2.5mm">Demanda grande en página 2–3: contenido, no ajuste</p><ul class="acc">' + "".join(
            f'<li><span class="tag">pos. {n(x["pos"],1)}</span><b>{e(x["query"])}</b> · {n(x["impr"])} impr. · {path_corto(x["page_path"], 30)}</li>' for x in prof) + '</ul>'
    html += '</div></div></div>'
    return html


# --------------------------------------------------------------- recomendaciones por propiedad (texto)
REC = {
    "España": [("Título y snippet", "GRS (15.968 impr., pos. 8,1, CTR 0,27%) y Welfair (11.232, pos. 8,3, 0,31%) están en primera página y nadie hace clic. Reescribir title y meta con la intención real: «Certificación GRS: requisitos, auditoría y cómo obtenerla»."),
               ("ISO 45001", "La mayor demanda del grupo (72.363 impr., pos. 11,6) con página propia. Contenido de apoyo: requisitos, plazos, diferencias con OHSAS, preguntas frecuentes. Pasar de 11 a primera página vale más que cualquier campaña."),
               ("ISCC", "Dos URL compiten (iscc-plus e iscc_eu) y la query «iscc» pasó de 605 a 11 impresiones desde España. Unificar en una página madre ISCC con secciones EU y PLUS, redirigir la otra."),
               ("Versiones EN", "gmp+, gstc y bienestar animal reparten impresiones entre la URL en español y la /en/. Declarar hreflang y canonical por idioma para que España vea la versión en español."),
               ("ISO 27001", "La página rankea en posición 43 para sus propias queries mientras la campaña paga ARS 6.019 por clic. Reescribir con vocabulario de búsqueda: certificación, precio, requisitos, plazos, auditoría.")],
    "Portugal": [("ISO 9001", "1.271 impr. en posición 12,3 y cayendo (1.174 → 85 entre tramos). Revisar la página: es la única de la unidad con caída fuerte."),
                 ("Aquacultura", "La página de industria /industry/aquacultura-e-pesca/ tiene 4.959 impr. en posición 6,2 y CTR 0,06%: no responde a la búsqueda. Título con «certificação» y enlaces a ASC, MSC, BAP."),
                 ("OCS y PEFC", "OCS reparte entre PT y /en/; PEFC está en 9,0 con 525 impr. Hreflang y refuerzo interno desde /industry/florestal/ a la página PEFC."),
                 ("Rainforest Alliance", "4.829 impr. en posición 6,3 con CTR 0,21%. Snippet con beneficio concreto y llamada a la acción.")],
    "Norteamérica": [("TEMO", "22.485 impr., posición 8,9, CTR 0,06%, y cayó de 3.165 a 249 impresiones entre tramos. Es la página que más tráfico podría traer de la propiedad. Revisar indexación, título («TEMO: temperature monitoring for commodity inspections») y contenido."),
                     ("Geografía", "Canadá aporta 2.251 impresiones contra 7.599 de India y 13.441 de EE.UU. Contenido y señales geográficas (hreflang en-CA / en-US, direcciones, casos) para que el sitio exista en Canadá."),
                     ("PrimusGFS", "Dos páginas compiten por «primusgfs certification» (772 impr.). Unificar."),
                     ("Contenido forestal", "FSC y bosques suman 251 impresiones en toda la propiedad: no hay contenido que sostenga la campaña Forestry. Si se quiere vender FSC en Canadá, hay que escribir la página primero.")],
    "Argentina": [("SMETA y VISEC", "smeta (8.917 impr.) y visec (8.812) reparten entre la página en español y la /en/. Hreflang y canonical; la /en/ no debería rankear para búsquedas desde Argentina."),
                  ("Servicios", "/servicios-inspecciones/ tiene 11.472 impr. en posición 4,0 y CTR 0,5%. Es una página de listado: título y descripción con los servicios concretos (inspección de commodities, depósito fiscal, warrants)."),
                  ("Depósito fiscal", "De 801 impresiones a 1 entre tramos. Verificar que /service/deposito-fiscal/ existe, está indexada y enlazada."),
                  ("Quick wins", "visec carne (8,5), cfr (8,9), sedex argentina (8,8), warrants (8,6): todas a un empujón de primera página, con página propia. Enlazado interno y H1 alineado con la query.")],
    "Perú": [("HACCP", "45.407 impr. en posición 8,0 con CTR 0,28%: la búsqueda es «qué es HACCP» y la página vende certificación. Sección de definición arriba, rich snippet de preguntas frecuentes."),
             ("PDFs", "El certificado MSC en /wp-content/uploads/ recibe 32.767 impresiones con CTR 0,1%, y los GEI PDFs compiten entre sí. Página HTML que los reemplace y noindex para los PDF."),
             ("Login", "«control union login» reparte 3.460 impr. entre /en/cis-login/ y /en/login/. Una sola URL de acceso, enlazada desde el header, y sitelinks."),
             ("Pérdidas", "koa certification (1.151 → 128), bap (699 → 127) y haccp que es (797 → 213) bajaron entre tramos. Vigilar antes del próximo corte.")],
    "México": [("GRS", "38.407 impr. en posición 6,6 con CTR 0,27%: la mayor oportunidad de CTR de toda la red. Título y meta orientados a «certificación GRS en México»."),
               ("FSA", "6.663 impr. repartidas entre /programa-de-certificacion/fsa/ y /es/normas-internacionales/fsa/. Unificar con redirección."),
               ("Móvil", "La propiedad más móvil (41%) con CTR móvil 0,95% contra 1,50% escritorio. Revisar snippet y velocidad móvil de las páginas de programa."),
               ("Fair trade y OBP", "fair trade cayó de 1.025 a 62 impresiones; obp de 637 a 0. Verificar las dos páginas.")],
    "Brasil": [("GMP+", "3.712 impr. en posición 10,7: la página está a un paso de primera página y es el mismo caso que España y Portugal. Contenido en portugués sobre GMP+ FSA."),
               ("Pest control", "1.403 impresiones en el primer tramo y cero en el último: la página /service/servicos/inspeccoes/pest-control/ desapareció de los resultados. Verificar."),
               ("Versiones EN", "gmp+, iscc y pefc reparten entre PT y /en/. Hreflang."),
               ("Contacto", "/en/contact/ recibe 7.280 impr. con CTR 0,44%: rankea por marca en inglés. Sitelinks y versión en portugués.")],
    "Chile": [("Login por marca", "/en/cis-login/ acumula 12.005 impr. para búsquedas de marca con CTR 0,14%. La home debería ganar esas búsquedas: título de marca, sitelinks, y noindex del login."),
              ("BRCGS y SMETA", "brcgs (994 impr., pos. 8,2) y smeta (800, 7,9) a un paso de primera página con página propia. Enlazado interno y H1."),
              ("NCh 2861", "Tres URL compiten por la norma chilena (EN, ES y el listado). Una sola página en español.")],
    "Américas": [("Español para Argentina", "El 80% de las impresiones está en páginas /en/ y Argentina aporta el " + str(S["Américas"]["pct_pais"]) + "%. Los cinco servicios que se pagan (agricultura regenerativa, huella de carbono, ESG, huella de agua, EUDR) necesitan página en español con URL propia. Sin eso, el paid compite solo."),
                 ("RED III", "La página de RED III tiene 20.511 impr. en posición 8,4 con CTR 0,22%: es la que más ve el mercado. Título con la pregunta que la gente hace y enlaces a los servicios."),
                 ("Home y contacto", "«peterson» reparte 4.942 impr. entre / y /contact/. Consolidar la SERP de marca con sitelinks."),
                 ("Tono", "Peterson acompaña, co-desarrolla y prepara para certificar: las páginas nuevas no prometen el certificado.")],
    "Iberia": [("CSRD y CBAM", "csrd 1.456 impr. en posición 21,5, cbam services 238 en 28,6, finanzas sostenibles 269 en 25,4: hay página para cada uno y todas en página 2–3. Contenido de fondo y enlazado interno antes que pauta."),
               ("Marca e idioma", "«peterson solutions» reparte entre / y /en/, y /en/home/about-us/ recibe 4.717 impr. con CTR 0,19% de usuarios en español. Hreflang es/en, canonical de la home y versión en español visible.")],
}


def recs(p):
    return '<ul class="acc">' + "".join(f'<li><span class="tag">{e(t)}</span>{e(x)}</li>' for t, x in REC[p]) + '</ul>'


# --------------------------------------------------------------- hallazgos estructurales
ej_can = [(p, c) for p in ORDEN_CU + ORDEN_PS for c in S[p]["canibalizacion"] if any("/en/" in x["path"] or "/es/" in x["path"] or "/pt" in x["path"] for x in c["paginas"])]
ej_can_txt = " · ".join(f"{e(c['query'])} ({e(p)}, {n(c['impr'])})" for p, c in ej_can[:8])
pdfs = [(p, x) for p in S for x in S[p]["low_ctr"] + S[p]["top_pages"] if "/wp-content/" in x["path"]]
pdfs_impr = sum(x["impr"] for _, x in {(p, x["path"]): (p, x) for p, x in pdfs}.values())
low_ej = sorted(((p, x) for p in S for x in S[p]["low_ctr"]), key=lambda t: -t[1]["impr"])[:5]
perd_ej = sorted(((p, x) for p in S for x in S[p]["perdidas"]), key=lambda t: -t[1]["antes"])[:6]

hallazgos = f'''
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 01</p><h2>Seis problemas que se repiten en todos los sitios</h2></div>
 <p>Antes de ir propiedad por propiedad: estos seis patrones aparecen en casi todas y se corrigen una vez, a nivel de plantilla o de configuración.
 Son el grueso del trabajo y el que más rinde.</p>
 <div class="g">
  <div class="c4 find"><p class="k">{n(n_canib)}</p><h4>Páginas que compiten entre sí</h4>
   <p>La versión en español y la /en/ de la misma norma se reparten las impresiones de una query: gmp+ en España mitad y mitad, smeta y visec en Argentina, fsa en México, ocs en Portugal. Google no sabe cuál mostrar y ninguna sube.</p>
   <p class="small">Qué hacer: hreflang entre idiomas, canonical por idioma, y que cada mercado hispano enlace a la versión en su idioma. Casos: {ej_can_txt}.</p></div>
  <div class="c4 find"><p class="k">{n(low_impr)}</p><h4>Impresiones en primera página con CTR bajo</h4>
   <p>{n(n_low)} páginas con 1.000+ impresiones, posición 10 o mejor y menos de 0,6% de clics. La gente ve el resultado y no entra: el título no responde a lo que buscó.</p>
   <p class="small">Qué hacer: reescribir title y meta description con la intención real (qué es, requisitos, cómo obtener). Las mayores: {" · ".join(f"{seg(x['path'])} ({e(p)}, {n(x['impr'])}, {pct(x['ctr'],2)})" for p, x in low_ej[:4])}.</p></div>
  <div class="c4 find"><p class="k">{n(pdfs_impr)}</p><h4>Impresiones que se lleva un PDF</h4>
   <p>Certificados y documentos en /wp-content/uploads/ rankean en lugar de una página: el certificado MSC de Perú recibe 32.767 impresiones con CTR 0,1%, el de RESSA en España 3.426, y los GEI de Perú compiten entre sí.</p>
   <p class="small">Qué hacer: página HTML que explique el certificado y enlace al PDF; noindex en los uploads o canonical hacia la página.</p></div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c4 find"><p class="k">{n(n_qw)}</p><h4>Quick wins en posición 8–15</h4>
   <p>{n(qw_impr)} impresiones en queries con página propia que están a una o dos posiciones de la primera página. Es el trabajo más barato: enlazado interno, H1 alineado con la query, un párrafo que responda la pregunta.</p>
   <p class="small">Lista completa en cada propiedad. Las mayores: grs en México (21.761, pos. 7,6), haccp en Perú (15.252, 7,9), iso 45001 en España (7.859, 12,6), gmp en Brasil (3.712, 10,7), temo en Norteamérica (3.425, 15,1).</p></div>
  <div class="c4 find"><p class="k">{pct(mob['pct_impr'],0)}</p><h4>Móvil: mismas posiciones, la mitad de clics</h4>
   <p>El {pct(mob['pct_impr'],0)} de las impresiones llega desde móvil con posiciones iguales o mejores que escritorio, y el CTR móvil es entre la mitad y dos tercios en España, Portugal, México y Norteamérica.</p>
   <p class="small">Qué hacer: revisar el snippet en móvil (títulos que se cortan), velocidad y Core Web Vitals de las páginas de programa. Search Console no mide la velocidad: es un supuesto a verificar con PageSpeed.</p></div>
  <div class="c4 find"><p class="k">{len(perd_ej)}</p><h4>Páginas que perdieron visibilidad</h4>
   <p>Queries con 300+ impresiones en el primer tramo que cayeron más de 70% en el último. No son cambios de posición: son páginas que dejaron de aparecer.</p>
   <p class="small">{" · ".join(f"{e(x['query'])} ({e(p)}, {n(x['antes'])} → {n(x['despues'])})" for p, x in perd_ej)}. Verificar indexación y redirecciones antes del próximo corte.</p></div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c6 panel"><p class="kick kick-n">Regla de marca para el contenido</p><p class="small">Control Union certifica, audita, inspecciona y verifica: las páginas nuevas de controlunion.com hablan de certificación y auditoría, nunca de asesoramiento ni de «diseñar tu estrategia». Peterson Solutions acompaña, co-desarrolla y prepara para certificar: las de peterson-solutions.com no prometen el certificado. Cada dominio resuelve lo suyo.</p></div>
  <div class="c6 panel"><p class="kick kick-n">Cómo se midió</p><p class="small">Search Console, histórico completo por propiedad (marzo–septiembre 2026; Argentina y México desde mayo 2025), cortes query+página, página+fecha y query+dispositivo. Posiciones ponderadas por impresiones y filtradas al país principal de cada propiedad. Umbrales: quick win = posición 8–15 y 150+ impresiones; CTR bajo = 1.000+ impresiones, posición ≤ 10, CTR < 0,6%; canibalización = dos páginas con 20%+ de las impresiones de una query.</p></div>
 </div>
</section>'''

# --------------------------------------------------------------- propiedades
def seccion_marca(titulo, kick, props):
    # cada propiedad (ficha + recomendaciones) es un bloque indivisible: si no entra, pasa entero a la página siguiente
    return ('<section class="newpage">' + f'<div class="sec-head"><div class="rule"></div><p class="kick">{e(kick)}</p><h2>{e(titulo)}</h2></div>' +
            "".join(f'<div class="propwrap">{bloque_prop(p)}<p class="kick" style="margin-top:-2mm">Recomendaciones · {e(p)}</p>{recs(p)}</div><div class="hair"></div>' for p in props) + '</section>')


cu_html = seccion_marca("Sitios de Control Union", "Sección 02 · controlunion.com", ORDEN_CU)
ps_html = seccion_marca("Sitios de Peterson Solutions", "Sección 03 · peterson-solutions.com", ORDEN_PS)

# --------------------------------------------------------------- plan
plan = f'''
<section class="newpage">
 <div class="sec-head"><div class="rule"></div><p class="kick">Sección 04</p><h2>Plan y cómo medirlo</h2></div>
 <div class="plan">
  <div class="ph"><p class="when">Primeros 30 días · configuración</p><h4>Una vez, para todos los sitios</h4><ul>
   <li>hreflang y canonical por idioma en la plantilla de programa de certificación.</li>
   <li>noindex en /wp-content/uploads/ y página HTML para los certificados que rankean.</li>
   <li>Una sola URL de login, fuera del índice; sitelinks de marca.</li>
   <li>Verificar las {len(perd_ej)} páginas que perdieron visibilidad: indexación, redirecciones, contenido.</li></ul></div>
  <div class="ph"><p class="when">30 a 60 días · snippets y quick wins</p><h4>Sin escribir páginas nuevas</h4><ul>
   <li>Title y meta de las {n(n_low)} páginas con CTR bajo en primera página, empezando por GRS (México y España), HACCP (Perú) y TEMO.</li>
   <li>Los {n(n_qw)} quick wins: H1 alineado con la query, un párrafo de respuesta directa, enlazado interno desde industria y home.</li>
   <li>Unificar las páginas que compiten: ISCC en España, FSA en México, PrimusGFS en Norteamérica, NCh 2861 en Chile.</li></ul></div>
  <div class="ph"><p class="when">60 a 90 días · contenido</p><h4>Lo que necesita páginas nuevas</h4><ul>
   <li>Peterson Américas: cinco servicios en español para Argentina.</li>
   <li>ISO 45001 en España: contenido de apoyo para pasar de 11 a primera página.</li>
   <li>Peterson Iberia: CSRD, CBAM y finanzas sostenibles de página 2–3 a primera.</li>
   <li>Norteamérica: contenido forestal y señales geográficas para Canadá.</li></ul></div>
 </div>
 <div class="hair"></div>
 <div class="g">
  <div class="c6 panel-navy"><p class="kick">Indicadores, con línea de base hoy</p>
   <p><strong>CTR de las {n(n_low)} páginas con CTR bajo</strong>: hoy entre 0,06% y 0,52%. Meta: por encima de 1% en 60 días.<br>
   <strong>Quick wins en primera página</strong>: {n(n_qw)} queries hoy en posición 8–15. Meta: la mitad por debajo de 8 en 90 días.<br>
   <strong>Canibalización interna</strong>: {n(n_canib)} queries repartidas. Meta: cero con más de 20% en la segunda URL.<br>
   <strong>Argentina en Peterson Américas</strong>: {S['Américas']['pct_pais']}% de las impresiones hoy.</p></div>
  <div class="c6 panel"><p class="kick kick-n">Lo que este informe no puede ver</p>
   <p class="small">Search Console no mide velocidad, Core Web Vitals, enlazado interno ni contenido: las causas propuestas para el CTR móvil y las caídas son hipótesis a confirmar en el sitio. Las queries chicas están anonimizadas. Seis meses de datos para ocho propiedades: sin estacionalidad. Y la posición es un promedio: se lee como banda.</p>
   {nota_marca(FECHA)}</div>
 </div>
</section>'''

# --------------------------------------------------------------- portada
cover = f'''
<section class="cover">
 <div class="cover-top">
  <p class="kick">Documento interno · Peterson Control Union World Group</p>
  <h1>Recomendaciones SEO para los sitios, desde lo que Search Console ya muestra</h1>
  <div class="cover-meta">
   <div class="c3"><p class="lbl">Alcance</p><p class="val">8 sitios de Control Union<br>2 de Peterson Solutions</p></div>
   <div class="c3"><p class="lbl">Fuente</p><p class="val">Search Console, histórico completo<br>{n(tot_impr)} impresiones · {n(tot_clics)} clics</p></div>
   <div class="c3"><p class="lbl">Páginas</p><p class="val">{n(tot_pag_clic)} de {n(tot_pag)} recibieron un clic<br>el resto aparece y no convence</p></div>
   <div class="c3"><p class="lbl">Complementa a</p><p class="val">Pain points por unidad<br>Search Console: histórico y móvil</p></div>
  </div>
 </div>
 <div class="cover-body">
  <div class="g">
   <div class="c3">{stat(n(n_qw), "quick wins", f"queries en posición 8–15 con página propia y 150+ impresiones. {n(qw_impr)} impresiones a un empujón de primera página.")}</div>
   <div class="c3">{stat(n(low_impr), "impr. sin clic", f"en {n(n_low)} páginas de primera página con CTR menor a 0,6%. Problema de título, no de posición.")}</div>
   <div class="c3">{stat(n(n_canib), "queries repartidas", "entre dos páginas del mismo sitio, casi siempre la versión en español y la /en/.")}</div>
   <div class="c3">{stat(pct(mob['pct_impr'],0), "móvil", f"de las impresiones, con CTR {pct(mob['pct_clics'],0)} de los clics. Mismas posiciones, la mitad de clics.")}</div>
  </div>
  <div class="hair"></div>
  <div class="g">
   <div class="c7"><p class="kick kick-n">La idea en una frase</p>
    <p class="lede">Los sitios ya aparecen. Lo que falta no es posicionar páginas nuevas sino que las que están en primera página consigan el clic, que dejen de competir entre sí, y que cada mercado vea su idioma.</p>
    <p>Tres cuartas partes de las recomendaciones se resuelven con configuración y títulos, sin escribir una página. El resto es contenido concreto: cinco servicios en español para Peterson en Argentina, ISO 45001 en España, CSRD en Iberia y algo forestal en Canadá.</p></div>
   <div class="c5 panel"><p class="kick kick-n">Cómo leer</p><p class="small">Sección 01: seis problemas transversales y su solución única. Secciones 02 y 03: cada sitio con sus quick wins, sus páginas que compiten, sus páginas con CTR bajo y lo que perdió, más cuatro o cinco recomendaciones concretas. Sección 04: plan a 90 días e indicadores con línea de base. Cada dominio se trata en su propia marca.</p></div>
  </div>
 </div>
 <div class="cover-foot">{nota_marca(FECHA)}</div>
</section>'''

doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Recomendaciones SEO para los sitios · documento interno</title>
<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="estilo-ejecutivo.css">
<style>.prop table.mini td{{ font-size:7.5pt; }} .acc li{{ font-size:7.9pt; }}</style>
</head><body>{cover}{hallazgos}{cu_html}{ps_html}{plan}</body></html>'''
open(os.path.join(INF, "seo.html"), "w", encoding="utf-8").write(doc)
print("-> informe/seo.html")
