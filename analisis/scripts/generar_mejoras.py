# -*- coding: utf-8 -*-
"""
generar_mejoras.py — plan de mejoras de las campañas, unidad por unidad: pain point → mejora.
Cinco páginas. Números solo cuando cambian la decisión. Fuente: informe/datos_clientes.json.
"""
import json, os
from informe_util import n, pct, ars, e, hoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
C = json.load(open(os.path.join(INF, "datos_clientes.json"), encoding="utf-8"))
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))
SEO = json.load(open(os.path.join(INF, "datos_seo.json"), encoding="utf-8"))
U = {(c["propiedad"], c["pais"]): c for c in C["clientes"]}
s7 = D["s7"]


def camp(u, nombre):
    return next(x for x in u["campanas"] if x["camp_corta"] == nombre)


def row(pain, pain_txt, fix, fix_txt, tag=None):
    t = f'<span class="tag{" dec" if tag == "Decisión" else ""}">{e(tag)}</span>' if tag else ""
    return (f'<div class="row"><div class="pp"><div class="t">Pain point</div><h4>{pain}{t}</h4><p>{pain_txt}</p></div>'
            f'<div class="fix"><div class="t">Mejora</div><h4>{fix}</h4><p>{fix_txt}</p></div></div>')


def unit(u, lead, rows):
    a = u["ads"]
    marca = "Control Union" if u["marca"] == "CU" else "Peterson Solutions"
    return f'''<div class="unit">
 <div class="unit-bar"><div><div class="brand">{marca}</div><h2>{e(u["nombre"].replace("Control Union ", "").replace("Peterson Solutions ", "Peterson · "))}</h2></div>
  <div class="nums"><div><div class="v">{ars(a["gasto"])}</div><div class="k">gasto 6 semanas</div></div>
  <div><div class="v">{n(a["clics"])}</div><div class="k">clics</div></div><div><div class="v">{n(a["conv"])}</div><div class="k">conversiones</div></div>
  <div><div class="v">{n(a["campanas"])}</div><div class="k">campañas</div></div></div></div>
 <p class="lead">{lead}</p>{"".join(rows)}</div>'''


# ================================================================ CU España
u = U[("España", "esp")]; cae = camp(u, "CAEs"); iso = camp(u, "ISO 27001")
es = unit(u, "Once campañas. Cuatro se arreglan con negativos y exactas; las otras dos mejoras son abrir lo que la gente ya busca y no se compra.", [
    row("CAEs compra certificados de vivienda", f"{pct(cae['pct_fuera'])} del gasto visible ({ars(cae['desperdicio'])}) va a particulares que buscan el certificado energético de su piso, no al sistema CAE.",
        "Cerrar el mercado equivocado", "Negativos de vivienda (particular, gratis, ce3x, certicalia, online). La amplia pasa a frase. Exactas B2B: [sistema CAE], [verificación de actuaciones CAE], [sujeto delegado CAE]."),
    row("IFS paga genéricos de seguridad alimentaria", "Ninguna de las 9 keywords nombra IFS, y los términos IFS que sí entran no tienen keyword propia.",
        "Nombrar la norma", "Exactas [ifs food], [certificado ifs], [norma ifs], [auditoria ifs]. Grupos propios para ISO 22000 y FSSC 22000, que tienen página y demanda. BRCGS y cursos de manipuladores a negativo."),
    row("Textile paga OEKO-TEX", "ARS 15.362 en un esquema que Control Union no certifica. Cero búsquedas orgánicas en todo el histórico lo confirman.",
        "Negativizar y reforzar lo que sí", "oeko tex y organic cotton standard a negativo. Exactas [certificado gots], [sello gots], [grs global recycled standard]."),
    row("FSC llega a una landing de PEFC", "La filial certifica FSC y tiene página; el clic FSC hoy cae en Forestal/PEFC.",
        "Abrir grupo FSC", "Grupo de anuncios FSC con landing a la página de FSC. FSC sale de los negativos. «consultor fsc» sí va a negativo."),
    row("ISO 27001: ARS 6.019 por clic", "27 de 31 keywords sin una impresión; una sola concentra todo y sin tope de puja.",
        "Exactas con tope", "[iso 27001] y [certificarse en iso 27001] en exacta con CPC máximo. Eliminar renovación, transferencia y plazos."),
    row("Lo más buscado no tiene campaña", f"ISO 45001: {n(s7['iso45001_es']['impresiones'])} impresiones orgánicas con página propia y ninguna keyword. GMP+: 31 keywords que nunca publican mientras hay {n(s7['gmp_es']['impresiones'])} búsquedas.",
        "Campaña ISO 45001 y GMP+ rehecha", "ISO 45001 sobre la página que ya existe. GMP+ reconstruida con [gmp+], [gmp plus], [feed safety]: el vocabulario que la gente usa."),
])

