# -*- coding: utf-8 -*-
"""
generar_plan_unificado.py — plan de mejoras unificado y actualizado al 24 de septiembre de 2026.
Una sola pieza, neutra (cubre las dos marcas): Control Union → ISO 27001 (PCU) → Peterson Solutions.
Cada pain point lleva su mejora y su estado: Pendiente (propuesto en la auditoría y no aplicado),
Nuevo (surge de los datos por API), Hecho, Decisión.
Fuentes: informe/datos_estado.json, datos_clientes.json, datos_informe.json, datos_relacion_*.json
"""
import json, os
from informe_util import n, pct, ars, e, hoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
E = json.load(open(os.path.join(INF, "datos_estado.json"), encoding="utf-8"))
C = json.load(open(os.path.join(INF, "datos_clientes.json"), encoding="utf-8"))
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))
SEO = json.load(open(os.path.join(INF, "datos_seo.json"), encoding="utf-8"))
R2 = json.load(open(os.path.join(INF, "datos_relacion_2026-09-12_2026-09-24.json"), encoding="utf-8"))
T = E["totales"]; PM = E["por_marca"]
CAMP = {c["campana"]: c for c in E["campanas"]}
U = {(c["propiedad"], c["pais"]): c for c in C["clientes"]}
S = {s["propiedad"]: s for s in C["sin_campana"]}
s7 = D["s7"]
HOY = hoy()


def cp(nombre):
    return next(v for k, v in CAMP.items() if k.startswith(nombre))


def dia(c):
    return ars(c["coste_dia_post"])


def row(pain, pain_txt, fix, fix_txt, estado="Pendiente"):
    cls = {"Pendiente": "", "Nuevo": " new", "Hecho": " ok", "Decisión": " dec"}[estado]
    return (f'<div class="row"><div class="pp"><div class="t">Pain point</div><h4>{pain}<span class="tag{cls}">{e(estado)}</span></h4><p>{pain_txt}</p></div>'
            f'<div class="fix"><div class="t">Mejora</div><h4>{fix}</h4><p>{fix_txt}</p></div></div>')


def unit(brand, titulo, sub, nums, lead, rows):
    ns = "".join(f'<div><div class="v">{v}</div><div class="k">{e(k)}</div></div>' for v, k in nums)
    return f'''<div class="unit"><div class="unit-bar"><div><div class="brand">{e(brand)}</div><h2>{e(titulo)}</h2>{f'<div class="sub">{e(sub)}</div>' if sub else ''}</div><div class="nums">{ns}</div></div>
 <p class="lead">{lead}</p>{"".join(rows)}</div>'''


def rel(c):
    r = c.get("rel_post") or {}
    return r.get("pct_fuerte"), r.get("pct_nula")


# ================================================================== datos derivados
nuevas = [c for c in E["campanas"] if c["nueva"]]
aplicadas_a = sum(1 for c in E["campanas"] if c["anexo_a"] and c["anexo_a"]["aplicados"])
prop_a = sum(1 for c in E["campanas"] if c["anexo_a"])
aplicadas_b = sum(1 for c in E["campanas"] if c["anexo_b"] and c["anexo_b"]["aplicadas"])
prop_b = sum(1 for c in E["campanas"] if c["anexo_b"])
iso_es, iso_ar = cp("PCU España - ISO 27001"), cp("PCU Argentina - ISO 27001")
comp_es, comp_ar = cp("PCU España - Competidores"), cp("PCU Argentina - Competidores")
iso_dia = iso_es["coste_dia_post"] + iso_ar["coste_dia_post"] + comp_es["coste_dia_post"] + comp_ar["coste_dia_post"]
fo, aq, cg, gg = cp("CU Canada - Forestry"), cp("CU Canada- Aqua"), cp("CU Canada - Canada Gap"), cp("CU Canada - GLOBALG.A.P.")
nop, prim = cp("CU United States - Organic - USDA NOP"), cp("CU United States - Organic - PrimusGFS")
cae, ifs, tex, forl, sme, gmp, bio_es = cp("CU España - CAEs"), cp("CU España - IFS"), cp("CU España - Textile"), cp("CU España - Forestal"), cp("CU España - Smeta"), cp("CU España - GMP+"), cp("CU España - Bioenergia")
pt_pla, pt_for, pt_tex, pt_gmp, pt_bio = cp("CU Portugal - Plasticos"), cp("CU Portugal - Forestal"), cp("CU Portugal - Textile"), cp("CU Portugal - GMP+"), cp("CU Portugal - Biomasa")
ar_eudr, ar_bio, ar_ghg, ar_ind, ar_coc, ar_agro = cp("CU Argentina - Agroexportación"), cp("CU Argentina - Biocombustible"), cp("CU Argentina - GHG"), cp("CU Argentina - Industria"), cp("CU Argentina - Cadena"), cp("CU Argentina - Agro sost")
ps_ag, ps_hc, ps_esg, ps_bio, ps_ha, ps_ce, ps_eudr = cp("PS Argentina - SuSo - Agricultura"), cp("PS Argentina - SuSe - Huella de carbono"), cp("PS Argentina - SuSe - ESG"), cp("PS Argentina - Bioenergia"), cp("PS Argentina - SuSe - Huella de agua"), cp("PS Argentina - CeSu"), cp("PS Argentina - SuSo - Trazabilidad")


