# -*- coding: utf-8 -*-
"""
generar_clientes.py — informe corto por unidad: pain points actuales y solución actual de cada uno.
Fuente: informe/datos_clientes.json + informe/datos_informe.json. Sale a informe/clientes.html
"""
import json, os
from informe_util import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
C = json.load(open(os.path.join(INF, "datos_clientes.json"), encoding="utf-8"))
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))
SEO = json.load(open(os.path.join(INF, "datos_seo.json"), encoding="utf-8"))
PCT_ARG = SEO["Américas"]["pct_pais"]
U = {(c["propiedad"], c["pais"]): c for c in C["clientes"]}
S = {s["propiedad"]: s for s in C["sin_campana"]}
s7 = D["s7"]
FECHA = hoy()


def camp(u, nombre):
    return next((x for x in u["campanas"] if x["camp_corta"] == nombre), None)


def fila(titulo, sub, evidencia, solucion, estado):
    return (f'<div class="pain"><div class="h">{titulo}<span>{e(sub)}</span></div>'
            f'<div><span class="lab">Evidencia</span><p>{evidencia}</p></div>'
            f'<div><span class="lab">Solución actual</span><p>{solucion}</p></div>'
            f'<div>{chip(estado)}</div></div>')


def demanda(u, k=5, titulo="Demanda orgánica sin comprar · las mayores"):
    top = u["gsc"]["no_comprada"][:k]
    if not top:
        return ""
    mx = max(t["impressions"] for t in top)
    rows = "".join(f'<div class="r"><div><b>{e(t["query"])}</b>{(" · " + e(t["norma"])) if t.get("norma") and str(t["norma"]) not in ("nan", "None") else ""}</div>'
                   f'<div>{barra(t["impressions"], mx)}</div><div class="num">{n(t["impressions"])}</div><div class="num">{n(t["position"],1)}</div></div>' for t in top)
    return (f'<div class="dem" style="margin-top:3mm"><div class="r head"><div>{e(titulo)}</div><div></div><div class="num">Impr.</div><div class="num">Pos.</div></div>{rows}</div>'
            f'<p class="small" style="margin-top:1.5mm">{n(u["gsc"]["no_comprada_n"])} queries con 40+ impresiones en el histórico sin keyword ni término por tema · {n(u["gsc"]["no_comprada_impr"])} impresiones.</p>')


def unidad(u, filas_html, intro, extra=""):
    a, g = u["ads"], u["gsc"]
    desp_pct = round(a["desperdicio"] / a["visible"] * 100) if a["visible"] else 0
    return f'''
<section class="unit">
 <div class="unit-head">
  <div><p class="brand">{e(u["marca"] == "CU" and "Control Union · organismo certificador" or "Peterson Solutions · consultora")}</p>
   <h2>{e(u["nombre"])}</h2><p class="sub">{n(a["campanas"])} campañas de Search · 1 ago – 11 sep 2026 · {n(a["keywords"])} keywords, {n(a["sin_impr"])} sin una impresión</p></div>
  <div class="kpis">{kpi(ars(a["gasto"]), "gasto")}{kpi(n(a["clics"]), "clics pagos")}{kpi(n(a["conv"]), "conv.")}{kpi(ars(a["cpc"]), "cpc")}</div>
 </div>
 <div class="g" style="margin-bottom:3.5mm">
  <div class="c3">{stat(pct(desp_pct), "fuera de foco", f"{ars(a['desperdicio'])} del gasto visible en términos que no corresponden al servicio")}</div>
  <div class="c3">{stat(ars(a["huecos"]), "sin contenido", f"gasto con clic en temas donde el sitio no tiene nada, en el país que compra")}</div>
  <div class="c3">{stat(n(g["clics_ads"]), "clics orgánicos", f"contra {n(a['clics'])} pagos, mismas seis semanas · {n(g['impr_ads'])} impresiones desde {e(u['pais'].upper())}")}</div>
  <div class="c3">{stat(pct(g["movil_pct"], 0), "móvil", f"de las impresiones orgánicas · CTR móvil {pct(g['ctr_movil'],2)} vs {pct(g['ctr_desk'],2)} escritorio")}</div>
 </div>
 <p>{intro}</p>
 <div class="pain-head"><div>Pain point</div><div>Evidencia</div><div>Solución actual</div><div>Estado</div></div>
 {filas_html}
 {extra}
</section>'''


# ================================================================== unidades
out = []