# ================================================================ CU Portugal
u = U[("Portugal", "prt")]
can = D["canibalizacion"]["top"][0]
pt = unit(u, "Gasta un tercio de España con mejor foco. Los problemas son dos: paga un término que ya rankea tercero y no compra lo que más se busca.", [
    row("Plásticos paga recyclass, que ya rankea 3º", f"{ars(can['coste'])} por un término con posición orgánica {n(can['pos_org'],1)} en Portugal. Es la mitad de la campaña.",
        "Bajar la puja y medir", "recyclass a exacta con tope bajo, 30 días. Si el clic orgánico compensa, se pausa. UNE-EN 15343 se mantiene: no rankea."),
    row("FSC y GMP+, igual que España", "FSC entra por PEFC con página propia disponible. GMP+: 24 keywords, ninguna publicó.",
        "Grupo FSC · GMP+ rehecha", "Abrir grupo FSC con su landing. Reconstruir GMP+ con [gmp+], [gmp plus] o pausar la estructura vacía."),
    row("Siete campañas, ninguna sobre lo más buscado", "aquacultura (4.451 impresiones, posición 6) y rainforest alliance (posición 3,6) no tienen campaña.",
        "Campañas de defensa", "Grupos chicos en exacta para aquacultura y Rainforest Alliance: posición ganada, demanda probada, CPC contenido."),
])

# ================================================================ CU Canadá
u = U[("Norteamérica", "can")]; fo = camp(u, "Forestry"); cg = camp(u, "Canada Gap"); aq = camp(u, "Aqua / Fisheries")
ca = unit(u, "Segundo gasto del grupo sobre un sitio sin contenido para lo que compra. Dos pausas decididas y un presupuesto que cambia de destino.", [
    row("Forestry: la campaña más cara, sin sitio detrás", f"{ars(fo['coste'])} a {ars(4545)} el clic. El sitio no tiene contenido forestal: {n(s7['fsc_na']['impresiones'])} búsquedas de FSC en todo el histórico, ninguna desde Canadá.",
        "Pausar", "Pausar Forestry hasta que exista contenido forestal. Si se mantiene: exactas [fsc], [fsc canada], [fsc chain of custody] y negativos de credencial personal (rpf, forester license, courses)."),
    row("Aqua compra MSC, ASC y BAP sin página", f"{ars(aq['coste'])}: los 8 clics tienen buena intención y ninguna landing que los atienda.",
        "Pausar y reasignar", "Pausar. El presupuesto va a lo que sí tiene página y demanda: TEMO, collateral management, PrimusGFS."),
    row("CanadaGAP construida por hipótesis", f"38 de 45 keywords nunca se activaron; {pct(cg['pct_fuera'])} del gasto visible en supply chain, indocert y consultant.",
        "Reducir a lo que se busca", "Eliminar produce broker, packing house y repacking. Exactas [canada gap], [canadagap]. Negativos supply chain management, indocert, consultant."),
    row("TEMO: la mayor demanda de la propiedad, sin campaña", f"{n(s7['temo_na']['impresiones'])} impresiones orgánicas, posición {n(s7['temo_na']['pos'],1)}, y cayendo.",
        "Campaña TEMO", "Campaña TEMO con la página que ya rankea, financiada con lo que deja Forestry."),
])