def suma_dia(prefijo):
    return sum(c["coste_dia_post"] for c in E["campanas"] if c["campana"].startswith(prefijo))


def conv(prefijo):
    return sum(c["conv_post"] for c in E["campanas"] if c["campana"].startswith(prefijo))


def relm(m, key):
    return next((x for x in (PM[m]["relacion_post"] or []) if x["relacion_anuncio"] == key), {"pct": 0})["pct"]


# ================================================================== portada
cover = f'''<div class="cover">
 <div class="hero">
  <div class="eyebrow">Plan de mejoras · campañas de búsqueda · Control Union → ISO 27001 → Peterson Solutions · actualizado al 24 sep 2026</div>
  <h1>Qué está mal en cada campaña, qué se propuso, qué se hizo y qué apareció nuevo</h1>
  <p class="sub">La cuenta cambió más que las campañas: el gasto diario se multiplicó por {n(T["dia_post"] / T["dia_aud"], 1)} desde la auditoría, aparecieron {n(T["nuevas"])} campañas y casi ninguna de las mejoras propuestas se aplicó. Este plan parte de lo que hay hoy, leído por API.</p>
  <div class="hero-nums">
   <div><div class="n">{ars(T["dia_aud"])} → {ars(T["dia_post"])}</div><div class="l">gasto por día · auditoría vs 12–24 sep</div></div>
   <div><div class="n">{n(T["conv_post"])}</div><div class="l">conversiones en 13 días ({n(T["conv_aud"])} en las 6 semanas previas)</div></div>
   <div><div class="n">{aplicadas_a} de {prop_a}</div><div class="l">campañas con negativos propuestos que aplicaron alguno</div></div>
   <div><div class="n">{n(T["nuevas"])}</div><div class="l">campañas nuevas, todas de Control Union Argentina</div></div>
  </div>
 </div>
 <div class="top5"><h2>Las cinco mejoras que más pesan hoy</h2>
  <div class="move"><div class="num">1</div><div><h3>ISO 27001 pasó a ser la mitad de la cuenta y hay que decidir de qué marca es</h3><p>{ars(iso_dia)} por día entre España y Argentina, {n(iso_es["conv_post"] + iso_ar["conv_post"])} conversiones en 13 días, relación anuncio-término fuerte. Funciona. Pero se llama «PCU» y el manual no admite una campaña sin marca: certifica Control Union.</p></div></div>
  <div class="move"><div class="num">2</div><div><h3>Aplicar lo que ya estaba decidido y no se hizo</h3><p>Negativos de la auditoría en {prop_a - aplicadas_a} campañas, exactas en {prop_b - aplicadas_b}, grupo FSC en España y Portugal, pausa de Forestry y Aqua. Nada de eso requiere una decisión nueva.</p></div></div>
  <div class="move"><div class="num">3</div><div><h3>SMETA España compra nombres de competidores</h3><p>Pasó de {ars(sme["coste_dia_aud"])} a {ars(sme["coste_dia_post"])} por día y el 80% del gasto visible es Intertek, TÜV SÜD, DNV, Veolia: la keyword «smeta auditoria» en frase abrió la puerta.</p></div></div>
  <div class="move"><div class="num">4</div><div><h3>USDA NOP triplicó el gasto en búsquedas de definición</h3><p>{ars(nop["coste_dia_post"])} por día, cero conversiones. «what does certified organic mean» costó ARS 18.726 por dos clics.</p></div></div>
  <div class="move"><div class="num">5</div><div><h3>Peterson: las mismas cuatro campañas, ahora con más presupuesto en la peor</h3><p>Huella de agua pasó de {ars(ps_ha["coste_dia_aud"])} a {ars(ps_ha["coste_dia_post"])} por día con el 100% del gasto visible fuera de foco. Bioenergía se duplicó y sigue en biogás.</p></div></div>
 </div>
 <p class="foot">Documento interno sin identidad de marca: cubre campañas de Control Union y de Peterson Solutions, y el manual del grupo no admite piezas que combinen ambas marcas; cada mejora se ejecuta dentro de su marca. Fuentes: Google Ads por API (estructura al 25 sep; métricas 1 ago – 11 sep y 12 – 24 sep 2026) y Search Console (histórico completo). Generado el {HOY}.</p>
</div>'''