# ---------- CU España
u = U[("España", "esp")]; c_cae = camp(u, "CAEs"); c_ifs = camp(u, "IFS"); c_tex = camp(u, "Textile"); c_iso = camp(u, "ISO 27001"); c_for = camp(u, "Forestal")
zona = {z["termino"]: z for z in u["ads"]["zona"]}
filas = [
    fila("CAEs mezcla dos mercados", "Campaña más cara de la unidad",
         f"{ars(c_cae['coste'])} · {pct(c_cae['pct_fuera'])} del gasto visible fuera de foco ({ars(c_cae['desperdicio'])}). La amplia «certificado de eficiencia energetica» trae el certificado de vivienda, un particular, no un sujeto obligado CAE. Convirtió una vez, no se sabe con qué búsqueda.",
         "Negativizar el vocabulario de vivienda (Anexo A), pasar la amplia a frase, agregar exactas B2B: sistema CAE, verificación de actuaciones, sujeto delegado. Revisar en 30 días.", "Propuesto"),
    fila("IFS compra genéricos", "Y la demanda IFS queda sin keyword",
         f"{ars(c_ifs['coste'])} en 9 keywords de seguridad alimentaria; ninguna nombra IFS. Orgánico: {n(s7['ifs_es']['impresiones'])} impresiones en queries IFS, cero clics, posición {n(s7['ifs_es']['pos'],1)}. ISO 22000 ({n(s7['iso22000_es']['impresiones'])} impr.) y FSSC ({n(s7['fssc_es']['impresiones'])}) tienen página y demanda; BRCGS {n(s7['brcgs_es']['impresiones'])}.",
         "Exactas [ifs food], [certificado ifs], [norma ifs]. Grupos propios para ISO 22000 y FSSC 22000. BRCGS y formación de manipuladores a negativos.", "Resuelto"),
    fila("Textile paga OEKO-TEX", "Un esquema que Control Union no certifica",
         f"ARS 15.362 en oeko tex standard 100 y organic cotton standard. Cero apariciones de OEKO-TEX en {n(s7['queries_cu_total'])} queries orgánicas de las ocho propiedades. GOTS y GRS sí traen intención.",
         "Negativo confirmado con evidencia propia. Sumar exactas [certificado gots], [grs global recycled standard]. Marca propia fuera de Textile (ARS 1.848).", "Resuelto"),
    fila("FSC entra por PEFC", "La auditoría proponía negativizarlo",
         f"La filial certifica FSC: página propia, {n(s7['fsc_espana']['impresiones'])} impresiones en {n(s7['fsc_espana']['queries'])} queries, posición {n(s7['fsc_espana']['pos'],1)}. Los clics FSC llegaban a una landing de PEFC.",
         "Sacar FSC del Anexo A. Abrir grupo FSC con landing a la página que existe. Negativizar solo «consultor fsc» por regla de marca.", "Corregido"),
    fila("ISO 27001 caro y vacío", "CPC ARS 6.019, 27 de 31 keywords mudas",
         f"{ars(c_iso['coste'])} y {n(c_iso['clics'])} clics. La página orgánica de ISO 27001 rankea en posición {n(D['landing']['pos_es'],1)} para sus propias queries: no hay respaldo orgánico ({ars(c_iso['hueco'])} en hueco).",
         "Exactas [iso 27001] y [certificarse en iso 27001] con tope de puja. Eliminar renovación y trámites. La página necesita trabajo SEO (informe aparte).", "Propuesto"),
    fila("ISO 45001, la demanda más grande, sin campaña", "Sin keyword ni término en la cuenta",
         f"{n(s7['iso45001_es']['impresiones'])} impresiones orgánicas en {n(s7['iso45001_es']['queries'])} queries, posición {n(s7['iso45001_es']['pos'],1)}, {n(s7['iso45001_es']['clics'])} clics. Página propia. GMP+: {n(s7['gmp_es']['impresiones'])} impr. en posición {n(s7['gmp_es']['pos'],1)} con campaña de 31 keywords que no publica.",
         "Campaña ISO 45001 sobre la página existente. Reconstruir GMP+ con el vocabulario que la gente usa (gmp+, gmp plus, feed safety).", "Propuesto"),
    fila("ISCC dejó de aparecer", "Zona 8–20: donde el paid rinde",
         f"«iscc» pasó de posición 6,9 con 605 impresiones en abril a {n(zona['iscc']['pos_org'],1)} con 11 en agosto, desde España. La campaña de Bioenergía paga {ars(zona['iscc']['coste'])} por ese término y convirtió. smeta está en {n(zona['smeta']['pos_org'],1)} y ya no necesita paid.",
         "Revisar la página ISCC antes del próximo corte (dos URL compiten: iscc-plus e iscc_eu). Mantener [iscc] exacta mientras tanto.", "Nuevo"),
]
intro = "La unidad con más campañas y más demanda orgánica desatendida. Tres decisiones se cerraron con Search Console (IFS, OEKO-TEX, FSC) y dos siguen pendientes de ejecución (CAEs, ISO 27001). Lo nuevo es ISCC. Además de ISO 45001, sin comprar: welfair (5.196 impresiones, posición 6,5), grasp (4.553, 8,3), sure y gmp+."
out.append(unidad(u, "".join(filas), intro))