# ================================================================ CU EE.UU.
u = U[("Norteamérica", "usa")]; nop = camp(u, "USDA NOP")
us = unit(u, "Paga el clic más caro del grupo por genéricos, mientras lo que rankea no tiene pauta.", [
    row("USDA NOP: ARS 6.326 por clic", f"43 de 51 keywords sin impresión. {pct(nop['pct_fuera'])} del gasto visible en organic chicken, omri y organic land.",
        "Negativos y exactas", "Negativos: organic chicken, chicken certification, omri, organic land. Exactas [certified organic], [national organic program]. Eliminar multi-site, switch certifier, importer. Confirmar el estado real de «Usda nop»."),
    row("PrimusGFS pagó consultoría", "ARS 20.951 en «gfsi consultant»: Control Union no asesora, y GFSI no es un esquema certificable.",
        "Regla de marca a nivel cuenta", "consultant, consultoría y advisor negativos en todas las campañas de Control Union. PrimusGFS reconstruida con [primusgfs], [primusgfs certification]."),
    row("Marca propia desde una campaña de producto", "«certified organic by control union» costó ARS 3.586 y ya rankea primero.",
        "Cortar", "Fuera de USDA NOP. Si se quiere proteger la marca, campaña de marca a CPC bajo."),
])

# ================================================================ CU Argentina
u = U[("Argentina", "arg")]; nc = {t["query"]: t for t in u["gsc"]["no_comprada"]}
ar = unit(u, "La unidad con menos gasto y mejor orgánico: en seis semanas el sitio trajo 446 clics solo y la pauta 23. El pain point es lo que no se compra.", [
    row("ISO 27001: una keyword hace todo", "24 de 31 sin impresión; «iso 27001» no es keyword y entra por variante. Competidores captura genéricos.",
        "Exactas y orden", "[iso 27001], [iso27001], [norma iso 27001], [certificacion 27001]. nist a negativo. Competidores solo con nombre de competidor, y «iso 27001» como negativo ahí."),
    row("SMETA y VISEC crecen solos y no tienen campaña", f"smeta: {n(nc['smeta']['impressions'])} impresiones, ×19 interanual. visec: {n(nc['visec']['impressions'])} en posición {n(nc['visec']['position'],1)}, ×39. SMETA sí se compra en España, Portugal y Canadá.",
        "Campaña SMETA · defensa VISEC", "Campaña SMETA Argentina sobre la página existente. VISEC y FSA en exacta, presupuesto chico: la posición ya está ganada."),
])

# ================================================================ PS Argentina
u = U[("Américas", "arg")]; ag = camp(u, "Agricultura regenerativa"); hc = camp(u, "Huella de carbono / GEI"); ha = camp(u, "Huella de agua"); bio = camp(u, "Bioenergia / Biocombustibles")
ps = unit(u, "La unidad con más clics y ninguna conversión: cuatro de ocho campañas compran búsquedas informativas o de otro negocio.", [
    row("Agricultura regenerativa: los clics más baratos, peor usados", f"La amplia «agricultura regenerativa en argentina» trae 219 de los {n(ag['clics'])} clics: marcas del agro, agtech y agronomía de nicho.",
        "Sacar la amplia", "Eliminar la amplia. Exactas [agricultura regenerativa], [ganadería regenerativa argentina], [agricultura sustentable en argentina]. Negativos: marcas del agro y tecnología agrícola."),
    row("Huella de carbono compra bonos de carbono", f"{pct(hc['pct_fuera'])} del gasto visible en bonos, mercado, créditos y carbono neutral: otro negocio, y Peterson no emite créditos.",
        "Cerrar el mercado y abrir el correcto", "Negativos de bonos, mercado, créditos, carbono neutral, iso 14001. Amplias a frase. Agregar [consultoria ambiental], [iso 14064], [inventario gei argentina]."),
    row("ESG paga números de estándar sueltos", "gri 403, gri 401, gri 304: alguien leyendo el indicador, no buscando quién arme el reporte.",
        "Negativos y lo que sí vende", "gri + número, «qué es» y «qué significa» a negativo. Agregar [csrd], [estandar gri], [consultora esg], [analisis de materialidad]."),
    row("Huella de agua: 100% fuera de foco", f"{ars(ha['coste'])} en tratamiento de efluentes y calculadoras gratis.",
        "Vocabulario corporativo", "Eliminar «gestion del agua industrial». Negativos tratamiento, efluentes, calculadora. Exactas [huella hidrica corporativa], [iso 14046]."),
    row("Bioenergía y CeSu no tienen mercado de servicio", f"Bioenergía {pct(bio['pct_fuera'])} fuera de foco (biogás, «qué es»). CeSu: 37 de 39 keywords que nadie busca.",
        "Pausar", "Pausar las dos. Si Bioenergía se rehace sobre ISCC y 2BSvs, antes hay que definir el corte con Control Union, que ya compra ISCC.", "Decisión"),
    row("El sitio no existe en orgánico en Argentina", f"Argentina es el {SEO['Américas']['pct_pais']}% de las impresiones de la propiedad y casi toda la visibilidad está en páginas en inglés.",
        "Páginas en español", "Una página en español por cada servicio que se paga. Hasta entonces, cada campaña compite sola contra sitios que sí hablan el idioma del cliente."),
])