# ================================================================== qué cambió
top = sorted([c for c in E["campanas"] if c["coste_post"] > 0], key=lambda c: -c["coste_post"])[:14]
filas = ""
for c in top:
    f, nu = rel(c)
    filas += (f'<tr><td>{e(c["campana"].replace(" - Search", "").replace(" - SEARCH", ""))}{" <span class=\'tag new\'>nueva</span>" if c["nueva"] else ""}</td>'
              f'<td class="num">{ars(c["coste_dia_aud"]) if c["coste_dia_aud"] else "—"}</td><td class="num"><b>{ars(c["coste_dia_post"])}</b></td>'
              f'<td class="num">{n(c["coste_dia_post"] / c["coste_dia_aud"], 1) + "×" if c["coste_dia_aud"] else "—"}</td>'
              f'<td class="num">{n(c["conv_post"])}</td><td class="num">{pct(f) if f is not None else "—"}</td><td class="num">{pct(nu) if nu is not None else "—"}</td></tr>')
cambios = f'''<div class="page">
 <h2 class="sec-title">Qué cambió desde la auditoría</h2>
 <p class="sec-sub">Estructura de la cuenta leída por API el 25 de septiembre y métricas del 12 al 24, contra las seis semanas de la auditoría. Gasto por día para que las dos ventanas sean comparables.</p>
 <table class="tbl"><thead><tr><th>Campaña</th><th class="num">Antes · día</th><th class="num">Ahora · día</th><th class="num">×</th><th class="num">Conv. 13 d</th><th class="num">Anuncio fuerte</th><th class="num">Anuncio nulo</th></tr></thead><tbody>{filas}</tbody></table>
 <p class="small">Las 14 campañas de mayor gasto actual. «Anuncio fuerte / nulo»: parte del gasto visible cuyos términos de búsqueda aparecen completos en algún título del anuncio, o en ninguno.</p>
 <div class="g3">
  <div><h4>Lo que se hizo</h4><p>Se retiró la campaña de Cannabis en Canadá. PrimusGFS dejó de gastar y sumó la exacta [primusgfs]. Forestry sumó «training» y «job» a negativos. ISO 27001 en España y Argentina se renombró «PCU» y su presupuesto pasó de ARS 2.500 a ARS 15.300 y 12.750 por día.</p></div>
  <div><h4>Lo que no se hizo</h4><p>De {prop_a} campañas con negativos propuestos, {aplicadas_a} aplicaron alguno. De {prop_b} con exactas propuestas, {aplicadas_b}. No hay grupo FSC en España ni Portugal, no hay campaña ISO 45001 ni TEMO, Forestry y Aqua siguen activas y gastan más, «consultant» sigue sin ser negativo de cuenta en Control Union.</p></div>
  <div><h4>Lo nuevo</h4><p>Seis campañas de Control Union Argentina: EUDR, ISCC/2BSvs, FSC, GHG, SMETA/FSSC y RTRS/FSA. Bien orientadas en general, con tres detalles que se corrigen abajo. SMETA España abrió a competidores. USDA NOP se triplicó. El gasto diario de la cuenta pasó de {ars(T["dia_aud"])} a {ars(T["dia_post"])}.</p></div>
 </div>
  <div class="navy-box"><h4>Cómo saber si funcionó, en 30 días</h4>
  <p>Gasto con anuncio nulo por debajo del <b>10%</b> en cada marca (hoy {pct(relm("cu","nula"))} Control Union, {pct(relm("ps","nula"))} Peterson, {pct(relm("pcu","nula"))} ISO 27001). Negativos de la auditoría aplicados en las {prop_a} campañas. Forestry, Aqua, Huella de agua, Bioenergía y CeSu en pausa. Y que el gasto por día vuelva a estar explicado por campañas que convierten: hoy ISO 27001 y Plásticos España traen 5 de las 6 conversiones.</p></div>
</div>'''