# ---------- CU Portugal
u = U[("Portugal", "prt")]; c_for = camp(u, "Forestal"); c_tex = camp(u, "Textile"); c_pla = camp(u, "Plasticos")
zona = {z["termino"]: z for z in u["ads"]["zona"]}
can = D["canibalizacion"]["top"][0]
filas = [
    fila("recyclass se paga y ya rankea 3º", "Canibalización real, la única de la cuenta",
         f"Plásticos paga {ars(can['coste'])} por «recyclass» con posición orgánica {n(can['pos_org'],1)} para búsquedas desde Portugal. Es la mitad del gasto visible de la campaña.",
         "Bajar la puja o pasar a exacta con tope y medir 30 días si el clic orgánico compensa. Mantener UNE-EN 15343, que no rankea.", "Nuevo"),
    fila("FSC entra por PEFC", "Misma corrección que España",
         f"Página propia, {n(s7['fsc_portugal']['impresiones'])} impresiones en {n(s7['fsc_portugal']['queries'])} queries, posición {n(s7['fsc_portugal']['pos'],1)}; «madeira certificada fsc» con demanda local. ARS 3.069 de clics FSC llegaban a PEFC.",
         f"Sacar FSC del Anexo A y abrir grupo FSC con landing propia. PEFC ({n(zona['pefc']['pos_org'],1)}) e ISCC ({n(zona['iscc']['pos_org'],1)}) están en la zona donde el paid rinde: se mantienen.", "Corregido"),
    fila("GMP+ y Biomasa no publican", "36 keywords, una impresión",
         f"GMP+: 24 keywords, ninguna publicó; orgánico {n(s7['gmp_pt']['impresiones'])} impresiones en posición {n(s7['gmp_pt']['pos'],1)}. Biomasa SURE: 10 de 12 mudas, {ars(camp(u, 'Biomasa')['coste'])}.",
         "Reconstruir GMP+ sobre demanda real o pausar la estructura vacía. SURE: mantener y revisar en el próximo corte.", "Propuesto"),
    fila("Lo más buscado no tiene campaña", "Siete campañas, ninguna sobre esto",
         f"aquacultura {n(u['gsc']['no_comprada'][0]['impressions'])} impresiones en posición {n(u['gsc']['no_comprada'][0]['position'],1)}; rainforest alliance en 3,6; iso 9001 {n(next(t['impressions'] for t in u['gsc']['no_comprada'] if t['query']=='iso 9001'))} impresiones en posición 12,9 y cayendo (1.174 → 85 entre tramos).",
         "Evaluar campaña de defensa en aquacultura y Rainforest Alliance (posición ganada, demanda probada). ISO 9001 es un caso SEO antes que paid.", "Propuesto"),
    fila("Textile con ruido chico", "La mejor relación clic/gasto de la unidad",
         f"{ars(c_tex['coste'])}, {n(c_tex['clics'])} clics, {pct(c_tex['pct_fuera'])} fuera de foco (wordly, database). GOTS fuerte: 5 clics sobre 112 impresiones pagas.",
         "Exactas [gots], [gots 8.0], [certificado gots], [grs]. Negativos wordly y database. Sin más cambios.", "Propuesto"),
]
intro = "Portugal gasta un tercio de España con mejor foco: casi nada fuera de servicio. Sus dos problemas son de arquitectura, no de desperdicio: paga un término que ya rankea tercero y no compra lo que más se busca."
out.append(unidad(u, "".join(filas), intro, demanda(u)))