# ================================================================ mercados sin inversión + orden
S = {s["propiedad"]: s for s in C["sin_campana"]}


def mk(p, txt, brand=None):
    s = S[p]; t = s["top"]
    return f'<div><h4>{("Peterson · " if brand else "") + e(p)}</h4><div class="d"><b>{n(s["clics"])} clics orgánicos sin invertir</b>{txt}</div></div>'


mercados = f'''<div class="page">
 <h2 class="sec-title">Donde no se invierte y ya se rinde</h2>
 <p class="sec-sub">Cinco propiedades sin campaña. Solo entre Perú, Brasil, México y Chile el orgánico trajo {n(sum(S[p]["clics_ads"] for p in ("Perú","Brasil","México","Chile")))} clics en las seis semanas del informe de Ads, más que las cuatro unidades de Control Union con campaña juntas. La mejora es la misma en todas: pauta de defensa chica donde la posición ya está ganada.</p>
 <div class="mk">
  {mk("Perú", "koa certification, haccp y rainforest alliance (posición 3,4) en primera página. Defensa en exacta sobre esos tres.")}
  {mk("México", "grs: la mayor demanda de GRS de toda la red, en posición 7,5. Un grupo GRS en exacta.")}
  {mk("Brasil", "obp, grs y gmp+ en primera página. Extender la campaña GMP+ rehecha cuando exista.")}
  {mk("Chile", "bap y asc con posición ganada. Todavía sin pauta: primero ordenar la búsqueda de marca.")}
  {mk("Iberia", "csrd y cbam en página 2–3. Es territorio de Peterson, no de las campañas de Control Union: primero contenido, después pauta.", True)}
 </div>
 <h2 class="sec-title" style="margin-top:10mm">Orden de ejecución</h2>
 <p class="sec-sub">Los dos primeros bloques no dependen de ninguna decisión y se hacen en días. El tercero necesita definiciones.</p>
 <div class="steps">
  <div><div class="w">Esta semana · sin riesgo</div><h4>Cerrar lo que sobra</h4><ul>
   <li>Negativos de cada unidad, y consultant / consultoría / advisor a nivel cuenta en Control Union.</li>
   <li>Pausar Forestry y Aqua en Canadá; Huella de agua queda con vocabulario nuevo.</li>
   <li>Cortar marca propia de USDA NOP y Textile.</li>
   <li>Limpiar las 681 keywords sin impresión.</li></ul></div>
  <div><div class="w">Próximas dos semanas</div><h4>Comprar lo que se busca</h4><ul>
   <li>Exactas en todas las campañas que hoy entran por variante: IFS, ISO 27001 (ES y AR), GOTS/GRS, CanadaGAP, PrimusGFS, NOP.</li>
   <li>Grupos FSC en España y Portugal. ISO 22000 y FSSC en España.</li>
   <li>Campañas nuevas: ISO 45001 (ES), SMETA (AR), TEMO (CA). GMP+ rehecha en ES y PT.</li>
   <li>recyclass Portugal a exacta con tope; medir 30 días.</li></ul></div>
  <div><div class="w">Requiere decisión</div><h4>Lo que no se resuelve con datos</h4><ul>
   <li>Pausar Bioenergía y CeSu en Peterson Argentina.</li>
   <li>Corte de marca en ISCC: Control Union ya lo compra en España y Portugal.</li>
   <li>Presupuesto para los mercados sin campaña.</li>
   <li>Páginas en español para Peterson en Argentina: sin eso, la pauta compite sola.</li></ul></div>
 </div>
 <div class="navy-box"><h4>Cómo saber si funcionó, en 30 días</h4>
  <p>El desperdicio visible en el informe de términos de búsqueda por debajo del <b>10%</b> (hoy {pct(round(C["clientes"][0]["ads"]["desperdicio"] / C["clientes"][0]["ads"]["visible"] * 100))} en España, {pct(round(U[("Américas","arg")]["ads"]["desperdicio"] / U[("Américas","arg")]["ads"]["visible"] * 100))} en Peterson Argentina). Y que las campañas nuevas (ISO 45001, SMETA Argentina, TEMO) tengan clics con intención de servicio antes de hablar de conversiones: con 4 en seis semanas, la conversión todavía no dice nada.</p></div>
 <p class="foot">Documento interno. Cubre unidades de Control Union y de Peterson Solutions; por eso no lleva identidad de marca y usa solo los colores comunes a los dos manuales. Cada mejora se ejecuta dentro de su propia marca. Fuentes: Google Ads (1 ago – 11 sep 2026) y Search Console (histórico completo). Generado el {hoy()}.</p>
</div>'''