# ================================================================== CONTROL UNION
es = unit("Control Union", "España", None,
          [(ars(suma_dia("CU España")), "gasto por día"), (n(conv("CU España")), "conv. 13 d"), ("9", "campañas")],
          f"Las cuatro mejoras de la auditoría siguen pendientes, y apareció un problema nuevo en SMETA, que ahora es la campaña que más gasta de la unidad.", [
    row("SMETA compra nombres de competidores", f"De {ars(sme['coste_dia_aud'])} a {ars(sme['coste_dia_post'])} por día. El 80% del gasto visible son Intertek, TÜV SÜD, DNV, Veolia, «cuadro comparativo iso 9001 14001 45001». Entra por «smeta auditoria» en frase.",
        "Negativos de competidores y exacta", "intertek, tüv, dnv, veolia, sgs, bureau veritas, aenor a negativo. «smeta auditoria» a exacta. Sumar [smeta], [sedex], [auditoria smeta].", "Nuevo"),
    row("CAEs sigue comprando certificados de vivienda", f"{ars(cae['coste_dia_post'])} por día. Ninguno de los seis negativos propuestos está aplicado; la amplia sigue en amplia.",
        "Aplicar el Anexo A", "vivienda, particular, gratis, ce3x, certicalia, online a negativo. Amplia a frase. Exactas [sistema CAE], [verificación de actuaciones CAE].", "Pendiente"),
    row("IFS: genéricos y sin exactas", f"{ars(ifs['coste_dia_post'])} por día con las mismas 9 keywords. Solo «curso» está en negativos.",
        "Nombrar la norma", "[ifs food], [certificado ifs], [norma ifs]. Grupos ISO 22000 y FSSC 22000. servsafe, manipulación, food handler a negativo.", "Pendiente"),
    row("Textile paga OEKO-TEX y Forestal compra «sostenibilidad»", f"oeko tex sigue sin ser negativo. En Forestal ({ars(forl['coste_dia_post'])} por día, el doble) la keyword «pefc certification» trae «sostenibilidad» a secas: ARS 6.284 en 13 días. Sigue sin grupo FSC.",
        "Negativos, exacta y grupo FSC", "oeko tex, organic cotton standard a negativo en Textile. En Forestal: «pefc certification» a exacta, sostenibilidad y pymes a negativo, grupo FSC con su página.", "Pendiente"),
    row("GMP+ empezó a gastar sin reconstruirse", f"{ars(gmp['coste_dia_post'])} por día con las 31 keywords originales, 2 clics. Orgánico: {n(s7['gmp_es']['impresiones'])} búsquedas en posición {n(s7['gmp_es']['pos'],1)}.",
        "Reconstruir sobre lo que se busca", "[gmp+], [gmp plus], [feed safety], [certificacion gmp]. Pausar el resto.", "Pendiente"),
    row("ISO 45001, la mayor demanda, sigue sin campaña", f"{n(s7['iso45001_es']['impresiones'])} búsquedas orgánicas con página propia. En seis semanas se abrieron seis campañas en Argentina y ninguna acá.",
        "Campaña ISO 45001", "Sobre la página existente, en exacta, con el modelo de la de ISO 27001 que ya convierte.", "Pendiente"),
])

pt = unit("Control Union", "Portugal", None,
          [(ars(suma_dia("CU Portugal")), "gasto por día"), (n(conv("CU Portugal")), "conv. 13 d"), ("7", "campañas")],
          f"El gasto se triplicó ({ars(suma_dia('CU Portugal'))} por día) sin que cambie la estructura. Las tres mejoras siguen pendientes; Biomasa empezó a gastar.", [
    row("Plásticos sigue pagando recyclass, que rankea 3º", f"{ars(pt_pla['coste_dia_post'])} por día, cuatro veces la auditoría. La posición orgánica no cambió.",
        "Exacta con tope, 30 días", "recyclass a exacta con CPC máximo bajo. Si el clic orgánico compensa, pausar.", "Pendiente"),
    row("FSC entra por PEFC · GMP+ vacía · Biomasa despertó", f"Sin grupo FSC. GMP+ con 24 keywords y cero gasto. Biomasa pasó de {ars(pt_bio['coste_dia_aud'])} a {ars(pt_bio['coste_dia_post'])} por día con 6 clics.",
        "Grupo FSC · GMP+ rehecha · revisar Biomasa", "Grupo FSC con landing propia. GMP+ con [gmp+], [gmp plus]. Biomasa: mirar términos antes de que se consolide.", "Pendiente"),
    row("Textile: bien, con ruido nuevo", f"{ars(pt_tex['coste_dia_post'])} por día, 89% del gasto con anuncio fuerte o parcial. «ppwr» y «wordly» entran por GRS e Higg.",
        "Negativos chicos", "ppwr, wordly, database a negativo. Exactas [gots], [gots certification], [grs portugal].", "Nuevo"),
])