# ---------- CU Canadá
u = U[("Norteamérica", "can")]; c_f = camp(u, "Forestry"); c_g = camp(u, "Canada Gap"); c_a = camp(u, "Aqua / Fisheries")
temo = s7["temo_na"]
filas = [
    fila("Forestry: la campaña más cara, sin sitio que la sostenga", "ARS 4.545 por clic",
         f"{ars(c_f['coste'])} y {n(c_f['clics'])} clics. {ars(c_f['hueco'])} en temas sin contenido. Orgánico de FSC y bosques en toda la propiedad: {n(s7['fsc_na']['impresiones'])} impresiones, {n(s7['fsc_na_por_pais'].get('can',0))} desde Canadá. Bloque de credencial personal (rpf, forester license) en negativos.",
         "Pausar Forestry hasta que exista contenido forestal en el sitio. Si se mantiene, exactas [fsc], [fsc canada], [fsc chain of custody] y negativos de credencial personal.", "Resuelto"),
    fila("Aqua / Fisheries compra lo que el sitio no tiene", "Los 8 clics son MSC, ASC, BAP: buena intención, mala landing",
         f"{ars(c_a['coste'])}, {n(c_a['clics'])} clics, {ars(c_a['hueco'])} sin contenido en Canadá. No hay página que responda MSC o ASC para ese mercado.",
         "Pausar junto con Forestry. Reasignar a TEMO, collateral management y PrimusGFS, que sí tienen página y demanda.", "Resuelto"),
    fila("CanadaGAP construida por hipótesis", "38 de 45 keywords nunca se activaron",
         f"{ars(c_g['coste'])}, {pct(c_g['pct_fuera'])} fuera de foco (supply chain management, indocert, consultant). Hueco: {ars(c_g['hueco'])}.",
         "Eliminar el bloque produce broker / packing house / repacking. Exactas [canada gap], [canadagap]. Negativos de la auditoría más «consultant» a nivel cuenta.", "Propuesto"),
    fila("El sitio no existe para Canadá", "Estructural: geografía y contenido",
         f"Desde Canadá llegaron {n(u['gsc']['impr_ads'])} impresiones y {n(u['gsc']['clics_ads'])} clics orgánicos en seis semanas; India trae más que Canadá en el histórico (7.599 vs 2.251). Todo lo que la unidad recibe de Canadá es pagado.",
         "Contenido por mercado antes que más pauta. Revisar el filtro geográfico de la propiedad y de las campañas. Es la causa de fondo de los tres puntos anteriores.", "Nuevo"),
    fila("TEMO, la mayor demanda de la propiedad, se está apagando", "Sin campaña, sin SEO, y cayendo",
         f"{n(temo['impresiones'])} impresiones en el histórico, posición {n(temo['pos'],1)}, {n(temo['clics'])} clics: CTR 0,06% en la página. Pasó de 3.165 impresiones en el primer tramo a 249 en el último.",
         "Campaña TEMO con la página que ya rankea, y revisar por qué la página perdió visibilidad (informe SEO). Es donde debería ir el presupuesto de Forestry.", "Alerta"),
]
intro = "La unidad con peor respaldo de toda la cuenta: segundo gasto del grupo sobre una propiedad que casi no recibe búsquedas desde Canadá. Las decisiones de pausa están tomadas; lo nuevo es que la demanda que sí existe, TEMO, se está perdiendo."
out.append(unidad(u, "".join(filas), intro, demanda(u, 5, "Demanda orgánica de la propiedad sin comprar (Canadá y EE.UU.)")))

# ---------- CU Estados Unidos
u = U[("Norteamérica", "usa")]; c_n = camp(u, "USDA NOP")
filas = [
    fila("USDA NOP: el CPC más alto de la cuenta", "ARS 6.326 por clic, 43 de 51 keywords mudas",
         f"{ars(c_n['coste'])}, {n(c_n['clics'])} clics, cero conversiones. {pct(c_n['pct_fuera'])} fuera de foco: organic chicken certification (ARS 11.056 un clic), omri, organic land. La keyword que más gastó figura en pausa.",
         "Negativos de producto animal y OMRI. Exactas [national organic program], [certified organic]. Eliminar multi-site, switch certifier, importer. Confirmar el estado real de «Usda nop» en la interfaz.", "Propuesto"),
    fila("PrimusGFS pagó consultoría", "Regla de marca: Control Union no asesora",
         "ARS 25.941 fuera del export (keywords retiradas después de gastar): gfsi consultant ARS 20.951 y gfsi certification. GFSI no es un esquema certificable. 25 de 28 keywords no publican.",
         "Negativizar consultant, consultoría y advisor a nivel cuenta. Reconstruir con exactas [primusgfs], [primusgfs certification], [primus gfs]. Orgánico: 772 impresiones con dos páginas compitiendo (informe SEO).", "Propuesto"),
    fila("Marca propia desde campaña de producto", "Ya rankea primero",
         f"«certified organic by control union» costó ARS 3.586 con posición orgánica 1,0. Es la canibalización más clara de la cuenta.",
         "Cortar de USDA NOP. Si se quiere proteger la marca, campaña de marca a CPC bajo.", "Propuesto"),
    fila("Demanda real, presupuesto en otro lado", "EE.UU. trae el 32% de las impresiones de la propiedad",
         f"cumcs en posición 1,9 (1.107 impr.), collateral management (1.266, posición 49), fslm (1.225, posición 8,7). Ninguna con campaña.",
         "Mover parte del presupuesto de Forestry a estos temas, con página existente. cumcs ya está arriba: campaña de defensa, no de conquista.", "Propuesto"),
]
intro = "Dos campañas, ambas con estructura larga y muda. El problema de EE.UU. no es desperdicio masivo sino precio: paga el clic más caro del grupo por términos genéricos mientras lo que sí rankea no tiene pauta."
out.append(unidad(u, "".join(filas), intro))

