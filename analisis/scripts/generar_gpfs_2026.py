# -*- coding: utf-8 -*-
"""
generar_gpfs_2026.py — dos informes sobre la campaña Search de Control Union para The Global Produce & Floral Show 2026:

  A  solo con los archivos adjuntos (todo-junto.csv + LEEME_ARS.md) y buenas prácticas generales
  B  completo: lo anterior + la web oficial del show, la landing, la cuenta de Google Ads, Search Console y el proyecto

Pieza de una sola marca (Control Union): identidad completa de CU (estilo-cu.css, render con --marca cu).
Salidas: informe/gpfs-2026-A.html y informe/gpfs-2026-B.html (los PDF los arma render_informe.py).
Cada número sale de un archivo fuente; los hechos de la web llevan su URL y la fecha de verificación.
"""
import csv, json, os, re
import pandas as pd
from informe_util import n, ars, e
from lib_analisis import cargar_hist, agregar
import gpfs_2026_campana as V2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
API = os.path.join(ROOT, "datos", "ads", "api")
ORIG = os.path.join(ROOT, "campanas", "gpfs-2026", "original", "todo-junto.csv")
VERIFICADO = "1 oct 2026"
FUENTE_SHOW = "freshproduce.com/events/the-global-produce-and-floral-show (sección Schedule)"

# ================================================================== 1. la campaña original
filas = list(csv.DictReader(open(ORIG, encoding="utf-8-sig")))
kw_o = [r for r in filas if r["Criterion Type"] in ("Exact", "Phrase")]
neg_o = [r for r in filas if r["Criterion Type"].startswith("Campaign Negative")]
rsa_o = [r for r in filas if r["Ad Name"]]
sl_o = [r for r in filas if r["Sitelink Text"]]
grupos_o = sorted({r["Ad Group"] for r in kw_o})
tit_o = [[r[f"Headline {i}"] for i in range(1, 16) if r[f"Headline {i}"]] for r in rsa_o]
des_o = [[r[f"Description {i}"] for i in range(1, 5) if r[f"Description {i}"]] for r in rsa_o]
O = dict(grupos=len(grupos_o), kw=len(kw_o), exactas=sum(r["Criterion Type"] == "Exact" for r in kw_o), neg=len(neg_o), rsa=len(rsa_o),
         titulos=min(len(t) for t in tit_o), titulos_max=max(len(t) for t in tit_o), sitelinks=len(sl_o),
         largo_max_t=max(len(x) for t in tit_o for x in t), largo_max_d=max(len(x) for d in des_o for x in d),
         presupuesto=int(filas[0]["Budget"]), dias=15)
O["total"] = O["presupuesto"] * O["dias"]
assert O["largo_max_t"] <= 30 and O["largo_max_d"] <= 90
fechas_en_copy = sorted({x for t in tit_o + des_o for x in t if "14-16" in x})

# ================================================================== 2. contexto de la cuenta (foto de la API, solo lectura)
ctx_ruta = sorted(f for f in os.listdir(API) if f.startswith("gpfs_contexto_"))[-1]
CTX = json.load(open(os.path.join(API, ctx_ruta), encoding="utf-8"))
form = CTX["disparos_ago_sep"].get("Enviar formulario de clientes potenciales", {}).get("conversiones", 0)
email = CTX["disparos_ago_sep"].get("Click Email", {}).get("conversiones", 0)
tasa_form = form / CTX["cuenta_ago_sep"]["clics"] * 100
prim_ruido = [a["nombre"] for a in CTX["acciones"] if a["primaria"] and a["categoria"] in ("PAGE_VIEW", "OUTBOUND_CLICK")]
usa_sep = {x["campana"]: x for x in CTX["usa_sep"]}
nop_sep = usa_sep["CU United States - Organic - USDA NOP - Search"]
pri_sep = usa_sep["CU United States - Organic - PrimusGFS - Search"]

# ================================================================== 3. Google Ads: EE.UU. y Canadá, 1 ago – 24 sep 2026 (dos ventanas del proyecto)
VENT = ("2026-08-01_2026-09-11", "2026-09-12_2026-09-24")
an = pd.concat([pd.read_csv(os.path.join(API, "cu", f"ads_cu_anuncios_{w}.csv"), encoding="utf-8-sig") for w in VENT])
an = an[an["campaign.name"].str.contains("United States|Canada", na=False)]
g = an.groupby("campaign.name").agg(coste=("metrics.cost_micros", "sum"), clics=("metrics.clicks", "sum"), conv=("metrics.conversions", "sum"))
g["coste"] = g["coste"] / 1e6
CPC = {c: (r.coste / r.clics if r.clics else None, int(r.clics), r.coste, r.conv) for c, r in g.iterrows()}
cpc_nop = CPC["CU United States - Organic - USDA NOP - Search"]
cpc_pri = CPC["CU United States - Organic - PrimusGFS - Search"]
cpc_ca = {c: v for c, v in CPC.items() if c.startswith("CU Canada") and v[1]}
ter = pd.concat([pd.read_csv(os.path.join(API, "cu", f"ads_cu_terminos_{w}.csv"), encoding="utf-8-sig") for w in VENT])
ter = ter[ter["campaign.name"].str.contains("United States", na=False)].groupby("search_term_view.search_term", as_index=False).agg(
    coste=("metrics.cost_micros", "sum"), clics=("metrics.clicks", "sum"))