# ================================================================ portada
tot_gasto = C["ads_total"]; tot_desp = sum(U[k]["ads"]["desperdicio"] for k in U)
cover = f'''<div class="cover">
 <div class="hero">
  <div class="eyebrow">Plan de mejoras · campañas de búsqueda · Control Union y Peterson Solutions</div>
  <h1>Qué está mal en cada campaña y qué se hace con eso</h1>
  <p class="sub">Seis unidades con inversión, {sum(len(c["campanas"]) for c in C["clientes"])} campañas, un pain point por problema y una mejora por pain point. Sin metodología: eso está en los informes largos.</p>
  <div class="hero-nums">
   <div><div class="n">{ars(tot_gasto)}</div><div class="l">gasto en seis semanas</div></div>
   <div><div class="n">{n(C["ads_conv"])}</div><div class="l">conversiones</div></div>
   <div><div class="n">{ars(tot_desp)}</div><div class="l">gasto visible fuera de foco</div></div>
   <div><div class="n">681</div><div class="l">keywords que nunca se activaron</div></div>
  </div>
 </div>
 <div class="top5">
  <h2>Las cinco mejoras que más pesan</h2>
  <div class="move"><div class="num">1</div><div><h3>Pausar Forestry y Aqua en Canadá</h3><p>{ars(camp(U[("Norteamérica","can")], "Forestry")["coste"] + camp(U[("Norteamérica","can")], "Aqua / Fisheries")["coste"])} sobre un sitio sin contenido forestal ni acuícola. El presupuesto pasa a TEMO, que sí tiene página y demanda.</p></div></div>
  <div class="move"><div class="num">2</div><div><h3>Sacar la amplia de Agricultura regenerativa y cerrar el mercado de bonos de carbono</h3><p>Las dos campañas más grandes de Peterson compran búsquedas de otro negocio. Negativos, amplias a frase, exactas de lo que Peterson sí vende.</p></div></div>
  <div class="move"><div class="num">3</div><div><h3>Abrir ISO 45001 en España</h3><p>{n(s7["iso45001_es"]["impresiones"])} búsquedas orgánicas con página propia y ninguna keyword. Es la demanda más grande del grupo sin comprar.</p></div></div>
  <div class="move"><div class="num">4</div><div><h3>Negativos a nivel cuenta en Control Union: consultant, consultoría, advisor</h3><p>Regla de marca. Ya costó ARS 20.951 en un solo término de PrimusGFS.</p></div></div>
  <div class="move"><div class="num">5</div><div><h3>Corregir FSC: grupo propio en España y Portugal</h3><p>La auditoría proponía negativizarlo. Las dos filiales certifican FSC y tienen página; el clic hoy cae en PEFC.</p></div></div>
 </div>
</div>'''

if __name__ == "__main__":
    doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan de mejoras · campañas de búsqueda</title>
<link rel="stylesheet" href="estilo-mejoras.css"></head><body>
{cover}
<div class="page">{es}{pt}</div>
<div class="page">{ca}{us}</div>
<div class="page">{ar}{ps}</div>
{mercados}
</body></html>'''
    open(os.path.join(INF, "mejoras.html"), "w", encoding="utf-8").write(doc)
    print("-> informe/mejoras.html")