# ---------- CU Argentina
u = U[("Argentina", "arg")]; c_i = camp(u, "ISO 27001")
nc_ar = {t["query"]: t for t in u["gsc"]["no_comprada"]}
ya = D["interanual"]["Argentina"]["total"]
filas = [
    fila("ISO 27001: una keyword hace todo", "24 de 31 sin impresión; «iso 27001» no es keyword",
         f"{ars(c_i['coste'])}, {n(c_i['clics'])} clics; «certificacion iso 27001» concentra 20. La página orgánica rankea en {n(D['landing']['pos_ar'],1)} para sus propias queries. Competidores captura genéricos que deberían ir a la campaña principal.",
         "Exactas [iso 27001], [iso27001], [norma iso 27001]. Negativizar nist. Competidores a exacta con nombre de competidor, e «iso 27001» genérico como negativo ahí.", "Propuesto"),
    fila("El orgánico trae 20 veces más que el paid", "Y crece: +45% impresiones interanual",
         f"En seis semanas: {n(u['gsc']['clics_ads'])} clics orgánicos desde Argentina contra {n(u['ads']['clics'])} pagos. Junio–agosto: {n(ya['impr_2025'])} → {n(ya['impr_2026'])} impresiones y {n(ya['clics_2025'])} → {n(ya['clics_2026'])} clics de un año al otro.",
         "La inversión en Argentina es chica frente al mercado. Priorizar SEO sobre las páginas que ya rankean y campañas de defensa donde la posición está ganada.", "Nuevo"),
    fila("SMETA y VISEC: la asimetría más fácil de corregir", "SMETA tiene campaña en España, Portugal y Canadá, no acá",
         f"smeta {n(nc_ar['smeta']['impressions'])} impresiones, posición {n(nc_ar['smeta']['position'],1)}, multiplicó por 19 sus impresiones interanuales. visec {n(nc_ar['visec']['impressions'])} en posición {n(nc_ar['visec']['position'],1)} (×39), visec carne {n(nc_ar['visec carne']['impressions'])}. fsa {n(nc_ar['fsa']['impressions'])} en posición {n(nc_ar['fsa']['position'],1)}.",
         "Campaña SMETA Argentina sobre la página existente. VISEC y FSA: campaña de defensa, ya están en primera página.", "Propuesto"),
    fila("Depósito fiscal desapareció", "De 801 impresiones a 1 entre tramos",
         f"«deposito fiscal» acumula {n(nc_ar['deposito fiscal']['impressions'])} impresiones en el histórico y cayó a 1 en junio–agosto de 2026. La página /service/deposito-fiscal/ dejó de aparecer.",
         "Verificar si la página existe, está indexada y no fue reemplazada. Es pérdida de servicio, no de ranking.", "Alerta"),
]
intro = "La unidad con menos gasto y mejor orgánico del grupo: el sitio argentino rinde solo. El pain point no es lo que se paga sino todo lo que no se compra ni se cuida."
out.append(unidad(u, "".join(filas), intro, demanda(u)))