ter["coste"] = ter["coste"] / 1e6
gfsi = ter[ter["search_term_view.search_term"] == "gfsi consultant"].iloc[0]
defin = ter[ter["search_term_view.search_term"].str.contains(r"^(?:what|how)\b", regex=True)]
kws = pd.read_csv(os.path.join(API, sorted(d for d in os.listdir(API) if d.startswith("estructura_"))[-1], "keywords.csv"), encoding="utf-8-sig")
kp = kws[(kws["campaign.name"] == "CU United States - Organic - PrimusGFS - Search") & (kws["ad_group_criterion.status"] == "ENABLED")]
kp_raras = int((kp["ad_group_criterion.system_serving_status"] == "RARELY_SERVED").sum())

# ================================================================== 4. Search Console (histórico hasta 14 sep 2026)
q = cargar_hist("cu", "queries_agg")
na = q[q["property"] == "Norteamérica"]
mx = q[q["property"] == "México"]


def tema(df, rx, paises=None):
    s = df[df["query"].str.contains(rx, case=False, regex=True, na=False)]
    if paises:
        s = s[s["country"].isin(paises)]
    return s


ev = tema(na, r"ifpa|fresh summit|produce show|produce and floral|gpfs|trade show", ["usa", "can", "mex"])
marca_us = agregar(tema(na, r"^(?!.*pest).*control ?union", ["usa"]), ["query"]).sort_values("impressions", ascending=False)
marca_cu_us = marca_us[marca_us["query"] == "control union"].iloc[0]
marca_usa = marca_us[marca_us["query"] == "control union usa"].iloc[0]
marca_total_us = int(marca_us["impressions"].sum())
pri_na = tema(na, r"primus", ["usa", "can", "mex"])
pri_us = int(pri_na[pri_na["country"] == "usa"]["impressions"].sum())
pri_pos = (pri_na["position"] * pri_na["impressions"]).sum() / pri_na["impressions"].sum()
pri_mx_na = int(pri_na[pri_na["country"] == "mex"]["impressions"].sum())
gg_us = int(tema(na, r"global ?g\.?a\.?p|globalgap|global gap", ["usa"])["impressions"].sum())
MX = {k: int(tema(mx, rx)["impressions"].sum()) for k, rx in [("PrimusGFS", r"primus"), ("SMETA", r"smeta"), ("GLOBALG.A.P.", r"global ?g\.?a\.?p|globalgap|global gap")]}
pag = cargar_hist("cu", "pages")
pag = agregar(pag[pag["page"].str.contains("northamerica", na=False)], ["page"])
landing_en_gsc = bool(pag["page"].str.contains("fresh-produce-certification-expertise").any())

# ================================================================== 5. expectativa de clics (presupuesto ÷ puja media ponderada)
pujas = [p for d in V2.GRUPOS.values() for _, _, p in d["kw"]]
puja_media = sum(pujas) / len(pujas)
clics_max = O["total"] / puja_media

# ================================================================== HTML
CSS = """
table{ width:100%; border-collapse:collapse; font-size:8pt; margin:1.5mm 0 3mm; }
th{ text-align:left; font-size:6.4pt; letter-spacing:.14em; text-transform:uppercase; color:var(--grey); font-weight:700; border-bottom:1.2pt solid var(--navy); padding:1.4mm 2mm 1.2mm 0; }
td{ border-bottom:.5pt solid var(--hair); padding:1.3mm 2mm 1.3mm 0; vertical-align:top; color:var(--ink); }
td.r, th.r{ text-align:right; font-variant-numeric:tabular-nums; }
td.mono{ font-family:Consolas,monospace; font-size:7.4pt; color:var(--navy); }
td b{ color:var(--navy); }
.h2{ font-size:15pt; margin:0 0 1.5mm; }
.h3{ font-size:10.5pt; margin:4mm 0 1.5mm; }
.lead2{ font-size:9pt; margin:0 0 3mm; color:var(--navy); }
.ok{ color:#1b1e42; }
.box{ background:var(--tint2); padding:3.5mm 4.5mm; margin:3mm 0; break-inside:avoid; }
.box h4{ font-size:9.6pt; margin:0 0 1.5mm; }
.box ul{ margin:0; padding-left:4mm; font-size:8.3pt; }
.box li{ margin-bottom:.8mm; }
.two{ display:grid; grid-template-columns:1fr 1fr; gap:5mm; }
.ad{ border:.6pt solid var(--hair); padding:3mm 3.5mm; break-inside:avoid; margin-bottom:3mm; }
.ad .g{ font-size:6.4pt; letter-spacing:.16em; text-transform:uppercase; color:var(--grey); font-weight:700; margin-bottom:1.5mm; }
.ad ol{ margin:0; padding-left:5mm; font-size:7.8pt; columns:2; column-gap:5mm; }
.ad ol li{ break-inside:avoid; }
.ad .d{ font-size:7.8pt; margin-top:1.5mm; color:var(--navy); }
.ad .pin{ color:var(--cyan); font-weight:700; }
.len{ color:var(--grey); font-size:6.6pt; }
.verdict{ break-inside:avoid; border-left:2pt solid var(--cyan); padding:2mm 0 2mm 4mm; margin:3mm 0; font-size:9.4pt; color:var(--navy); }
.src{ font-size:6.8pt; color:var(--grey); margin-top:1mm; }
"""