ca = unit("Control Union", "Canadá", None,
          [(ars(suma_dia("CU Canada")), "gasto por día"), (n(conv("CU Canada")), "conv. 13 d"), ("5", "campañas")],
          "Las dos pausas decididas no se ejecutaron: Forestry gasta más que en la auditoría y Aqua se duplicó. Cero conversiones en 13 días.", [
    row("Forestry y Aqua siguen activas", f"Forestry {ars(fo['coste_dia_post'])} por día (+{pct((fo['coste_dia_post']/fo['coste_dia_aud']-1)*100)}), Aqua {ars(aq['coste_dia_post'])} (×{n(aq['coste_dia_post']/aq['coste_dia_aud'],1)}). El sitio sigue sin contenido forestal ni acuícola para Canadá.",
        "Pausar", f"Pausar las dos. El presupuesto va a TEMO ({n(s7['temo_na']['impresiones'])} búsquedas orgánicas, sin campaña) y a CanadaGAP limpia.", "Pendiente"),
    row("CanadaGAP y GLOBALG.A.P. sin los negativos", f"CanadaGAP {ars(cg['coste_dia_post'])} por día, ninguno de los cuatro negativos aplicado. GLOBALG.A.P. se quintuplicó a {ars(gg['coste_dia_post'])}.",
        "Aplicar y acotar", "supply chain management, indocert, consultant, cargill a negativo. Exactas [canada gap], [canadagap], [global gap certification].", "Pendiente"),
    row("Cannabis se retiró; cumcs rankea 2º sin campaña", "La campaña de Cannabis fue eliminada. Orgánicamente «cumcs» tiene 1.107 búsquedas en posición 1,9.",
        "Campaña de defensa cumcs", "Grupo chico en exacta sobre la página del estándar, con la landing UTM que ya existía.", "Nuevo"),
])

us = unit("Control Union", "Estados Unidos", None,
          [(ars(suma_dia("CU United States")), "gasto por día"), (n(conv("CU United States")), "conv. 13 d"), ("2", "campañas")],
          f"USDA NOP pasó de {ars(nop['coste_dia_aud'])} a {ars(nop['coste_dia_post'])} por día y compra definiciones. PrimusGFS dejó de gastar.", [
    row("USDA NOP: el triple, en búsquedas de definición", "«what does certified organic mean» ARS 18.726 por 2 clics; «what is certified organic», «how to get certified as organic». Ninguno de los tres negativos propuestos aplicado. Cero conversiones.",
        "Negativos de definición y tope", "what is, what does, mean, meaning, how to become a negativo. omri, organic chicken, organic land también. CPC máximo. Exactas [certified organic], [national organic program].", "Nuevo"),
    row("PrimusGFS: sin gasto, con la exacta puesta", "Se sumó [primusgfs]. El presupuesto de ARS 8.000 por día no se está usando: 28 keywords activas, cero impresiones con gasto.",
        "Verificar por qué no publica", "Revisar estado de las keywords y del anuncio. Negativo consultant, consultoría, advisor a nivel cuenta: sigue sin estar.", "Pendiente"),
])