# ---------- PS Argentina
u = U[("Américas", "arg")]; c_ag = camp(u, "Agricultura regenerativa"); c_hc = camp(u, "Huella de carbono / GEI"); c_esg = camp(u, "ESG / Reportes")
c_bio = camp(u, "Bioenergia / Biocombustibles"); c_ha = camp(u, "Huella de agua"); c_ce = camp(u, "CeSu - Preparacion para certificaciones")
filas = [
    fila("Agricultura regenerativa: más clics, peor usados", "La campaña con más clics de toda la cuenta",
         f"{ars(c_ag['coste'])}, {n(c_ag['clics'])} clics, {pct(c_ag['pct_fuera'])} fuera de foco más {ars(c_ag['hueco'])} en temas sin contenido. La amplia «agricultura regenerativa en argentina» (219 clics) abre a marcas del agro, tecnología agrícola y agronomía de nicho.",
         "Eliminar la amplia. Exactas [agricultura regenerativa], [ganadería regenerativa argentina]. Negativizar marcas y agtech (Anexo A).", "Propuesto"),
    fila("Huella de carbono compra bonos de carbono", "Otro negocio, y Peterson no emite créditos",
         f"{ars(c_hc['coste'])}, {n(c_hc['clics'])} clics. Tres amplias abrieron el mercado de bonos, verra, carbono neutral: {pct(c_hc['pct_fuera'])} fuera de foco, {ars(c_hc['hueco'])} sin contenido.",
         "Negativizar bonos, mercado, créditos, carbono neutral, iso 14001, plataformas. Amplias a frase. Agregar lo que Peterson sí vende: [consultoria ambiental], [iso 14064], [inventario gei argentina].", "Propuesto"),
    fila("ESG / Reportes: sana, pero sin respaldo en el sitio", "«reporte GRI» trae 31 clics con intención",
         f"{ars(c_esg['coste'])}, {n(c_esg['clics'])} clics, solo {pct(c_esg['pct_fuera'])} fuera de foco. Pero {ars(c_esg['hueco'])} de clics van a temas donde el sitio no tiene página en español.",
         "Negativizar gri + número y «qué es». Agregar [csrd], [estandar gri], [consultora esg]. Y crear contenido GRI/ESG en español: hoy la landing no responde.", "Propuesto"),
    fila("Bioenergía y Huella de agua: sin mercado de servicio", "65% y 100% fuera de foco",
         f"Bioenergía {ars(c_bio['coste'])}: biogás, plantas, «qué es». Huella de agua {ars(c_ha['coste'])}: tratamiento de efluentes y calculadoras gratis. Ninguno busca un servicio de sostenibilidad.",
         "Huella de agua: eliminar «gestion del agua industrial», negativos, vocabulario corporativo. Bioenergía: pausar; si se rehace sobre ISCC/2BSvs hay que definir antes el corte con Control Union, que ya compra ISCC.", "Decisión abierta"),
    fila("CeSu no tiene demanda con ese vocabulario", "37 de 39 keywords marcadas «no suele publicarse»",
         f"{n(c_ce['keywords'])} keywords, cero clics, {ars(c_ce['coste'])}: frases construidas por hipótesis (preparacion auditoria ISCC, consultoria 2BSvs).",
         "Pausar y atender el servicio desde las campañas donde el tráfico ya existe, con un grupo de preparación. Sigue abierto.", "Decisión abierta"),
    fila("El sitio no existe orgánicamente en Argentina", "Todo el tráfico argentino es pagado",
         f"Desde Argentina, la propiedad recibió {n(u['gsc']['impr_ads'])} impresiones y {n(u['gsc']['clics_ads'])} clics orgánicos en las seis semanas; Argentina es el {PCT_ARG}% de sus impresiones en todo el histórico. El 80% de la visibilidad está en páginas /en/ y la demanda que rankea es RED III desde EE.UU.",
         "Contenido en español, con URL propias, para los cinco servicios que se pagan. Mientras no exista, cada campaña compite sola. Es el pain point de fondo de la unidad (informe SEO).", "Nuevo"),
]
intro = "La unidad con más clics y sin una sola conversión. Cuatro de sus ocho campañas gastan sobre búsquedas informativas o de otro negocio, y el sitio no acompaña: en Argentina, Peterson no aparece en orgánico."
out.append(unidad(u, "".join(filas), intro))

# ---------- mercados sin inversión
def bloque_sin(p, texto):
    s = S[p]
    top = s["top"][:4]
    lst = " · ".join(f"<b>{e(t['query'])}</b> {n(t['impressions'])} en pos. {n(t['position'],1)}" for t in top)
    return (f'<div class="c6 card key"><h4>{"PS " if s["marca"]=="PS" else ""}{e(p)}</h4>'
            f'<p class="met">{n(s["impr"])} impresiones · {n(s["clics"])} clics en el histórico · posición media {n(s["pos"],1)} · móvil {pct(s["movil_pct"],0)} · {n(s["no_comprada_n"])} queries sin comprar</p>'
            f'<p class="dem">{lst}</p><p>{texto}</p></div>')