def doc(cuerpo, titulo):
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(titulo)}</title>
<link rel="stylesheet" href="../marca/cu/estilo-cu.css"><style>{CSS}</style></head><body>{cuerpo}</body></html>'''


def head(txt):
    return f'<div class="brandhead"><img src="../marca/cu/logos/control-union.svg" alt=""><div class="doc">{txt}</div></div>'


def move(i, t, p):
    return f'<div class="move"><div class="num">{i}</div><div><h3>{t}</h3><p>{p}</p></div></div>'


def fila(pp_t, pp, fix_t, fix, etiqueta="Hoy", etiqueta2="Cambio"):
    return (f'<div class="row"><div class="pp"><div class="t">{etiqueta}</div><h4>{pp_t}</h4><p>{pp}</p></div>'
            f'<div class="fix"><div class="t">{etiqueta2}</div><h4>{fix_t}</h4><p>{fix}</p></div></div>')


def tabla(cols, rows):
    th = "".join(f'<th class="{c[1]}">{c[0]}</th>' for c in cols)
    tr = "".join("<tr>" + "".join(f'<td class="{c[1]}">{v}</td>' for c, v in zip(cols, r)) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


def lista_anuncio(grupo, a, i):
    hs = "".join(f'<li>{"<span class=pin>📌 </span>" if j < 3 else ""}{e(t)} <span class="len">{len(t)}</span></li>' for j, t in enumerate(a["h"]))
    ds = "".join(f'<div class="d">{e(t)} <span class="len">{len(t)}/90</span></div>' for t in a["d"])
    return f'<div class="ad"><div class="g">{grupo} · RSA {i} · ruta /{a["p"][0]}/{a["p"][1]}</div><ol>{hs}</ol>{ds}</div>'


# ------------------------------------------------------------------ cambios que A puede proponer solo con los adjuntos
CAMBIOS_A = [
    ("Anuncios con 12 de 15 títulos", f"Las {O['rsa']} RSA usan {O['titulos']} títulos. Google combina mejor con los 15 y la fuerza del anuncio sube.",
     "Completar a 15 y fijar el stand en posición 1", "Tres títulos con «Booth #851» fijados en la posición 1: cada impresión dice dónde encontrarlos, que es el objetivo de la campaña."),
    ("UTM en la plantilla de seguimiento", "La plantilla de seguimiento ({lpurl}?utm…) está pensada para rastreadores externos; cada cambio vuelve a pasar por revisión.",
     "Pasar los UTM a «Sufijo de URL final»", "Mismo resultado en GA4, sin revisión al editar y sin redirecciones."),
    ("Callouts fuera del CSV y sin otros recursos", "Los textos destacados quedan para cargar a mano; no hay fragmento estructurado, formulario de clientes potenciales ni imágenes.",
     "Sumar fragmento, formulario e imágenes", "Fragmento «Service catalog» con los programas; formulario de Google «Meet Us at Booth #851» para agendar sin pasar por la landing; logo y fotos."),
    ("Sitelinks genéricos", "«About Control Union» y «Certification Services» no ayudan a quien busca el show; ninguno lleva directo a agendar.",
     "Sitelinks de acción y de programa", "«Schedule a Meeting» al formulario de la landing y sitelinks a los programas que más se buscan del rubro."),
    ("Negativas de asistente sin cubrir", "Las negativas cubren empleo, viaje y ser expositor, pero no la entrada al show: registro, tickets, badge, app, agenda, oradores.",
     "Negativas de entrada, proveedores y otras ferias", "registration, tickets, badge, app, agenda, speakers; armado de stands; vendedores de bases («attendee list», «email list»); otras ferias del rubro que entran por «produce trade show 2026»."),
    ("Faltan variantes del nombre", "No están «the global produce and floral show», «ifpa global produce and floral show», «ifpa 2026 orlando» ni el nombre anterior del show.",
     "Sumarlas en exacta y frase", "Son búsquedas del mismo asistente: baratas y muy relevantes."),
    ("Expositores con la puja más alta", "«exhibitor list» y «floor plan» los busca el asistente que arma su recorrido, pero también quien vende a expositores.",
     f"Bajar a ARS {n(V2.EXPO_PUJA)}", "Se mantiene la idea (muy buena: «Add Booth #851 to Your Plan»), con menos riesgo de pagar por prospección ajena."),
    ("Una sola conversión, sin respaldo", "Todo depende de que el envío del formulario de la landing se registre.",
     "Probar antes de lanzar y sumar el formulario de Google", "Tag Assistant sobre el formulario real; el formulario dentro del anuncio registra la conversión por sí solo."),
]

# ------------------------------------------------------------------ lo que solo se ve con todo el proyecto (B)
HALLAZGOS = [
    ("La expo abre solo jueves 15 y viernes 16",
     f"El cronograma oficial muestra el miércoles 14 con desayuno, State of the Industry y Education Festival; «Expo, All Halls Open» recién el 15 y el 16, de 10 a 17 h. "
     f"Los anuncios combinan la invitación al stand (#851) con «October 14-16» en {len(fechas_en_copy)} textos distintos, uno de ellos en la misma descripción. <span class=src>Fuente: {FUENTE_SHOW}, verificado el {VERIFICADO}.</span>",
     "Stand con fechas de expo", "«Booth #851, Expo Oct 15-16» y descripciones con «Expo floor open October 15-16». Las fechas del show (14 al 16) quedan solo para el evento. Conviene el mismo ajuste en la landing."),
    ("El formulario de la landing puede no registrarse",
     "La landing carga GTM con la etiqueta de la cuenta (" + CTX["cuenta"]["tag"] + "), pero el formulario es de HubSpot dentro de un iframe y con la redirección desactivada: no hay página de gracias ni envío visible para GTM. "
     f"En ago–sep la cuenta registró {form} envíos de formulario y {email} clics a email en {n(CTX['cuenta_ago_sep']['clics'])} clics.",
     "Probar y, si hace falta, escuchar el evento de HubSpot", "Tag Assistant con un envío real antes del 2/10. Si no dispara, en GTM un activador con el evento de envío de HubSpot. Respaldo: formulario de Google en el anuncio."),
    ("Conversiones primarias que no son contactos",
     f"La cuenta tiene como primarias «{'» y «'.join(prim_ruido)}», que cuentan varias por clic. Hoy no disparan, pero si se activan inflan la campaña y cualquier puja automática.",
     "Objetivos propios de la campaña", "Solo «Enviar formulario de clientes potenciales» y el formulario de Google. Así el informe del evento cuenta reuniones, no visitas."),
    ("El CPC real en EE.UU. es más alto que el del planificador",
     f"1 ago – 24 sep: USDA NOP ARS {n(cpc_nop[0])} por clic ({cpc_nop[1]} clics); PrimusGFS ARS {n(cpc_pri[0])} ({cpc_pri[1]} clics). En septiembre USDA NOP tuvo {round(nop_sep['cuota'] * 100)}% de cuota de impresiones y perdió {round(nop_sep['perdida_ranking'] * 100)}% por ranking.",
     "Pujas del evento se mantienen; marca aparte", f"Las keywords del show no compiten con certificadoras y el rango del planificador (ARS 3.542 a 4.561) es razonable. La marca va a ARS {n(V2.MARCA_PUJA)}: es propia y su nivel de calidad es alto."),
    ("La gente ya busca «control union» en EE.UU. y no hay anuncio",
     f"Search Console: «control union» {n(marca_cu_us['impressions'])} impresiones desde EE.UU. (posición {n(marca_cu_us['position'], 1)}), «control union usa» {n(marca_usa['impressions'])}; {n(marca_total_us)} en total con marca. "
     "Con la campaña de branding en Meta antes y durante el show, esa búsqueda sube; hoy aterriza en la home, sin el stand.",
     "Grupo MARCA_CU en exacta", "Durante 15 días quien busca la marca ve el stand y agenda. Es la conexión entre Meta y Search. Pagar por la marca solo se justifica por eso, y se apaga con la campaña."),
    ("PrimusGFS: hay demanda y ya hay campaña",
     f"«primusgfs» y variantes: {n(pri_us)} impresiones desde EE.UU., posición {n(pri_pos, 1)}. La campaña «CU United States - Organic - PrimusGFS» casi no publica ({cpc_pri[1]} clics en 8 semanas; {kp_raras} de {len(kp)} keywords con poco volumen; {round(pri_sep['perdida_ranking'] * 100)}% de impresiones perdidas por ranking en septiembre).",
     "No duplicar keywords; llevar el show a las campañas que ya existen", "Sitelink «Meet Us at Booth #851» y callouts con fecha en PrimusGFS y USDA NOP del 2 al 16. Copiar keywords haría competir dos campañas propias en la misma subasta."),
    ("México busca en su propio sitio, en español",
     f"El sitio de Norteamérica casi no recibe búsquedas desde México ({n(pri_mx_na)} impresiones de PrimusGFS). mexico.controlunion.com sí: PrimusGFS {n(MX['PrimusGFS'])}, SMETA {n(MX['SMETA'])}, GLOBALG.A.P. {n(MX['GLOBALG.A.P.'])} impresiones.",
     "México en la campaña, módulo en español aparte", "La campaña sigue mostrando a México las búsquedas del show en inglés. Un módulo en español para los programas solo tiene sentido con una versión en español de la landing."),
    ("El nombre de la campaña la deja fuera de nuestros informes",
     "La extracción mensual separa por marca con el prefijo «CU », y el tablero y la vista de gasto asignan país buscando «United States». «CU_US_SEARCH_GPFS-2026_EN» caería en «otros» y en «Sin asignar».",
     "«" + V2.CAMPANA + "»", f"El código original queda en utm_campaign ({V2.UTM_CAMPANA}) para GA4. Si el formato con guiones bajos es un estándar nuevo, se adaptan los scripts en lugar de renombrar."),
    ("La cuenta ya pagó por lo que las negativas evitan",
     f"«gfsi consultant» costó ARS {n(gfsi['coste'])} por {int(gfsi['clics'])} clics en PrimusGFS; {len(defin)} búsquedas de definición («what is», «how to») sumaron ARS {n(defin['coste'].sum())} en EE.UU. Control Union no consulta.",
     "Se confirman las negativas cruzadas y se suman las informativas", "consulting, consultant, advisory ya estaban: bien. Se agregan «what is», «meaning» y «membership»."),
    ("La app del show se busca como «GPFS 2026»",
     f"La web oficial indica: Search \"GPFS 2026\" to download. Esa keyword trae gente que busca la app. <span class=src>Fuente: {FUENTE_SHOW}, verificado el {VERIFICADO}.</span>",
     "Negativas app y download, y ficha en la app", "La keyword queda (es asistente), sin las búsquedas de descarga. Además, sin costo: perfil de Control Union en «My Show Planner» con enlace para agendar."),
]

TOP_A = [
    ("Completar los anuncios y fijar el stand", "15 títulos por anuncio; los del stand #851 fijados en la posición 1."),
    ("Cerrar las fugas de presupuesto", "Negativas de entrada al show, armado de stands, venta de bases y otras ferias."),
    ("Sumar recursos al anuncio", "Fragmento con los programas, formulario de Google para agendar, sitelinks de acción, imágenes."),
    ("UTM en el sufijo de URL", "Menos revisiones y redirecciones; misma lectura en GA4."),
    ("Probar la conversión antes de lanzar", "Un envío real del formulario con Tag Assistant."),
]
TOP_B = [
    ("Corregir las fechas del stand", "La expo abre el 15 y el 16; hoy el anuncio invita al stand del 14 al 16."),
    ("Asegurar que se cuenten las reuniones", "Formulario de HubSpot en iframe: probar, escuchar el evento en GTM y usar objetivos propios de la campaña."),
    ("Conectar Meta con Search por la marca", f"«control union» ya tiene {n(marca_cu_us['impressions'])} impresiones en EE.UU.; con Meta van a crecer y hoy no tienen anuncio."),
    ("Llevar el show a PrimusGFS y USDA NOP", "Sitelink y callouts con fecha en las campañas que ya existen, sin duplicar keywords."),
    ("Nombre que entienden nuestros informes", "«" + V2.CAMPANA + "» para verla en el tablero y en la extracción mensual."),
]


def portada(version, titulo, sub, nums, top):
    hn = "".join(f'<div><div class="n">{a}</div><div class="l">{b}</div></div>' for a, b in nums)
    mv = "".join(move(i, t, p) for i, (t, p) in enumerate(top, 1))
    return f'''<div class="cover">{head("Campaña de búsqueda · Global Produce &amp; Floral Show<br>Octubre 2026")}