ar_cu = unit("Control Union", "Argentina", "Seis campañas nuevas desde la auditoría · ISO 27001 pasó al bloque siguiente",
          [(ars(suma_dia("CU Argentina")), "gasto por día"), (n(conv("CU Argentina")), "conv. 13 d"), ("6", "campañas nuevas")],
          f"Bien orientadas: EUDR, SMETA y FSSC con anuncio fuerte y páginas propias. Tres detalles a corregir antes de que escalen, y dos campañas que todavía no publican.", [
    row("EUDR: funciona, con dos términos que no son cliente", f"{ars(ar_eudr['coste_dia_post'])} por día, 27 clics. «eudr que significa» ARS 5.493 por un clic; Google marca una keyword «por debajo» en relevancia.",
        "Negativos de definición", "que significa, que es, resumen, pdf a negativo. Mantener las exactas de soja, cacao, madera. Sumar [certificacion eudr argentina].", "Nuevo"),
    row("GHG compra «creditos de carbono»", "Misma keyword que lleva a Peterson a comprar el mercado de bonos. Ya trajo «valor de bonos de carbono». Control Union verifica, no vende créditos.",
        "Sacar la keyword", "Eliminar [creditos de carbono]. Negativos bonos, mercado, precio, valor. Mantener verificación ISO 14064 e inventario GEI.", "Nuevo"),
    row("Biocombustible: keywords ISCC, anuncio 2BSvs", "Las 26 keywords dicen ISCC; los anuncios dicen «2BSvs, alternativa a ISCC EU». Todavía sin gasto. Cuando publique, va a cobrar clics de gente que busca ISCC y ve otro esquema.",
        "Un grupo por esquema", "Grupo ISCC con anuncio y landing ISCC; grupo 2BSvs con los suyos. Definir antes el corte con Peterson, que compra Bioenergía.", "Decisión"),
    row("Cadena de custodia y Agro sostenible no publican", "Una keyword activa cada una (FSC, RTRS) y cero gasto en 13 días. Agro sostenible anuncia FSA con keyword RTRS.",
        "Ampliar y alinear", "FSC: [certificacion fsc], [fsc argentina], [cadena de custodia fsc]. Agro: keywords FSA o anuncio RTRS, no uno de cada.", "Nuevo"),
    row("SMETA Argentina ya existe: era la mejora nº5", f"Grupos SMETA compra y proceso dentro de Industria, {ars(ar_ind['coste_dia_post'])} por día, anuncio fuerte. Orgánico: {n(next(t['impressions'] for t in U[('Argentina','arg')]['gsc']['no_comprada'] if t['query']=='smeta'))} búsquedas, ×19 interanual.",
        "Mantener y separar", "Campaña propia SMETA con presupuesto propio; hoy comparte ARS 2.000 por día con FSSC.", "Hecho"),
])

# ================================================================== PCU
pcu = unit("ISO 27001 · campañas «PCU»", "España y Argentina", "Antes «CU España / CU Argentina - ISO 27001» · renombradas y con 6 veces más presupuesto",
           [(ars(iso_dia), "gasto por día"), (n(iso_es["conv_post"] + iso_ar["conv_post"]), "conv. 13 d"), (pct(relm("pcu", "fuerte")), "anuncio fuerte")],
           f"Es la campaña que mejor funciona de la cuenta y la más cara: {ars(iso_dia)} por día, el {pct(iso_dia / T['dia_post'] * 100)} del total, con dos conversiones en 13 días y Google calificando la relevancia del anuncio «por encima de la media». El problema no es de rendimiento.", [
    row("Se llama «PCU» y ninguna marca certifica así", "El manual no admite piezas ni campañas sin marca. ISO 27001 es certificación: la emite Control Union. Peterson no certifica. Un anuncio que dice «Peterson and Control Union» compite consigo mismo en la búsqueda.",
        "Definir la marca y renombrar", "Campañas y anuncios como Control Union, con landing en controlunion.com. Si se quiere que Peterson venda preparación para certificar, va en campaña de Peterson con vocabulario de preparación, no de certificación.", "Decisión"),
    row("La exacta [iso 27001] sigue sin existir", f"«iso 27001» a secas costó ARS 73.169 en España y ARS 56.643 en Argentina en 13 días, entrando por «certificacion iso 27001» en frase.",
        "Exactas y control de CPC", "[iso 27001], [iso27001], [norma iso 27001], [iso iec 27001] en exacta con CPC máximo. Baja el costo del término que ya se paga.", "Pendiente"),
    row("Búsquedas informativas a ARS 6.000 el clic", "«que dice la iso 27001» ARS 7.286, «dominios iso 27001 2022» ARS 6.021, «iso 27» ARS 5.895: un clic cada una.",
        "Negativos", "que dice, dominios, pdf, resumen, 2022 pdf, controles, «iso 27» a negativo.", "Nuevo"),
    row("Competidores España despertó con relevancia baja", f"{ars(comp_es['coste_dia_post'])} por día por «bureau veritas iso 27001» y «aenor iso 27001»; Google marca las dos keywords «por debajo de la media». En Argentina, {ars(comp_ar['coste_dia_post'])}.",
        "Anuncio de comparación real o pausar", "Si se mantiene, el anuncio tiene que responder a la comparación. Si no, pausar: ARS 2.180 por día en clics que Google considera poco relevantes.", "Nuevo"),
])