sin_html = f'''
<section class="unit">
 <div class="unit-head"><div><p class="brand">Ambas marcas · sin campaña</p><h2>Mercados donde no se invierte</h2>
  <p class="sub">Cuatro propiedades de Control Union y una de Peterson Solutions sin ninguna campaña en la cuenta</p></div>
  <div class="kpis">{kpi(n(sum(S[p]["clics_ads"] for p in S)), "clics org. 6 sem.")}{kpi(n(sum(S[p]["clics"] for p in S)), "clics org. hist.")}{kpi(n(sum(S[p]["no_comprada_n"] for p in S)), "queries sin comprar")}</div>
 </div>
 <p>El pain point es el mismo en los cinco: demanda probada y posición ganada sin nadie detrás. En las seis semanas del informe de Ads, Perú, Brasil, México y Chile trajeron
 {n(sum(S[p]["clics_ads"] for p in ("Perú","Brasil","México","Chile")))} clics orgánicos; las cuatro unidades con campaña de Control Union, {n(sum(U[k]["gsc"]["clics_ads"] for k in U if k[0] != "Américas"))}.
 La solución actual es una sola: no hay ninguna. Lo que sigue son las tres puertas de entrada más baratas por mercado.</p>
 <div class="g">
  {bloque_sin("Perú", "La propiedad más grande del grupo. koa certification y haccp están en primera página sin campaña; rainforest alliance en 3,4. Solución propuesta: campaña de defensa en tres temas y arreglar el CTR de HACCP (informe SEO).")}
  {bloque_sin("México", "La más móvil del grupo (41%). grs es la mayor demanda de GRS de toda la red, en posición 7,5 y con CTR 0,27%. Solución propuesta: título y snippet de la página GRS antes que pauta.")}
  {bloque_sin("Brasil", "obp, grs y gmp en primera página; gmp+ es el mismo caso que España y Portugal. Solución propuesta: extender la campaña GMP+ reconstruida a Brasil cuando exista.")}
  {bloque_sin("Chile", "Demanda de acuicultura (bap, asc) y GRS con posición ganada. La página de login rankea para la marca. Solución propuesta: ninguna pauta todavía; ordenar la SERP de marca.")}
  {bloque_sin("Iberia", "Peterson en España y Portugal: csrd 1.456 impresiones en posición 21,5, cbam services en 28,6. Es territorio de Peterson, no se resuelve con las campañas de Control Union. Solución propuesta: contenido CSRD/CBAM y una campaña propia cuando la página esté en primera página.")}
 </div>
</section>'''
out.append(sin_html)

# ---------- transversal
trans = f'''
<section class="unit">
 <div class="unit-head"><div><p class="brand">Toda la cuenta</p><h2>Lo que atraviesa a todas las unidades</h2>
  <p class="sub">Cinco acciones que no dependen de ninguna decisión pendiente</p></div>
  <div class="kpis">{kpi(ars(C["ads_total"]), "gasto total")}{kpi(n(C["ads_clics"]), "clics")}{kpi(n(C["ads_conv"]), "conversiones")}</div>
 </div>
 <div class="pain-head"><div>Pain point</div><div>Evidencia</div><div>Solución actual</div><div>Estado</div></div>
 {fila("Consultoría pagada desde Control Union", "Conflicto de interés, regla de marca", "consultant, consultor, consultoría, advisor aparecen en campañas de Canadá, EE.UU. y España. Orgánicamente el sitio no rankea para eso (posición 45 en «consultor fsc»).", "Negativos a nivel cuenta en todas las campañas de Control Union. Un día de trabajo, cero riesgo.", "Propuesto")}
 {fila("681 keywords que nunca se activaron", "69% de la cuenta", "Listas largas de variantes hiperespecíficas mientras el tráfico entra por dos o tres amplias por campaña. 460 marcadas «no suele publicarse».", "Limpieza completa. No ahorra plata, pero deja la cuenta legible para el próximo corte.", "Propuesto")}
 {fila("Ninguna conversión atribuible", "4 en seis semanas, todas en el bloque oculto de Ads", "El 43% del tráfico pago está bajo «Otros términos». No hay base para optimizar por CPA.", "Decidir por relevancia de intención. Indicador: desperdicio visible por debajo del 10% en el próximo informe de términos.", "Resuelto")}
 {fila("Dispositivo sin ajustar", "Nunca se había medido", f"El {pct(D['dispositivos_total']['MOBILE']['pct_impr'],0)} de las impresiones orgánicas llega desde móvil y el CTR móvil es la mitad del de escritorio en España, Portugal y Norteamérica. La búsqueda de normas es de escritorio.", "Ajuste de puja por dispositivo en las campañas de norma de España y Portugal, después de mirar el reparto de conversiones en Ads.", "Nuevo")}
 {fila("ISCC: dos marcas en la misma subasta", "Decisión abierta desde la auditoría", "Control Union España y Portugal compran ISCC (ARS 76.384 combinados, con conversión). Bioenergía de Peterson Argentina apuntaría al mismo vocabulario.", "Definir el corte de marca antes de que Peterson compre ISCC, como se hizo con EUDR. No se contesta con datos.", "Decisión abierta")}
 <div class="hair"></div>
 <div class="g">
  <div class="c4 panel"><p class="kick kick-n">Cómo se armó</p><p class="small">Ads: informes de keywords y términos del 1 ago al 11 sep 2026. Search Console: histórico completo de las diez propiedades (marzo a septiembre 2026; Argentina y México desde mayo 2025), cruzado por tema y por país de compra. Detalle y método en el informe «Search Console: histórico y móvil».</p></div>
  <div class="c4 panel"><p class="kick kick-n">Estados</p><p class="small"><strong>Resuelto</strong> y <strong>Corregido</strong>: decidido con evidencia. <strong>Propuesto</strong>: en la auditoría de Ads, pendiente de ejecutar. <strong>Decisión abierta</strong>: requiere una definición comercial. <strong>Nuevo</strong> y <strong>Alerta</strong>: surge del histórico y no estaba en ningún informe anterior.</p></div>
  <div class="c4 panel"><p class="kick kick-n">Límites</p><p class="small">Search Console anonimiza queries chicas; Ads oculta el 43% del tráfico. Las dos fuentes sirven para decidir dirección, no para sumarse. La posición es una banda, no un número fino. Seis meses de histórico: sin estacionalidad.</p></div>
 </div>
 {nota_marca(FECHA)}
</section>'''
out.append(trans)