<div class="hero"><div class="eyebrow">{version}</div><h1>{titulo}</h1><p class="sub">{sub}</p>
<div class="hero-nums">{hn}</div></div>
<div class="top5"><h2>Los cinco cambios que más pesan</h2>{mv}</div></div>'''


def bloque_campana_v2():
    cfg = tabla([("Elemento", ""), ("Valor", "")], [
        ("Nombre", f"<b>{e(V2.CAMPANA)}</b> (utm_campaign {V2.UTM_CAMPANA})"),
        ("Red", "Solo Búsqueda de Google, sin socios de búsqueda ni Display"),
        ("Fechas y presupuesto", f"{V2.INICIO} al {V2.FIN} · ARS {n(V2.PRESUPUESTO_DIA)} por día · ARS {n(V2.PRESUPUESTO_DIA * 15)} en total"),
        ("Puja", "CPC manual sin CPC mejorado: no hay historial de conversiones para automatizar en 15 días"),
        ("Ubicación", "Presencia: EE.UU. y México 0%, Canadá −30%, <b>Orlando +25%</b> (asistentes ya en la ciudad)"),
        ("Idiomas", "Inglés y español (el anuncio en inglés también llega a quien tiene Google en español)"),
        ("Conversiones", "Objetivos propios de la campaña: formulario de la landing + formulario de Google"),
        ("Seguimiento", "Sufijo de URL final por grupo (utm_content = grupo, utm_term = keyword); auto-tagging activo"),
    ])
    kw_rows = []
    for gname, d in V2.GRUPOS.items():
        kws_txt = ", ".join(f"{'[' + k + ']' if t == 'Exact' else chr(34) + k + chr(34)}" for k, t, _ in d["kw"])
        pujas_g = sorted({p for _, _, p in d["kw"]})
        kw_rows.append((f"<b>{gname}</b>", e(d["intencion"]), f'<span style="font-size:7.4pt">{e(kws_txt)}</span>', " / ".join(n(p) for p in pujas_g)))
    grupos = tabla([("Grupo", ""), ("Intención", ""), ("Keywords ([exacta], «frase»)", ""), ("Puja ARS", "r")], kw_rows)
    ads = "".join(lista_anuncio(gname, a, 1) for gname, ads_g in V2.ANUNCIOS.items() for a in ads_g[:1])
    rec = tabla([("Recurso", ""), ("Contenido", "")], [
        ("Callouts", " · ".join(e(c) for c in V2.CALLOUTS)),
        ("Sitelinks", "<br>".join(f"<b>{e(s[0])}</b>: {e(s[1])} / {e(s[2])}" for s in V2.SITELINKS)),
        ("Fragmento estructurado", f"{V2.SNIPPET[0]}: {', '.join(V2.SNIPPET[1])}"),
        ("Formulario de Google", f"«{e(V2.LEAD_FORM['titulo'])}» · {', '.join(V2.LEAD_FORM['campos'])} · «{e(V2.LEAD_FORM['pregunta'][0])}» (jueves 15 / viernes 16)"),
        ("Llamada", "+1 954-613-8725, solo si alguien atiende durante el show"),
        ("Imágenes", "Logo cuadrado y 2 o 3 fotos del stand o del equipo"),
    ])
    negs = tabla([("Motivo", ""), ("Negativas nuevas (además de las " + str(len(V2.NEG_ORIGINAL)) + " del original)", "")],
                 [(e(k), e(", ".join(x.strip('"') for x in v))) for k, v in V2.NEG_NUEVAS.items()])
    n_kw = sum(len(d["kw"]) for d in V2.GRUPOS.values())
    return f'''<div class="page">{head("Versión B · campaña propuesta")}