# ================================================================== PETERSON
ps = unit("Peterson Solutions", "Argentina", None,
          [(ars(suma_dia("PS Argentina")), "gasto por día"), (n(conv("PS Argentina")), "conv. 13 d"), (pct(relm("ps", "nula")), "anuncio nulo")],
          f"Ninguna de las mejoras se aplicó y el presupuesto se movió hacia las campañas que peor compran: Huella de agua ×3, Bioenergía ×2, CeSu empezó a gastar. Cero conversiones.", [
    row("Huella de agua: ×3 y 100% fuera de foco", f"De {ars(ps_ha['coste_dia_aud'])} a {ars(ps_ha['coste_dia_post'])} por día. Sigue «gestion del agua industrial» trayendo tratamiento de efluentes. Cero negativos en la campaña.",
        "Eliminar la keyword y negativos", "Eliminar «gestion del agua industrial». tratamiento, efluentes, calculadora, planta a negativo. Exactas [huella hidrica corporativa], [iso 14046].", "Pendiente"),
    row("Bioenergía: ×2 y sigue en biogás", f"{ars(ps_bio['coste_dia_post'])} por día; biogas, dosbio, bio gas: 47% del gasto con anuncio nulo. CeSu también empezó a gastar ({ars(ps_ce['coste_dia_post'])} por día) con 37 de 39 keywords que nadie busca.",
        "Pausar las dos", "Pausar Bioenergía y CeSu. Si se rehace Bioenergía sobre ISCC y 2BSvs, antes definir el corte con Control Union Argentina, que acaba de abrir Biocombustible con las mismas keywords.", "Decisión"),
    row("Agricultura regenerativa y Huella de carbono, sin cambios", f"Agricultura {ars(ps_ag['coste_dia_post'])} por día, Huella de carbono {ars(ps_hc['coste_dia_post'])}. La amplia sigue, «bonos de carbono» sigue, cero negativos en Huella de carbono.",
        "Aplicar el Anexo A", "Sacar la amplia «agricultura regenerativa en argentina». Negativos de marcas del agro, agtech, bonos, mercado, créditos, carbono neutral. Amplias a frase. Exactas [consultoria ambiental], [iso 14064].", "Pendiente"),
    row("ESG: la más sana, con los mismos huecos", f"{ars(ps_esg['coste_dia_post'])} por día. «que es» ya está en negativos; gri + número, no.",
        "Completar negativos y exactas", "gri 403, gri 401 y el patrón gri + número a negativo. [csrd], [estandar gri], [consultora esg].", "Pendiente"),
    row("El sitio sigue sin existir en Argentina", f"Argentina es el {SEO['Américas']['pct_pais']}% de las impresiones orgánicas de la propiedad; casi toda la visibilidad está en páginas en inglés.",
        "Páginas en español", "Una página en español por servicio pagado. Hasta entonces, cada campaña compite sola.", "Pendiente"),
])

ib = S["Iberia"]
iberia = f'''<div class="unit"><div class="unit-bar"><div><div class="brand">Peterson Solutions</div><h2>Iberia</h2></div>
 <div class="nums"><div><div class="v">{n(ib["clics"])}</div><div class="k">clics orgánicos sin invertir</div></div><div><div class="v">0</div><div class="k">campañas</div></div></div></div>
 <p class="lead">csrd (1.456 búsquedas, posición 21,5), cbam services (28,6) y finanzas sostenibles (25,4) tienen página y están en página dos y tres. Es territorio de Peterson, no de Control Union: primero contenido, después una campaña propia.</p></div>'''

# ================================================================== relación + mercados + orden
def tabla_rel(m, titulo):
    pc = sorted(R2["marcas"].get(m, {}).get("por_campana", []), key=lambda x: -x["coste"])[:6]
    filas = "".join(f'<tr><td>{e(x["campana"].replace(" - Search","").replace(" - SEARCH",""))}</td><td class="num">{ars(x["coste"])}</td><td class="num">{pct(x["pct_fuerte"])}</td><td class="num">{pct(x["pct_nula"])}</td><td class="num">{n(x["score_medio"],1)}</td></tr>' for x in pc)
    return f'<h4 style="margin:4mm 0 1.5mm">{e(titulo)}</h4><table class="tbl mini"><thead><tr><th>Campaña</th><th class="num">Gasto 13 d</th><th class="num">Fuerte</th><th class="num">Nulo</th><th class="num">Score 0–3</th></tr></thead><tbody>{filas}</tbody></table>'