# ---------- portada
tot_huecos = sum(U[k]["ads"]["huecos"] for k in U)
tot_desp = sum(U[k]["ads"]["desperdicio"] for k in U)
n_pain = sum(h.count('<div class="pain">') for h in out)
cover = f'''
<section class="cover">
 <div class="cover-top">
  <p class="kick">Documento interno · Peterson Control Union World Group</p>
  <h1>Pain points y solución actual, unidad por unidad</h1>
  <div class="cover-meta">
   <div class="c3"><p class="lbl">Alcance</p><p class="val">6 unidades con campaña<br>5 mercados sin inversión</p></div>
   <div class="c3"><p class="lbl">Fuentes</p><p class="val">Google Ads, 1 ago – 11 sep 2026<br>Search Console, histórico completo</p></div>
   <div class="c3"><p class="lbl">Pain points</p><p class="val">{n_pain} identificados<br>cada uno con su solución y estado</p></div>
   <div class="c3"><p class="lbl">Complementa a</p><p class="val">Auditoría de Ads · Search Console × Ads<br>Histórico y móvil</p></div>
  </div>
 </div>
 <div class="cover-body">
  <div class="g">
   <div class="c3">{stat(ars(C["ads_total"]), "gasto en seis semanas", f"{n(C['ads_clics'])} clics y {n(C['ads_conv'])} conversiones en 35 campañas de Search.")}</div>
   <div class="c3">{stat(ars(tot_desp), "fuera de foco", "términos que no corresponden al servicio de la campaña, sobre el gasto visible.")}</div>
   <div class="c3">{stat(ars(tot_huecos), "sin contenido", "gasto con clic en temas donde el sitio no dice nada, medido en el país que compra.")}</div>
   <div class="c3">{stat(n(sum(U[k]["gsc"]["no_comprada_n"] for k in U) + sum(S[p]["no_comprada_n"] for p in S)), "queries sin comprar", "con 40+ impresiones orgánicas y sin keyword ni término en la cuenta.")}</div>
  </div>
  <div class="hair"></div>
  <div class="g">
   <div class="c7">
    <p class="kick kick-n">Cómo leer este documento</p>
    <p class="lede">Una página por unidad. Arriba, lo que gasta y lo que recibe. Abajo, cada pain point con su evidencia, la solución que hoy está sobre la mesa y en qué estado está: resuelto, propuesto, decisión abierta o nuevo.</p>
    <p>Las soluciones «propuestas» son las de la auditoría de Ads, confirmadas o corregidas con Search Console. Las «nuevas» surgen del histórico y no estaban en ningún informe anterior. Nada de lo que ya estaba resuelto se reabre.</p>
   </div>
   <div class="c5 panel">
    <p class="kick kick-n">Los cuatro que más pesan</p>
    <p class="small"><strong>Canadá</strong>: {ars(U[("Norteamérica","can")]["ads"]["gasto"])} sobre un sitio que no recibe búsquedas desde Canadá. Pausa decidida.<br>
    <strong>Peterson Argentina</strong>: {n(U[("Américas","arg")]["ads"]["clics"])} clics, cero conversiones, y el sitio no aparece en orgánico en Argentina.<br>
    <strong>España</strong>: la mayor demanda del grupo (ISO 45001, {n(s7["iso45001_es"]["impresiones"])} impresiones) sin campaña, e ISCC apagándose.<br>
    <strong>Argentina CU</strong>: el orgánico trae 20 veces más clics que el paid y no se compra lo que crece.</p>
   </div>
  </div>
 </div>
 <div class="cover-foot">{nota_marca(FECHA)}</div>
</section>'''

doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Pain points y solución actual por unidad · documento interno</title>
<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="estilo-ejecutivo.css">
</head><body>{cover}{"".join(out)}</body></html>'''
open(os.path.join(INF, "clientes.html"), "w", encoding="utf-8").write(doc)
print("-> informe/clientes.html")