<h2 class="sec-title">La campaña completa</h2>
<p class="sec-sub">{len(V2.GRUPOS)} grupos, {n_kw} keywords, {sum(len(a) for a in V2.ANUNCIOS.values())} anuncios y {len(V2.NEG_ORIGINAL) + sum(len(v) for v in V2.NEG_NUEVAS.values())} negativas. Archivo para Google Ads Editor: <b>campanas/gpfs-2026/CU_US_GPFS-2026_v2.csv</b>; lo que se carga a mano, en <b>LEEME_v2_ARS.md</b>.</p>
<h3 class="h3">Configuración</h3>{cfg}
<h3 class="h3">Grupos y keywords</h3>{grupos}</div>
<div class="page">{head("Versión B · anuncios y recursos")}
<h2 class="sec-title">Anuncios</h2>
<p class="sec-sub">Una RSA por grupo (la segunda, con los mismos títulos del stand y el resto orientado a programas, está en el CSV). 📌 = fijado en posición 1. El número es el largo (máx. 30). Sin «IFPA» ni el nombre del show en el texto: es marca de un tercero y puede limitar la publicación; las keywords sí lo nombran.</p>
<div class="two">{ads}</div>
<h3 class="h3">Recursos</h3>{rec}
<h3 class="h3">Negativas</h3>{negs}</div>'''


# ================================================================== informe A
filas_a = "".join(fila(e(a), e(b), e(c), e(d)) for a, b, c, d in CAMBIOS_A)
bien = ["Concordancia exacta y de frase, sin amplia: correcto para 15 días sin historial.",
        "CPC manual sin CPC mejorado: no hay conversiones previas con las que automatizar.",
        "Ubicación por presencia, con Canadá en segundo plano (−30%).",
        "Tres grupos por intención (nombre del show, ciudad, expositores), cada uno con su UTM.",
        "Negativas cruzadas de marca (consulting, advisory, training): Control Union certifica, no consulta.",
        "Una sola landing del evento con un llamado claro: agendar una reunión.",
        f"Copy dentro de los límites (máximo {O['largo_max_t']}/30 y {O['largo_max_d']}/90) y con el vocabulario de Control Union: certify, audit, verify."]
no_ve = ["Si las fechas del texto coinciden con los días en que abre la expo.",
         "Si el formulario de la landing registra la conversión en Google Ads.",
         "Qué conversiones están configuradas en la cuenta y cuáles cuentan como primarias.",
         "Cuánto cuesta de verdad un clic en EE.UU. en esta cuenta.",
         "Si ya se busca la marca, ni si otras campañas propias compiten por las mismas búsquedas.",
         "Si el nombre de la campaña entra en la extracción mensual y en el tablero."]
A = portada("Versión A · solo con los archivos adjuntos", "Global Produce &amp; Floral Show 2026: revisión de la campaña",
            "Lectura de todo-junto.csv y LEEME_ARS.md con buenas prácticas de Google Ads, sin abrir la cuenta, el sitio ni la web del show. Sirve para comparar con la versión B y ver cuánto agrega el resto del proyecto.",
            [(O["grupos"], "grupos de anuncios"), (O["kw"], "keywords"), (O["rsa"], "anuncios RSA"), ("ARS " + n(O["total"]), "en 15 días")], TOP_A)
A += f'''<div class="page">{head("Versión A · diagnóstico")}
<h2 class="sec-title">Lo que está bien</h2><p class="sec-sub">La base es sólida: estructura, concordancias y estrategia de puja son las correctas para una campaña corta de evento.</p>
<div class="box"><ul>{"".join(f"<li>{e(x)}</li>" for x in bien)}</ul></div>
<h2 class="sec-title" style="margin-top:5mm">Lo que conviene cambiar</h2>{filas_a}</div>
<div style="margin-top:6mm">
<h2 class="sec-title">Lo que esta versión no puede ver</h2>
<p class="sec-sub">Con solo los dos archivos, estas preguntas quedan sin respuesta. Cualquiera de ellas puede cambiar el resultado más que todo lo anterior.</p>
<div class="box"><ul>{"".join(f"<li>{e(x)}</li>" for x in no_ve)}</ul></div>
<div class="navy-box"><h4>Resultado esperable con esta versión</h4><p>Una campaña más limpia y mejor armada: más títulos, menos clics perdidos en entradas y logística, recursos completos. Pero las decisiones que dependen de datos (fechas, medición, marca, superposición con otras campañas) quedan como supuestos.</p></div>
<p class="foot">Documento interno de Control Union North America · campaña de búsqueda para The Global Produce &amp; Floral Show 2026. Fuentes: todo-junto.csv y LEEME_ARS.md (1 oct 2026). Montos en ARS, moneda de la cuenta.</p></div>'''

# ================================================================== informe B
filas_b = "".join(fila(t, p, ft, fp, "Lo que encontramos", "Qué cambia") for t, p, ft, fp in HALLAZGOS)
comparacion = [
    ("Fechas del stand", "No lo ve", "Corrige el texto: la expo abre 15 y 16", "Alto: evita invitar al stand un día sin expo"),
    ("Medición de reuniones", "Recomienda probar", "Detecta el iframe de HubSpot sin página de gracias y las primarias que no son contactos", "Alto: sin esto, la campaña no se puede evaluar"),
    ("Marca y Meta", "No lo ve", f"Grupo de marca: {n(marca_cu_us['impressions'])} impresiones de «control union» en EE.UU.", "Medio-alto: aprovecha la inversión de Meta"),
    ("Otras campañas propias", "No lo ve", "PrimusGFS y USDA NOP llevan el show sin duplicar keywords", "Medio: más alcance sin presupuesto nuevo"),
    ("Pujas", "Usa el planificador", f"Lo compara con el CPC real de la cuenta (ARS {n(cpc_nop[0])} en USDA NOP)", "Medio: confirma pujas y fija la de marca"),
    ("México", "Ve el idioma", f"Ubica la demanda en el sitio de México (SMETA {n(MX['SMETA'])}, PrimusGFS {n(MX['PrimusGFS'])})", "Medio: decide el módulo en español"),
    ("Nombre de la campaña", "No lo ve", "Lo alinea con la extracción y el tablero", "Operativo: sin esto no aparece en los informes"),
    ("Negativas", "Agrega las de buenas prácticas", "Suma las que la cuenta ya pagó y las de la app del show", "Bajo-medio"),
    ("Anuncios y recursos", "Completa", "Igual que A, con fechas correctas y recursos con fecha de fin", "Igual"),
]
comp = tabla([("Tema", ""), ("Versión A", ""), ("Versión B", ""), ("Impacto", "")], [tuple(e(x) for x in r) for r in comparacion])
limites = [
    "El Planificador de palabras clave por API no está habilitado para la cuenta (acceso «explorer»): los volúmenes y rangos de puja del evento son los del archivo, sacados del planificador a mano.",
    f"Search Console llega hasta el 14 sep 2026; la landing del evento {'ya' if landing_en_gsc else 'todavía no'} figura con datos propios.",
    f"Las búsquedas del show no aparecen en orgánico ({len(ev)} consultas): el sitio no rankea para el evento, por eso se compra.",
    "Las conversiones de la cuenta son pocas (" + str(form) + " formularios en dos meses): sirven para revisar la medición, no para estimar una tasa del evento.",
    "No hay acceso al contenedor de GTM: que el formulario no se registre es un riesgo a probar, no un hecho comprobado.",
]
B = portada("Versión B · completa, con todo el proyecto", "Global Produce &amp; Floral Show 2026: la campaña completa",
            "Lo mismo que la versión A más la web oficial del show, la landing, la cuenta de Google Ads (solo lectura), Search Console de Norteamérica y México, y el resto del proyecto. Incluye la campaña lista para importar.",
            [("15-16 oct", "únicos días con la expo abierta"), (n(marca_cu_us["impressions"]), "impr. de «control union» en EE.UU."),
             ("ARS " + n(cpc_nop[0]), "CPC real en EE.UU. (USDA NOP)"), (f"{n(tasa_form, 2)}%", "clics que terminan en formulario")], TOP_B)
B += f'''<div class="page">{head("Versión B · hallazgos")}
<h2 class="sec-title">Lo que aparece al cruzar con el resto del proyecto</h2>
<p class="sec-sub">Diez hallazgos que no se ven en los archivos. Cada uno con su evidencia y el cambio que produce en la campaña.</p>{filas_b}</div>'''
B += bloque_campana_v2()
B += f'''<div class="page">{head("Versión B · medición y comparación")}
<h2 class="sec-title">Qué esperar y cómo medirlo</h2>
<p class="sec-sub">Con una puja media de ARS {n(puja_media)}, el presupuesto alcanza para unos {n(clics_max)} clics si hay búsquedas suficientes; las del show crecen la semana anterior y durante la expo.</p>
<div class="two"><div class="box"><h4>Indicadores</h4><ul>
<li><b>Reuniones agendadas</b>: formulario de la landing + formulario de Google. Es el resultado.</li>
<li><b>Costo por reunión</b>: inversión ÷ reuniones.</li>
<li><b>Cuota de impresiones</b> de las keywords del show: si queda bajo 50% en la parte superior, subir la puja.</li>
<li><b>Búsquedas de «control union» en EE.UU.</b> en octubre contra septiembre (Search Console): mide lo que suman Meta y el show.</li></ul></div>
<div class="box"><h4>Calendario</h4><ul>
<li><b>1 oct</b>: importar, probar la conversión, publicar (la revisión tarda hasta un día hábil).</li>
<li><b>4 oct</b>: términos de búsqueda a las 48 h; negativas nuevas.</li>
<li><b>13 oct</b>: última revisión antes del show; pujas de lo que rinde.</li>
<li><b>15 y 16 oct</b>: revisión a la mañana (Orlando +25%).</li>
<li><b>Después</b>: informe de reuniones y búsquedas de marca.</li></ul></div></div>
<p class="sec-sub" style="margin-top:2mm">Referencia de la cuenta: en ago–sep {n(form)} formularios en {n(CTX["cuenta_ago_sep"]["clics"])} clics ({n(tasa_form, 2)}%). A esa tasa, {n(clics_max)} clics darían menos de un formulario: la campaña se justifica porque la landing del evento pide algo concreto (una reunión en el stand) y porque el contacto también se cierra en persona. Es un supuesto a confirmar con los datos del show.</p>
<h2 class="sec-title" style="margin-top:4mm">¿Valió la pena la versión completa?</h2>{comp}
<div class="verdict"><b>Sí.</b> La versión A mejora la forma de la campaña; la B cambia decisiones. Dos de sus hallazgos (las fechas del stand y la medición de reuniones) definen si la campaña invita al lugar correcto y si se puede saber cuánto rindió, y ninguno se podía ver desde los archivos.</div>
<div class="box"><h4>Límites de los datos</h4><ul>{"".join(f"<li>{e(x)}</li>" for x in limites)}</ul></div>
<p class="foot">Documento interno de Control Union North America. Fuentes: todo-junto.csv y LEEME_ARS.md; {FUENTE_SHOW} y la landing del evento (verificados el {VERIFICADO}); Google Ads por API en solo lectura ({ctx_ruta}; anuncios y términos 1 ago – 24 sep 2026); Search Console histórico hasta el 14 sep 2026. Montos en ARS, moneda de la cuenta.</p></div>'''

open(os.path.join(INF, "gpfs-2026-A.html"), "w", encoding="utf-8").write(doc(A, "GPFS 2026 · Versión A"))
open(os.path.join(INF, "gpfs-2026-B.html"), "w", encoding="utf-8").write(doc(B, "GPFS 2026 · Versión B"))
print("-> informe/gpfs-2026-A.html, informe/gpfs-2026-B.html")
print(dict(fechas_en_copy=len(fechas_en_copy), form=form, tasa=round(tasa_form, 2), cpc_nop=round(cpc_nop[0]), cpc_pri=round(cpc_pri[0]),
           marca=int(marca_cu_us["impressions"]), marca_total=marca_total_us, pri_us=pri_us, pri_pos=round(pri_pos, 1), MX=MX, ev=len(ev),
           gfsi=round(gfsi["coste"]), defin=(len(defin), round(defin["coste"].sum())), clics_max=round(clics_max), puja_media=round(puja_media), raras=(kp_raras, len(kp))))