cierre = f'''<div class="page">
 <h2 class="sec-title">Qué tan relacionado está el anuncio con lo que la gente buscó</h2>
 <p class="sec-sub">Medido por API sobre el 12–24 de septiembre: para cada término con gasto, si sus palabras aparecen en los títulos del anuncio que se mostró (fuerte, parcial, nulo), si la URL final habla del tema, y la «relevancia del anuncio» que Google asigna a la keyword. El score suma las tres. Un nulo alto con anuncio bien escrito (SMETA España, Bioenergía) no es un problema de redacción sino de la keyword que trae búsquedas que ningún título puede responder: se arregla con negativos y concordancia. Detalle por término en <code>datos/ads/api/&lt;marca&gt;/analisis/</code>.</p>
 <div class="g2">
  <div>{tabla_rel("cu", "Control Union")}{tabla_rel("pcu", "ISO 27001 (PCU)")}</div>
  <div>{tabla_rel("ps", "Peterson Solutions")}
</div>
  </div>
 </div>
 <h2 class="sec-title" style="margin-top:4mm">Orden de ejecución</h2>
 <div class="steps">
  <div><div class="w">Esta semana · sin riesgo</div><h4>Cerrar lo que sobra</h4><ul>
   <li>Negativos de competidores en SMETA España; de definición en USDA NOP, EUDR e ISO 27001; el Anexo A completo en las {prop_a - aplicadas_a} campañas donde falta.</li>
   <li>consultant, consultoría, advisor a nivel cuenta en Control Union.</li>
   <li>Pausar Forestry y Aqua (Canadá), Huella de agua, Bioenergía y CeSu (Peterson). Eliminar [creditos de carbono] en GHG.</li></ul></div>
  <div><div class="w">Próximas dos semanas</div><h4>Comprar lo que se busca</h4><ul>
   <li>Exactas en ISO 27001 (ES y AR), IFS, Textile, CanadaGAP, NOP, PrimusGFS, CAEs.</li>
   <li>Grupos FSC en España y Portugal. Campaña ISO 45001 en España. TEMO y cumcs en Canadá.</li>
   <li>GMP+ rehecha en España y Portugal. recyclass Portugal a exacta con tope.</li></ul></div>
  <div><div class="w">Requiere decisión</div><h4>Lo que no se resuelve con datos</h4><ul>
   <li>Marca de las campañas «PCU» de ISO 27001: certifica Control Union.</li>
   <li>Corte ISCC/2BSvs entre Control Union Argentina (Biocombustible) y Peterson (Bioenergía): hoy las dos tienen las mismas keywords.</li>
   <li>Presupuesto: el gasto diario se multiplicó por {n(T["dia_post"]/T["dia_aud"],1)} y las conversiones siguen en una cifra; conviene fijar un techo por unidad hasta aplicar los negativos.</li></ul></div>
 </div>

</div>'''

CSS_EXTRA = '''
.tag.ok{ background:var(--navy); color:#fff; border-color:var(--navy); }
.tag.new{ background:var(--tint2); border-color:var(--tint2); color:var(--navy); }
.tbl{ width:100%; border-collapse:collapse; font-size:8.2pt; margin:2mm 0 2mm; }
.tbl th{ background:var(--navy); color:#fff; text-align:left; font-weight:700; padding:2mm 2.5mm; font-size:6.8pt; letter-spacing:.09em; text-transform:uppercase; }
.tbl td{ padding:1.6mm 2.5mm; border-bottom:.5pt solid var(--hair); vertical-align:top; line-height:1.35; }
.tbl tbody tr:nth-child(even) td{ background:var(--tint); }
.tbl .num, .tbl th.num{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }
.tbl.mini{ font-size:7.8pt; } .tbl.mini td{ padding:1.3mm 2mm; }
.g3{ display:grid; grid-template-columns:repeat(3,1fr); gap:5mm; margin-top:4mm; }
.g3 h4, .g2 h4{ font-size:10pt; color:var(--navy); margin:0 0 1.5mm; }
.g3 p{ font-size:8.4pt; line-height:1.45; }
.g2{ display:grid; grid-template-columns:1fr 1fr; gap:6mm; }
.box{ background:var(--tint); padding:3mm 3.5mm; margin-top:3mm; } .box p{ font-size:8pt; line-height:1.4; }
.small{ font-size:7.4pt; color:var(--grey); line-height:1.4; }
.unit-bar .sub{ font-size:7.8pt; color:var(--grey); margin-top:1mm; }
'''

doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan de mejoras unificado · campañas de búsqueda</title>
<link rel="stylesheet" href="estilo-mejoras.css"><style>{CSS_EXTRA}</style></head><body>
{cover}
{cambios}
<div class="page">{es}</div>
<div class="page">{pt}{ca}</div>
<div class="page">{us}{ar_cu}</div>
<div class="page">{pcu}</div>
<div class="page">{ps}{iberia}</div>
{cierre}
</body></html>'''
open(os.path.join(INF, "plan-unificado.html"), "w", encoding="utf-8").write(doc)
print("-> informe/plan-unificado.html")
