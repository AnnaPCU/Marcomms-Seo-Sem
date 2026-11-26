# -*- coding: utf-8 -*-
"""
unificar_tarjetas_sem.py — reorganiza las tarjetas SEM del tablero con el criterio de Felipe (21 oct 2026):

  1. Una acción, una tarjeta: cuando una campaña tiene una tarjeta de «plan» (keywords/negativas) y otra de «anuncio»
     que repiten la misma acción, quedan en una sola tarjeta por campaña (ficha «campana»). Se actualiza en el lugar la
     de anuncio (conserva id, estado e historial) y la de plan pasa a «descartada» con «Unificada en…».
  2. Grupo nuevo → siempre con keywords recomendadas y una decisión explícita sobre negativas.
  3. Ajuste de anuncio → el motivo del cambio y, por cada título/descripción propuesto, su motivo; las que conviene
     hacer sí o sí van destacadas (prioritario).
  4. Siempre dice dónde: nombre completo de la campaña y, si toca un grupo o un anuncio, cuál (con su id).

Lee informe/recomendaciones.json (texto de las tarjetas), el snapshot de estructura más reciente y los reportes de
anuncios de la ventana más reciente. Escribe informe/unificacion_sem_2026-10.sql (para el conector de Supabase).
ISCC (CU Argentina - Biocombustible) y EUDR (CU Argentina - Agroexportación) se reescriben a mano con datos al 21 oct.
"""
import glob, json, os, re
import pandas as pd
from aplicar_revision import validar_campana

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
MES = "2026-10"
USUARIO = "Unificación de tarjetas (Claude)"
FECHA_DATOS = "21 oct 2026"
VENTANA = "1 sep – 20 oct 2026"

R = {r["clave"]: r for r in json.load(open(os.path.join(ROOT, "informe", "recomendaciones.json"), encoding="utf-8"))}
SNAP = sorted(glob.glob(os.path.join(API, "estructura_*")))[-1]
ANUNCIOS = pd.read_csv(os.path.join(SNAP, "anuncios.csv"), encoding="utf-8-sig")
ANUNCIOS = ANUNCIOS[ANUNCIOS["ad_group_ad.status"] == "ENABLED"]
MET = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in glob.glob(os.path.join(API, "*", "ads_*_anuncios_2026-09-01_2026-10-20.csv"))])
MET = MET.groupby("ad_group_ad.ad.id").agg(clics=("metrics.clicks", "sum"), coste=("metrics.cost_micros", "sum")).reset_index()
FUERZA = {"POOR": "Pobre", "AVERAGE": "Promedio", "GOOD": "Buena", "EXCELLENT": "Excelente", "PENDING": "pendiente", "UNSPECIFIED": "—"}
ORDEN_FUERZA = {"POOR": 0, "AVERAGE": 1, "GOOD": 2, "EXCELLENT": 3}
PRIORIDAD = {"baja": 0, "media": 1, "alta": 2}
PROHIBIDO = {"CU": r"\b(asesor\w*|consultor\w*|te explicamos|diseñamos (tu|su) estrategia)\b", "PCU": r"\b(asesor\w*|consultor\w*|te explicamos)\b", "PS": r"\bcertificamos\b"}


def anuncios_del_grupo(campana, grupo):
    a = ANUNCIOS[(ANUNCIOS["campaign.name"] == campana) & (ANUNCIOS["ad_group.name"] == grupo)].copy()
    a["orden"] = a["ad_group_ad.ad_strength"].map(ORDEN_FUERZA).fillna(9)
    a = a.merge(MET, on="ad_group_ad.ad.id", how="left").fillna({"clics": 0, "coste": 0})
    return a.sort_values("orden")


def corta(campana):
    return re.sub(r"\s*-\s*search\s*$", "", campana, flags=re.I)


def bloque_anuncio_auto(campana, rec):
    """Anuncio de una tarjeta vieja + el anuncio vigente en la cuenta (id, fuerza, títulos de hoy)."""
    ev, grupo = rec["evidencia"], rec.get("grupo")
    vig = anuncios_del_grupo(campana, grupo)
    hoy_t, hoy_d, ad_id, desc, url = ev.get("titulos_hoy") or [], [], None, None, ev.get("url") or None
    gasto, clics = ev.get("gasto_ars"), None
    if len(vig):
        x = vig.iloc[0]
        ad_id = str(x["ad_group_ad.ad.id"])
        hoy_t = [t.strip() for t in str(x["ad_group_ad.ad.responsive_search_ad.headlines"]).split("|") if t.strip()]
        hoy_d = [t.strip() for t in str(x["ad_group_ad.ad.responsive_search_ad.descriptions"]).split("|") if t.strip()]
        url = str(x["ad_group_ad.ad.final_urls"]).strip("[]'\" ") or url
        gasto, clics = round(x["coste"] / 1e6), int(x["clics"])
        miles = f"{gasto:,.0f}".replace(",", ".")
        desc = f"fuerza {FUERZA.get(x['ad_group_ad.ad_strength'], x['ad_group_ad.ad_strength'])}, {clics} clics y ARS {miles} del {VENTANA}"
        if len(vig) > 1:
            desc += f"; el grupo tiene {len(vig)} anuncios activos y el cambio va en este, el de fuerza más baja"
    ya = {t.lower() for t in hoy_t + hoy_d}
    tit = [t for t in ev.get("titulos_propuestos") or [] if t.lower() not in ya]
    des = [t for t in ev.get("descripciones_propuestas") or [] if t.lower() not in ya]
    cargados = [t for t in (ev.get("titulos_propuestos") or []) + (ev.get("descripciones_propuestas") or []) if t.lower() in ya]
    return {
        "grupo": grupo, "anuncio_id": ad_id, "anuncio_desc": desc, "accion": ev.get("cambio") or "Ajustar", "motivo": ev.get("diagnostico"),
        "url": url, "gasto_ars": gasto, "clics": clics, "ventanas": VENTANA if ad_id else ev.get("ventanas"),
        "titulos_hoy": hoy_t, "descripciones_hoy": hoy_d, "quitar": ev.get("quitar") or [],
        "titulos_propuestos": tit, "descripciones_propuestas": des, "terminos": ev.get("terminos") or [], "nota": ev.get("nota"),
    }, cargados


# pares de una misma campaña: (tarjeta de anuncio que queda, tarjeta de plan que se unifica)
PARES = [
    ("CU:SEM:anuncio:cu-espana-caes:certificados-y-sistema-cae", "CU:SEM:plan:espana:caes-sigue-comprando-certificados-de-vivienda"),
    ("CU:SEM:anuncio:cu-espana-ifs:food-safety", "CU:SEM:plan:espana:ifs-genericos-y-sin-exactas"),
    ("CU:SEM:anuncio:cu-espana-smeta:social", "CU:SEM:plan:espana:smeta-compra-nombres-de-competidores"),
    ("CU:SEM:anuncio:cu-portugal-plasticos:une-15343", "CU:SEM:plan:portugal:plasticos-sigue-pagando-recyclass-que-rankea-3o"),
    ("CU:SEM:anuncio:cu-portugal-textile:gots", "CU:SEM:plan:portugal:textile-bien-con-ruido-nuevo"),
    ("CU:SEM:anuncio:cu-united-states-organic-usda-nop:switch-get-certified", "CU:SEM:plan:estados-unidos:usda-nop-el-triple-en-busquedas-de-definicion"),
    ("PS:SEM:anuncio:ps-argentina-suse-esg-reportes:reportes-esg", "PS:SEM:plan:argentina:esg-la-mas-sana-con-los-mismos-huecos"),
    ("PS:SEM:anuncio:ps-argentina-suse-huella-de-agua:gestion-agua", "PS:SEM:plan:argentina:huella-de-agua-3-y-100-fuera-de-foco"),
]

# tarjetas que abarcan varias campañas (una sola acción para todas) o que no tenían campaña: se nombran todas
CAMPANAS_EXPLICITAS = {
    "CU:SEM:plan:canada:canadagap-y-globalg-a-p-sin-los-negativos": ["CU Canada - Canada Gap - Search", "CU Canada - GLOBALG.A.P. - Search"],
    "CU:SEM:plan:canada:forestry-y-aqua-siguen-activas": ["CU Canada - Forestry - Search", "CU Canada- Aqua / Fisheries - Search"],
    "CU:SEM:plan:espana:textile-paga-oeko-tex-y-forestal-compra-sostenibilidad": ["CU España - Textile - Search", "CU España - Forestal - Search"],
    "CU:SEM:plan:portugal:fsc-entra-por-pefc-gmp-vacia-biomasa-desperto": ["CU Portugal - Forestal - Search", "CU Portugal - GMP+ - SEARCH", "CU Portugal - Biomasa - Search"],
    "CU:SEM:plan:argentina:cadena-de-custodia-y-agro-sostenible-no-publican": ["CU Argentina - Cadena de Custodia - Search", "CU Argentina - Agro sostentible - Search"],
    "PS:SEM:plan:argentina:agricultura-regenerativa-y-huella-de-carbono-sin-cambios": ["PS Argentina - SuSo - Agricultura regenerativa- Search", "PS Argentina - SuSe - Huella de carbono / GEI - Search"],
    "PS:SEM:plan:argentina:bioenergia-2-y-sigue-en-biogas": ["PS Argentina - Bioenergia / Biocombustibles - Search", "PS Argentina - CeSu - Preparacion para certificaciones - Search"],
    "PCU:SEM:plan:espana-y-argentina:la-exacta-iso-27001-sigue-sin-existir": ["PCU - España - ISO 27001 - Search", "PCU - Argentina - ISO 27001 - Search"],
    "PCU:SEM:plan:espana-y-argentina:busquedas-informativas-a-ars-6-000-el-clic": ["PCU - Argentina - ISO 27001 - Search", "PCU - España - ISO 27001 - Search"],
    "PCU:SEM:plan:espana-y-argentina:se-llama-pcu-y-ninguna-marca-certifica-asi": ["PCU - Argentina - ISO 27001 - Search", "PCU - Argentina - Competidores ISO 27001 - Search", "PCU - España - ISO 27001 - Search", "PCU - España - Competidores ISO 27001 - Search"],
    "PCU:SEM:plan:espana-y-argentina:competidores-espana-desperto-con-relevancia-baja": ["PCU - España - Competidores ISO 27001 - Search"],
    "CU:SEM:plan:argentina:eudr-funciona-con-dos-terminos-que-no-son-cliente": ["CU Argentina - Agroexportación - Search"],
    "CU:SEM:plan:argentina:smeta-argentina-ya-existe-era-la-mejora-no5": ["CU Argentina - Industria - Search"],
    "CU:SEM:plan:espana:iso-45001-la-mayor-demanda-sigue-sin-campana": ["CU España - ISO 45001 - Search (campaña nueva, a crear)"],
    "PS:SEM:plan:argentina:el-sitio-sigue-sin-existir-en-argentina": ["Todas las campañas de PS Argentina (8)"],
}


def unificar(clave_anuncio, clave_plan):
    a, p = R[clave_anuncio], R[clave_plan]
    campana = a["campana"]
    ea, ep = a["evidencia"], p["evidencia"]
    anuncio, cargados = bloque_anuncio_auto(campana, a)
    acciones = [x for x in ["anuncio", "keywords", "negativas", "estructura", "pausa", "landing", "revisar"] if x in set(ea.get("acciones", [])) | set(ep.get("acciones", []))]
    grupo = a.get("grupo")
    pasos = [
        {"accion": next((x for x in ep.get("acciones", []) if x != "anuncio"), "keywords"), "titulo": ep.get("mejora") or "Mejora de la campaña",
         "donde": "Toda la campaña", "detalle": ep.get("mejora_txt")},
        {"accion": "anuncio", "titulo": f"{(ea.get('cambio') or 'Ajustar')} el anuncio del grupo «{grupo}»",
         "donde": f"Grupo «{grupo}»" + (f" · anuncio id {anuncio['anuncio_id']}" if anuncio["anuncio_id"] else ""),
         "detalle": "Cargar los títulos y descripciones de abajo." + (f" {ea['nota']}" if ea.get("nota") else "")},
    ]
    mejora = ep.get("mejora") or ""
    mejora = mejora[:1].lower() + mejora[1:] if mejora[1:2].islower() else mejora
    titulo = f"{corta(campana)}: {mejora} · {(ea.get('cambio') or 'ajustar').lower()} el anuncio de «{grupo}»"
    ev = {
        "ficha": "campana", "unidad": ea.get("unidad") or ep.get("unidad"), "campana": campana, "acciones": acciones,
        # el diagnóstico es del análisis de septiembre: se dice de cuándo es
        "resumen": titulo, "por_que": "Al 24 sep: " + " ".join(x for x in [ep.get("pain"), ep.get("pain_txt")] if x),
        "ya_hecho": ("Ya están cargados en el anuncio, de lo que se propuso en septiembre: " + " · ".join(f"«{c}»" for c in cargados) + ".") if cargados else None,
        "pasos": pasos, "anuncios": [anuncio], "organico": ea.get("organico") or ep.get("organico"),
        "organico_desde": ea.get("organico_desde") or ep.get("organico_desde"), "organico_hasta": ea.get("organico_hasta") or ep.get("organico_hasta"),
        "datos_hasta": FECHA_DATOS, "unifica": [clave_anuncio, clave_plan],
    }
    detalle = f"{ep.get('mejora_txt') or ''}\n\nAnuncio del grupo «{grupo}»: {ea.get('diagnostico') or ''}".strip()
    prio = max(a.get("prioridad", "media"), p.get("prioridad", "media"), key=PRIORIDAD.get)
    return {"clave": clave_anuncio, "titulo": titulo, "detalle": detalle, "prioridad": prio, "evidencia": ev, "grupo": grupo, "campana": campana,
            "descarta": clave_plan}


# ─────────────────────────────── ISCC · CU Argentina - Biocombustible (a mano, datos al 21 oct)
def P(texto, motivo=None, prioritario=False, reemplaza=None):
    return {k: v for k, v in dict(texto=texto, motivo=motivo, prioritario=prioritario or None, reemplaza=reemplaza).items() if v}


ISCC_CAMP = "CU Argentina - Biocombustible - Search"
iscc_rfs = anuncios_del_grupo(ISCC_CAMP, "RFS2 compra").iloc[0]
ISCC = {
    "clave": "CU:SEM:anuncio:cu-argentina-biocombustible:iscc",
    "campana": ISCC_CAMP, "grupo": "ISCC EU compra", "prioridad": "alta", "descarta": "CU:SEM:plan:argentina:biocombustible-keywords-iscc-anuncio-2bsvs",
    "titulo": "Biocombustible: la separación por esquema ya está; faltan negativas en ISCC y decidir «soja epa» (75% del gasto)",
    "detalle": "La campaña ya tiene un grupo por esquema con su anuncio y su landing. Falta: (1) negativas para las búsquedas en inglés de quien navega "
               "el sitio de ISCC, (2) tres exactas en «ISCC EU compra» y (3) decidir la keyword «soja epa» del grupo «RFS2 compra»: se lleva el 75% "
               "del gasto con nivel de calidad 1 porque ni el anuncio ni la landing nombran la soja.",
    "evidencia": {
        "ficha": "campana", "unidad": "Argentina", "campana": ISCC_CAMP, "acciones": ["negativas", "keywords", "anuncio", "revisar"],
        "resumen": "Cerrar la separación por esquema: negativas, exactas en ISCC EU y una decisión sobre «soja epa».",
        "por_que": f"{VENTANA}: 30 clics y ARS 53.620, sin conversiones. Solo gastan dos grupos. «RFS2 compra» se llevó ARS 40.393 (75%) con una sola "
                   "keyword, «soja epa», que tiene nivel de calidad 1 de 10: la landing de RFS2 no menciona la soja ni «soja EPA», el anuncio tampoco, y "
                   "parte de las búsquedas son de definición («que significa soja epa», ARS 2.408 por un clic). En «ISCC EU compra» (ARS 13.226) la "
                   "keyword «iscc certificacion» entra en búsquedas en inglés de quien busca la base de certificados o el sitio de ISCC («iscc "
                   "certificates», «iscc client section», «iscc hub», «logo iscc»): «iscc carbon» costó ARS 5.272 por un solo clic.",
        "ya_hecho": "La campaña ya tiene un grupo por esquema, cada uno con su anuncio y su landing: «ISCC EU compra», «ISCC sector», «ISCC plus compra», "
                    "«ISCC CORSIA compra», «2BS compra» y «RFS2 compra» (estructura al 21 oct). Era lo que pedían las dos tarjetas de septiembre "
                    "(«Un grupo por esquema» y «Grupo nuevo con anuncio propio: ISCC»), que quedan unificadas en esta. ISCC sector, ISCC PLUS, CORSIA "
                    "y 2BS todavía no tuvieron impresiones: por ahora no se tocan.",
        "pasos": [
            {"accion": "negativas", "titulo": "Cargar 9 negativas", "donde": "Toda la campaña (8) y grupo «ISCC EU compra» (1)",
             "detalle": "Cortan las búsquedas de quien navega el sitio de ISCC y una de definición. Las negativas de campaña que ya existen están bien."},
            {"accion": "keywords", "titulo": "Sumar tres exactas en «ISCC EU compra»", "donde": "Grupo «ISCC EU compra»",
             "detalle": "Sin pausar la frase «iscc certificacion»: con las negativas del paso 1 deja de traer las búsquedas en inglés."},
            {"accion": "revisar", "titulo": "Decidir la keyword «soja epa»", "donde": "Grupo «RFS2 compra» · keyword «soja epa» (frase)",
             "detalle": "Confirmar con Control Union Argentina si el servicio de RFS2 incluye verificar soja EPA (soja para biodiésel a EE. UU.).\n"
                        "· Si sí: cargar el ajuste de anuncio del paso 4, sumar la exacta [soja epa] y pedir que la landing de RFS2 nombre «soja EPA».\n"
                        "· Si no: pausar «soja epa». Hoy se lleva el 75% del presupuesto de la campaña sin respaldo en la landing."},
            {"accion": "anuncio", "titulo": "Si se confirma: ajustar el anuncio de «RFS2 compra»", "donde": f"Grupo «RFS2 compra» · anuncio id {iscc_rfs['ad_group_ad.ad.id']}",
             "detalle": "Tres títulos y una descripción; el resto del anuncio queda igual."},
        ],
        "keywords": [
            {"texto": "certificacion iscc", "concordancia": "exacta", "grupo": "ISCC EU compra", "accion": "agregar",
             "motivo": "Es la búsqueda principal en castellano. En exacta se paga solo eso; hoy entra por la frase «iscc certificacion», que también trae búsquedas en inglés."},
            {"texto": "certificado iscc", "concordancia": "exacta", "grupo": "ISCC EU compra", "accion": "agregar",
             "motivo": "1 clic a ARS 228 en el período y 31 impresiones orgánicas en posición 4,8: hay demanda real y barata."},
            {"texto": "iscc eu", "concordancia": "exacta", "grupo": "ISCC EU compra", "accion": "agregar",
             "motivo": "9 impresiones sin clic, entrando por otra keyword. En exacta y con el anuncio de ISCC EU gana relevancia."},
            {"texto": "soja epa", "concordancia": "frase", "grupo": "RFS2 compra", "accion": "decidir (paso 3)",
             "motivo": "Nivel de calidad 1 de 10, 15 clics y ARS 40.393: el 75% de la campaña."},
            {"texto": "soja epa", "concordancia": "exacta", "grupo": "RFS2 compra", "accion": "agregar solo si se confirma",
             "motivo": "Si el servicio existe, la exacta controla el costo de la búsqueda más cara y deja a la frase solo las variantes."},
        ],
        "negativas": [
            {"texto": "certificates", "concordancia": "frase", "nivel": "campaña",
             "motivo": "«iscc certificates», «iscc all certificates», «iscc valid certificates»: buscan un certificado ajeno en la base de ISCC, no una certificadora. 4 clics, ARS 2.407."},
            {"texto": "iscc carbon", "concordancia": "exacta", "nivel": "campaña", "motivo": "Es el nombre de la organización (International Sustainability and Carbon Certification): ARS 5.272 por un clic."},
            {"texto": "hub", "concordancia": "frase", "nivel": "campaña", "motivo": "«iscc hub», la plataforma de ISCC para sus usuarios: ARS 1.992 por un clic."},
            {"texto": "client section", "concordancia": "frase", "nivel": "campaña", "motivo": "Acceso de clientes del sitio de ISCC: navegación, no compra."},
            {"texto": "logo", "concordancia": "frase", "nivel": "campaña", "motivo": "«logo iscc», «iscc logo»: buscan la imagen del sello."},
            {"texto": "material list", "concordancia": "frase", "nivel": "campaña", "motivo": "Lista de materiales que publica ISCC («iscc material list 2026»)."},
            {"texto": "list of materials", "concordancia": "frase", "nivel": "campaña", "motivo": "La misma lista, escrita de otra forma."},
            {"texto": "que significa", "concordancia": "frase", "nivel": "campaña",
             "motivo": "«que significa soja epa» costó ARS 2.408. La campaña ya bloquea «significado» y «que es», pero no «que significa»."},
            {"texto": "plus", "concordancia": "amplia", "nivel": "grupo", "grupo": "ISCC EU compra",
             "motivo": "Para que las búsquedas de ISCC PLUS vayan al grupo «ISCC plus compra», que tiene su anuncio y su landing, y no a ISCC EU."},
        ],
        "negativas_decision": "Sí hay que ajustar negativas: 9 nuevas (8 de campaña y 1 de grupo). Las de campaña que ya existen (gratis, curso, "
                              "consultoría, «que es», precio del biodiésel…) están bien y no se tocan.",
        "anuncios": [{
            "grupo": "RFS2 compra", "anuncio_id": str(iscc_rfs["ad_group_ad.ad.id"]),
            "anuncio_desc": f"fuerza {FUERZA[iscc_rfs['ad_group_ad.ad_strength']]}, único anuncio del grupo, 15 clics y ARS 40.393 del {VENTANA}",
            "accion": "Ajustar si se confirma el servicio",
            "motivo": "La keyword que más gasta es «soja epa» y ni el anuncio ni la landing la nombran: por eso Google le da nivel de calidad 1 y cada clic "
                      "sale más caro. Nombrarla en títulos y en una descripción es lo que más sube la relevancia. Solo si Control Union verifica soja EPA.",
            "url": str(iscc_rfs["ad_group_ad.ad.final_urls"]).strip("[]'\" "), "gasto_ars": 40393, "clics": 15, "ventanas": VENTANA,
            "titulos_hoy": [t.strip() for t in str(iscc_rfs["ad_group_ad.ad.responsive_search_ad.headlines"]).split("|")],
            "descripciones_hoy": [t.strip() for t in str(iscc_rfs["ad_group_ad.ad.responsive_search_ad.descriptions"]).split("|")],
            "quitar": [
                {"texto": "Renewable Fuel Standard 2", "motivo": "Repite «RFS2», que ya está en otros cuatro títulos."},
                {"texto": "Certificadora RFS2", "motivo": "Casi igual a «Certificación RFS2»: Google no puede combinarlos."},
                {"texto": "80+ países, 274+ oficinas", "motivo": "Respaldo genérico; ya está «100+ años certificando»."},
                {"texto": "Auditores propios en Argentina con experiencia en plantas de biodiésel y aceiteras.",
                 "motivo": "Repite el título «Auditores en Argentina» y la cuarta descripción («auditores propios en Argentina»)."},
            ],
            "titulos_propuestos": [
                P("Verificación Soja EPA", "Repite la búsqueda que paga el 75% de la campaña: es lo que más sube la relevancia.", True, "Renewable Fuel Standard 2"),
                P("Soja EPA para EE. UU.", "Une la búsqueda con el destino del servicio, que es lo que define a quien compra.", True, "Certificadora RFS2"),
                P("Soja y biodiésel para la EPA", "Cubre las búsquedas que mezclan soja y EPA sin nombrar RFS2.", False, "80+ países, 274+ oficinas"),
            ],
            "descripciones_propuestas": [
                P("Verificamos soja EPA y biodiésel para exportar a EE. UU. bajo el RFS2 de la EPA.",
                  "Pone «soja EPA» en el texto largo del anuncio, con el verbo de Control Union y el destino.", True,
                  "Auditores propios en Argentina con experiencia en plantas de biodiésel y aceiteras."),
            ],
            "terminos": [
                {"termino": "soja epa", "relacion": "nula", "coste": 6756, "clics": 3},
                {"termino": "soja epa requisitos", "relacion": "nula", "coste": 4220, "clics": 1},
                {"termino": "que significa soja epa", "relacion": "nula", "coste": 2408, "clics": 1},
                {"termino": "soja epa eudr", "relacion": "nula", "coste": 0, "clics": 0},
                {"termino": "soja sustentable epa", "relacion": "nula", "coste": 0, "clics": 0},
            ],
            "nota": "Si el servicio no incluye soja EPA, no cargar estos textos: pausar la keyword (paso 3). Los términos visibles suman ARS 13.384; "
                    "el resto de los ARS 40.393 Google lo agrupa como «otros términos».",
        }],
        "organico": R["CU:SEM:anuncio:cu-argentina-biocombustible:iscc"]["evidencia"].get("organico"),
        "organico_desde": "Argentina", "organico_hasta": "14 sep 2026", "datos_hasta": FECHA_DATOS,
        "unifica": ["CU:SEM:anuncio:cu-argentina-biocombustible:iscc", "CU:SEM:plan:argentina:biocombustible-keywords-iscc-anuncio-2bsvs"],
    },
}

# ─────────────────────────────── EUDR · CU Argentina - Agroexportación (a mano, datos al 21 oct)
EUDR_CAMP = "CU Argentina - Agroexportación - Search"
eu = anuncios_del_grupo(EUDR_CAMP, "EUDR proceso").set_index("ad_group_ad.ad.id")
debil, otro = 824719684469, 824719684472
partes = lambda ad, col: [t.strip() for t in str(eu.loc[ad, col]).split("|")]
EUDR = {
    "clave": "CU:SEM:anuncio:cu-argentina-agroexportacion:eudr-proceso",
    "campana": EUDR_CAMP, "grupo": "EUDR proceso", "prioridad": "alta",
    "titulo": "EUDR proceso: que el anuncio ofrezca la verificación y no explique el reglamento (98 clics, ARS 114.313, 0 conversiones)",
    "detalle": "Los dos anuncios del grupo «EUDR proceso» atraen a quien quiere aprender el reglamento: los títulos con más clics son «EUDR paso a paso», "
               "«Cómo cumplir EUDR» y «Qué exige EUDR», y la descripción más clickeada dice «Te explicamos…», tono de consultora. Además prometen una "
               "«Certificación EUDR» y un «Organismo acreditado» que no existen: EUDR se verifica. Reescribir el anuncio débil, corregir el otro y cerrar "
               "la búsqueda suelta «eudr» en este grupo.",
    "evidencia": {
        "ficha": "campana", "unidad": "Argentina", "campana": EUDR_CAMP, "acciones": ["anuncio", "keywords", "negativas"],
        "resumen": "Pasar el grupo de «te explicamos EUDR» a «verificamos tu cadena EUDR».",
        "por_que": f"{VENTANA}: el grupo «EUDR proceso» llevó 98 clics y ARS 114.313 sin ninguna conversión. Los títulos que más clics traen responden a "
                   "quien quiere aprender («EUDR paso a paso» 55, «Cómo cumplir EUDR» 45, «Reglamento 2023/1115» 38, «Qué exige EUDR» 37) y la "
                   "descripción con más clics promete explicar («Te explicamos qué documentación…», 61): es el tono de una consultora, que Control Union "
                   "no usa, y atrae estudiantes, despachantes y curiosos. Un tercio del gasto entra por la búsqueda suelta «eudr» (18 clics, ARS 35.656) a "
                   "través de la keyword «reglamento deforestacion union europea». Y tres títulos prometen algo que no existe: «Certificación EUDR», "
                   "«Certificación de origen» y «Organismo acreditado». EUDR no tiene certificación ni acreditación; lo que hace Control Union es verificar "
                   "la debida diligencia, y la landing no menciona ninguna acreditación.",
        "ya_hecho": "La negativa «que significa» ya está en el grupo y en la campaña, junto con «que es», «resumen» y «definicion» (era la tarjeta "
                    "«Negativos de definición», hecha). El anuncio id 824719684472 ya tiene «Verificación EUDR Argentina», que se propuso en septiembre "
                    "y es su título con intención de compra que mejor anda (11 clics).",
        "pasos": [
            {"accion": "anuncio", "titulo": "Reescribir el anuncio débil", "donde": f"Grupo «EUDR proceso» · anuncio id {debil} (fuerza Pobre)",
             "detalle": "Reemplazar los títulos y descripciones marcados. Es el de fuerza Pobre y el que menos rinde por clic: conviene rehacerlo y dejar "
                        "el otro casi igual para comparar los dos durante 30 días."},
            {"accion": "anuncio", "titulo": "Corregir el otro anuncio, sin rehacerlo", "donde": f"Grupo «EUDR proceso» · anuncio id {otro} (fuerza Promedio)",
             "detalle": "Solo tres cambios: sacar «Organismo acreditado» y «Certificación de origen», y cambiar la descripción «Te explicamos…». "
                        "Sus títulos informativos («EUDR paso a paso», «Cómo cumplir EUDR») quedan: son el punto de comparación."},
            {"accion": "keywords", "titulo": "Pasar «reglamento deforestacion union europea» a exacta", "donde": "Grupo «EUDR proceso»",
             "detalle": "Es la keyword que trae la búsqueda suelta «eudr» y el 57% del gasto del grupo."},
            {"accion": "negativas", "titulo": "Sumar dos negativas", "donde": "Grupo «EUDR proceso» (1) y toda la campaña (1)"},
            {"accion": "revisar", "titulo": "En 30 días, comparar los dos anuncios", "donde": "Grupo «EUDR proceso»",
             "detalle": "Mirar clics, costo y contactos de cada uno. Si el reescrito consigue contactos con menos clics, pausar el otro."},
        ],
        "keywords": [
            {"texto": "reglamento deforestacion union europea", "concordancia": "exacta", "grupo": "EUDR proceso", "accion": "cambiar de frase a exacta",
             "motivo": "41 clics y ARS 65.562 (57% del grupo), casi todo por búsquedas que no la contienen, como «eudr» suelta (ARS 35.656). En exacta solo entra quien busca el reglamento."},
        ],
        "negativas": [
            {"texto": "eudr", "concordancia": "exacta", "nivel": "grupo", "grupo": "EUDR proceso",
             "motivo": "La búsqueda suelta «eudr» costó ARS 35.656 (18 clics) en este grupo, que es de aprendizaje. Cerrada acá, puede tomarla «EUDR compra», cuyos anuncios ofrecen la verificación; si no la toma, deja de pagarse."},
            {"texto": "faq", "concordancia": "frase", "nivel": "campaña",
             "motivo": "«faq eudr» costó ARS 2.658 por un clic: busca preguntas frecuentes, no un proveedor."},
        ],
        "negativas_decision": "Las negativas de definición ya están en la campaña («que significa», «que es», «resumen», «definicion»): no hace falta "
                              "repetirlas. Solo dos nuevas.",
        "anuncios": [
            {
                "grupo": "EUDR proceso", "anuncio_id": str(debil), "accion": "Reescribir",
                "anuncio_desc": f"fuerza Pobre, 37 clics y ARS 56.202 del {VENTANA}",
                "motivo": "Sus dos recursos con más clics explican el reglamento («Qué exige EUDR», 37 clics; «Geolocalización, evaluación de riesgo y "
                          "declaración de due diligence: qué pide EUDR», 33) y dos títulos prometen una certificación que no existe. La propuesta mantiene el "
                          "tema (requisitos, debida diligencia, geolocalización, plazo) pero siempre como lo que Control Union verifica, para que el clic lo "
                          "haga el exportador que tiene que cumplir y no quien solo quiere entender.",
                "url": str(eu.loc[debil, "ad_group_ad.ad.final_urls"]).strip("[]'\" "), "gasto_ars": 56202, "clics": 37, "ventanas": VENTANA,
                "titulos_hoy": partes(debil, "ad_group_ad.ad.responsive_search_ad.headlines"),
                "descripciones_hoy": partes(debil, "ad_group_ad.ad.responsive_search_ad.descriptions"),
                "quitar": [
                    {"texto": "Qué exige EUDR", "motivo": "El título con más clics (37): promete explicar y atrae a quien quiere aprender."},
                    {"texto": "Certificación EUDR", "motivo": "EUDR no tiene certificación: promete un sello que no existe."},
                    {"texto": "EUDR: due diligence", "motivo": "1 clic en 44 impresiones: nombra la tarea, no el servicio."},
                    {"texto": "Evaluación de riesgo EUDR", "motivo": "Es lo que hace el operador; dicho así suena a consultoría."},
                    {"texto": "Geolocalización de lotes", "motivo": "2 impresiones: Google casi no lo usa."},
                    {"texto": "Geolocalización, evaluación de riesgo y declaración de due diligence: qué pide EUDR.", "motivo": "33 clics: enumera el reglamento para quien quiere entenderlo."},
                    {"texto": "Organismo de certificación con más de 100 años y presencia en 80+ países.", "motivo": "La descripción que menos rinde (4 clics); el respaldo ya está en los títulos."},
                ],
                "titulos_propuestos": [
                    P("Verificamos tu cadena EUDR", "Dice lo que hace Control Union, con su verbo, y deja afuera a quien solo quiere entender el reglamento.", True, "Qué exige EUDR"),
                    P("Verificación EUDR Argentina", "Es el título con intención de compra que mejor anda en el otro anuncio del grupo (11 clics) y nombra el país.", True, "Certificación EUDR"),
                    P("Debida diligencia verificada", "Traduce «due diligence», que es lo que el exportador tiene que presentar, y lo convierte en el servicio.", True, "EUDR: due diligence"),
                    P("Exportadores de soja y carne", "Nombra a quien compra: «eudr soja» es la keyword con más gasto de «EUDR compra».", False, "Evaluación de riesgo EUDR"),
                    P("Geolocalización verificada", "Mismo tema que hoy, pero como servicio verificado y no como tarea a explicar.", False, "Geolocalización de lotes"),
                ],
                "descripciones_propuestas": [
                    P("Verificamos la debida diligencia EUDR de tu cadena: origen, geolocalización, trazabilidad.",
                      "Enumera lo mismo que la descripción con más clics, pero como lo que verificamos.", True,
                      "Geolocalización, evaluación de riesgo y declaración de due diligence: qué pide EUDR."),
                    P("¿Exportás soja, carne o madera a la UE? Contanos qué exportás y te cotizamos.",
                      "Cierra con un pedido concreto que solo hace quien va a contratar.", False,
                      "Organismo de certificación con más de 100 años y presencia en 80+ países."),
                ],
                "terminos": [
                    {"termino": "eudr", "relacion": "parcial", "coste": 35656, "clics": 18},
                    {"termino": "eudr que significa", "relacion": "parcial", "coste": 8587, "clics": 2},
                    {"termino": "diligencia debida eudr", "relacion": "parcial", "coste": 3239, "clics": 1},
                    {"termino": "faq eudr", "relacion": "nula", "coste": 2658, "clics": 1},
                    {"termino": "norma eudr", "relacion": "parcial", "coste": 1811, "clics": 1},
                    {"termino": "eudr dds", "relacion": "parcial", "coste": 1208, "clics": 1},
                ],
                "nota": "Los términos son del grupo entero (los dos anuncios comparten keywords).",
            },
            {
                "grupo": "EUDR proceso", "anuncio_id": str(otro), "accion": "Corregir",
                "anuncio_desc": f"fuerza Promedio, 61 clics y ARS 58.111 del {VENTANA}",
                "motivo": "Es el anuncio que más clics trae y queda casi igual para comparar. Solo se sacan dos títulos que prometen algo que no existe "
                          "(EUDR no tiene certificación ni Control Union una acreditación para EUDR) y se cambia «Te explicamos…», que es tono de consultora.",
                "url": str(eu.loc[otro, "ad_group_ad.ad.final_urls"]).strip("[]'\" "), "gasto_ars": 58111, "clics": 61, "ventanas": VENTANA,
                "titulos_hoy": partes(otro, "ad_group_ad.ad.responsive_search_ad.headlines"),
                "descripciones_hoy": partes(otro, "ad_group_ad.ad.responsive_search_ad.descriptions"),
                "quitar": [
                    {"texto": "Organismo acreditado", "motivo": "No hay acreditación EUDR y la landing no menciona ninguna."},
                    {"texto": "Certificación de origen", "motivo": "No es una certificación: promete otro servicio."},
                    {"texto": "Te explicamos qué documentación y qué datos de origen exige el reglamento de la UE.", "motivo": "Control Union no asesora ni explica: verifica."},
                ],
                "titulos_propuestos": [
                    P("Verificamos tu cadena EUDR", "El verbo de Control Union en el anuncio que más se muestra.", True, "Certificación de origen"),
                    P("Organismo de certificación", "Es lo que Control Union es, sin atarlo a una acreditación EUDR que no existe.", False, "Organismo acreditado"),
                ],
                "descripciones_propuestas": [
                    P("Verificamos que tu documentación y tus datos de origen cumplan el reglamento de la UE.",
                      "Es la descripción con más clics del grupo (61): mantiene el tema y cambia «te explicamos» por «verificamos».", True,
                      "Te explicamos qué documentación y qué datos de origen exige el reglamento de la UE."),
                ],
            },
        ],
        "organico": R["CU:SEM:anuncio:cu-argentina-agroexportacion:eudr-proceso"]["evidencia"].get("organico"),
        "organico_desde": "Argentina", "organico_hasta": "14 sep 2026", "datos_hasta": FECHA_DATOS,
    },
}


# ─────────────────────────────── las 8 unificadas, completadas a mano (datos al 21 oct)
# Felipe (21 oct): cada propuesta con su motivo, las que conviene hacer marcadas, y un grupo nuevo siempre con keywords y
# decisión de negativas. unificar() arma la base; MANUAL la reemplaza campo por campo.
TERMINOS = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in glob.glob(os.path.join(API, "*", "ads_*_terminos_2026-09-01_2026-10-20.csv"))])


def terminos_de(campana, grupo, relacion, n=8):
    """Términos del período con más gasto en el grupo; `relacion` clasifica los que se conocen (fuerte / parcial / nula)."""
    t = TERMINOS[(TERMINOS["campaign.name"] == campana) & (TERMINOS["ad_group.name"] == grupo)]
    t = t.groupby("search_term_view.search_term").agg(clics=("metrics.clicks", "sum"), coste=("metrics.cost_micros", "sum")).reset_index()
    t = t[t["clics"] > 0].sort_values("coste", ascending=False).head(n)
    return [{k: v for k, v in dict(termino=x["search_term_view.search_term"], relacion=relacion.get(x["search_term_view.search_term"]),
                                   coste=round(x["coste"] / 1e6), clics=int(x["clics"])).items() if v is not None} for _, x in t.iterrows()]


def anuncio_vigente(campana, grupo, ad_id, **spec):
    """Bloque de un anuncio que ya existe: lo de hoy sale del snapshot y de los reportes; lo propuesto, de `spec`."""
    a = anuncios_del_grupo(campana, grupo)
    x = a[a["ad_group_ad.ad.id"] == ad_id].iloc[0]
    hoy_t = [s.strip() for s in str(x["ad_group_ad.ad.responsive_search_ad.headlines"]).split("|") if s.strip()]
    hoy_d = [s.strip() for s in str(x["ad_group_ad.ad.responsive_search_ad.descriptions"]).split("|") if s.strip()]
    gasto, clics = round(x["coste"] / 1e6), int(x["clics"])
    miles = f"{gasto:,.0f}".replace(",", ".")
    desc = f"fuerza {FUERZA.get(x['ad_group_ad.ad_strength'], x['ad_group_ad.ad_strength'])}, {clics} clics y ARS {miles} del {VENTANA}"
    if len(a) > 1:
        desc += f"; el grupo tiene {len(a)} anuncios activos"
    return {"grupo": grupo, "anuncio_id": str(ad_id), "anuncio_desc": desc, "url": str(x["ad_group_ad.ad.final_urls"]).strip("[]'\" "),
            "gasto_ars": gasto, "clics": clics, "ventanas": VENTANA, "titulos_hoy": hoy_t, "descripciones_hoy": hoy_d, **spec}


def Q(texto, motivo):
    return {"texto": texto, "motivo": motivo}


def K(texto, concordancia, grupo, accion, motivo):
    return {"texto": texto, "concordancia": concordancia, "grupo": grupo, "accion": accion, "motivo": motivo}


def N(texto, concordancia, motivo, grupo=None):
    return {k: v for k, v in dict(texto=texto, concordancia=concordancia, nivel="grupo" if grupo else "campaña", grupo=grupo, motivo=motivo).items() if v}


CAES = "CU España - CAEs - Search"
IFS = "CU España - IFS - SEARCH"
SMETA = "CU España - Smeta - Search"
PLAST = "CU Portugal - Plasticos - Search"
TEXT = "CU Portugal - Textile - Search"
NOP = "CU United States - Organic - USDA NOP - Search"
ESG = "PS Argentina - SuSe - ESG / Reportes - Search"
AGUA = "PS Argentina - SuSe - Huella de agua - Search"
CU_ES = "https://espana.controlunion.com/programa-de-certificacion/"

MANUAL = {
    # ── CAEs ──────────────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-espana-caes:certificados-y-sistema-cae": {
        "titulo": "CU España - CAEs: pausar «certificado de eficiencia energetica» (57% del gasto: es el certificado de viviendas) · negativas y anuncio para sujetos obligados",
        "detalle": "La keyword amplia «certificado de eficiencia energetica» se llevó ARS 63.789 de ARS 112.250 (57%) con nivel de calidad 3: es el "
                   "certificado energético de pisos y casas, otro producto, y trae particulares («certificado energético oviedo», «cuanto cuesta el "
                   "certificado energetico de un piso»). Pausarla, sumar negativas de particulares y gestores, y completar el anuncio de fuerza Pobre "
                   "con lo que compra un sujeto obligado: la verificación de actuaciones.",
        "evidencia": {
            "acciones": ["pausa", "negativas", "anuncio"],
            "resumen": "Dejar de pagar el certificado energético de viviendas y hablarle al sujeto obligado.",
            "por_que": f"{VENTANA}: 110 clics y ARS 112.250, sin conversiones. El 57% (ARS 63.789, 73 clics) entra por la amplia «certificado de "
                       "eficiencia energetica», nivel de calidad 3: el certificado de eficiencia energética es el que necesita un particular para "
                       "vender o alquilar su vivienda, no el Certificado de Ahorro Energético (CAE) que verifica Control Union. Sus términos lo "
                       "confirman: «certificado energético oviedo», «certificado energético mallorca», «obtener certificado energético gratis», «cuanto "
                       "cuesta el certificado energetico de un piso». Otra parte busca quien le gestione el CAE («gestión caes particulares», «gestion "
                       "de caes», «gestionar cae coche electrico», «repsol cae»): Control Union verifica, no gestiona.",
            "ya_hecho": "Ya están como negativas de campaña «vivienda», «casas» y «que es» (estructura al 21 oct), de lo que se propuso en septiembre. "
                        "Algunos términos del período con esas palabras pueden ser anteriores a que se cargaran.",
            "pasos": [
                {"accion": "pausa", "titulo": "Pausar la keyword «certificado de eficiencia energetica»", "donde": f"{CAES} › grupo «Certificados y Sistema CAE» · keyword amplia",
                 "detalle": "Cambia lo propuesto en septiembre (pasarla a frase): en frase seguiría trayendo «certificado de eficiencia energetica "
                            "vivienda». El grupo queda con sus 12 keywords de CAE."},
                {"accion": "negativas", "titulo": "Sumar 13 negativas de campaña", "donde": f"{CAES} › toda la campaña",
                 "detalle": "Particulares, gestores y descargas. Las negativas de campaña que ya existen no se tocan."},
                {"accion": "anuncio", "titulo": "Completar el anuncio de fuerza Pobre", "donde": f"{CAES} › grupo «Certificados y Sistema CAE» · anuncio id 817970230928",
                 "detalle": "Tiene 7 títulos y 2 descripciones: Google lo califica Pobre por falta de variantes. Se suman 6 títulos y 2 descripciones."},
            ],
            "keywords": [K("certificado de eficiencia energetica", "amplia", "Certificados y Sistema CAE", "pausar",
                           "73 clics y ARS 63.789 (57% de la campaña), nivel de calidad 3. Es el certificado de viviendas, otro producto.")],
            "negativas": [
                N("particular", "amplia", "«gestión caes particulares» (ARS 3.498 por un clic): el particular no es cliente de una verificadora."),
                N("particulares", "amplia", "Las negativas no cubren plurales: hace falta también en plural."),
                N("piso", "amplia", "«cuanto cuesta el certificado energetico de un piso»: certificado de vivienda."),
                N("gestion", "amplia", "«gestion de caes» (ARS 2.962): busca un gestor que tramite el CAE. Control Union verifica, no gestiona."),
                N("gestión", "amplia", "La misma palabra con tilde: Google la trata como otra negativa."),
                N("gestionar", "amplia", "«gestionar cae coche electrico» (ARS 2.419)."),
                N("repsol", "amplia", "«repsol cae»: Repsol compra CAE a particulares; buscan venderle sus ahorros."),
                N("coche electrico", "frase", "Ahorros de un particular por su coche: no es un sujeto obligado."),
                N("gratis", "amplia", "«obtener certificado energético gratis»: la campaña no la tenía."),
                N("ce3", "amplia", "«ce3 descargar» (ARS 2.889): es el programa para calcular el certificado de viviendas."),
                N("ce3x", "amplia", "La otra versión del mismo programa."),
                N("curso", "amplia", "«curso de caes» (2 clics, ARS 1.943): formación."),
                N("que son", "frase", "«que son los caes en energia»: definición; la campaña ya bloquea «que es»."),
            ],
            "negativas_decision": "Sí: 13 negativas nuevas de campaña. Las que ya existen (vivienda, casas, que es, y las de coordinación de "
                                  "actividades empresariales) están bien. Con la amplia pausada, las de ciudades («oviedo», «mallorca») ya no hacen falta.",
        },
        "anuncios": [anuncio_vigente(
            CAES, "Certificados y Sistema CAE", 817970230928, accion="Completar",
            motivo="Fuerza Pobre con 88 clics y ARS 78.394: tiene 7 títulos y 2 descripciones, y ninguno dice «verificación de actuaciones», «sujeto "
                   "obligado» ni «verificador», que es lo que compra la campaña y por lo que el sitio aparece en orgánico («verificacion cae», 239 "
                   "impresiones en posición 10). Sumar esas variantes sube la fuerza y la relevancia; la descripción que aclara que no gestionamos "
                   "CAE de particulares filtra el clic que hoy se paga sin cliente detrás.",
            quitar=[Q("Rigor Técnico en Cada Proyecto", "No dice qué ni para quién: es un título de relleno."),
                    Q("Convierta sus ahorros energéticos en valor certificado, con soporte técnico continuo.", "Le habla a quien quiere vender sus ahorros (el particular) y «soporte técnico continuo» es de consultora.")],
            titulos_propuestos=[
                P("Verificamos Actuaciones CAE", "Es lo que compra un sujeto obligado y lo que trae el orgánico («verificacion cae», 239 impresiones).", True, "Rigor Técnico en Cada Proyecto"),
                P("Sujetos Obligados y Delegados", "Nombra a quien compra y deja afuera al particular.", True),
                P("Verificamos, No Gestionamos", "Corta a quien busca un gestor («gestion de caes», «gestión caes particulares»).", True),
                P("Verificador CAE Acreditado", "Repite «verificador cae» (123 impresiones orgánicas). La acreditación ENAC ya figura en el anuncio actual."),
                P("Verificación CAE para Empresas", "Variante con el tipo de cliente."),
                P("Solicita Verificación CAE", "Llamado a la acción con el servicio, no «solicita información»."),
            ],
            descripciones_propuestas=[
                P("No gestionamos ni tramitamos CAE de particulares: verificamos actuaciones de empresas.",
                  "Filtra al particular antes del clic: hoy es la mayor parte del gasto sin cliente.", True,
                  "Convierta sus ahorros energéticos en valor certificado, con soporte técnico continuo."),
                P("Para sujetos obligados y delegados: verificación técnica de CAE con plazos claros.",
                  "Nombra a los dos clientes posibles del sistema CAE.", True),
                P("Cuéntanos tu actuación y te confirmamos alcance y plazos de la verificación.", "Cierre con un pedido concreto."),
            ],
            terminos=terminos_de(CAES, "Certificados y Sistema CAE", {
                "eficiencia energética": "nula", "cae": "fuerte", "certificado energético cantabria barato": "nula", "repsol cae": "nula",
                "curso de caes": "nula", "cae que es": "parcial", "obtener certificado energético gratis": "nula", "caes": "fuerte"}),
            nota="Los dos grupos de la campaña tienen el mismo texto; el de «Verificación y Actuaciones CAE» (id 817970230931) tiene fuerza Promedio. "
                 "Si el cambio rinde en 30 días, replicarlo ahí.",
        )],
    },
    # ── IFS ───────────────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-espana-ifs:food-safety": {
        "titulo": "CU España - IFS: la campaña no tiene ninguna keyword de IFS · crear los grupos «IFS Food» e «ISO 22000 y FSSC 22000» y ajustar «Food Safety»",
        "detalle": "La campaña se llama IFS, pero sus 9 keywords son genéricas («certificación seguridad alimentaria» se lleva el 62%). Las búsquedas de "
                   "IFS Food, ISO 22000 y FSSC 22000 caen en un anuncio que no las nombra y llevan a la página general de seguridad alimentaria, "
                   "aunque el sitio tiene página propia de cada norma. Crear dos grupos con sus keywords, anuncio y página; dejar «Food Safety» para "
                   "seguridad alimentaria y HACCP; y sumar negativas.",
        "evidencia": {
            "acciones": ["estructura", "keywords", "negativas", "anuncio"],
            "resumen": "Que quien busca IFS, ISO 22000 o FSSC 22000 vea un anuncio y una página de esa norma.",
            "por_que": f"{VENTANA}: 59 clics y ARS 115.441, sin conversiones. Un solo grupo, «Food Safety», con 9 keywords genéricas: «certificación "
                       "seguridad alimentaria» (frase) se lleva ARS 71.537 (62%). Por ahí entran «ifs food» (109 impresiones), «iso 22000» (98), «fssc "
                       "22000» (78), «certificado ifs» (30), «auditoria ifs» (20) y «certificacion ifs» (19), que ven un anuncio de «seguridad "
                       "alimentaria» y llegan a /industry/seguridad-alimentaria/. El sitio tiene página propia de cada norma, con demanda orgánica "
                       "(Search Console, histórico): IFS Food (892 impresiones; 3.583 la versión en inglés), ISO 22000 (1.572) y FSSC 22000 (795). "
                       "BRCGS no: 30 impresiones, va a negativo (ya decidido en el análisis de septiembre).",
            "ya_hecho": "Nada de lo propuesto en septiembre: la campaña sigue con las mismas 9 keywords y solo «curso» y «qué es» como negativas de "
                        "definición o formación.",
            "pasos": [
                {"accion": "estructura", "titulo": "Crear el grupo «IFS Food»", "donde": f"{IFS} › grupo nuevo «IFS Food»",
                 "detalle": f"Crear el grupo con URL final {CU_ES}ifs-food/ y cargarle las 5 keywords y el anuncio de este paso."},
                {"accion": "estructura", "titulo": "Crear el grupo «ISO 22000 y FSSC 22000»", "donde": f"{IFS} › grupo nuevo «ISO 22000 y FSSC 22000»",
                 "detalle": f"Crear el grupo con URL final {CU_ES}iso-22000-food-safety-management-system/ y cargarle las 5 keywords y el anuncio de este paso (FSSC 22000 "
                            "es ISO 22000 más requisitos adicionales: por ahora comparten grupo; ver paso 5)."},
                {"accion": "negativas", "titulo": "Cargar las negativas", "donde": f"{IFS} › toda la campaña (11) y grupo «Food Safety» (3)",
                 "detalle": "Las 3 del grupo «Food Safety» mandan las búsquedas de IFS, ISO 22000 y FSSC a sus grupos nuevos."},
                {"accion": "anuncio", "titulo": "Ajustar el anuncio de «Food Safety»", "donde": f"{IFS} › grupo «Food Safety» · anuncio id 817970220944",
                 "detalle": "Queda para seguridad alimentaria y HACCP: se sacan los títulos genéricos y la descripción con voseo."},
                {"accion": "revisar", "titulo": "En 30 días, mirar FSSC 22000", "donde": f"{IFS} › grupo «ISO 22000 y FSSC 22000»",
                 "detalle": f"Si «fssc 22000» supera unas 100 impresiones por mes, pasarla a un grupo propio con la página {CU_ES}fssc-22000-food-safety-system-certification/"},
            ],
            "keywords": [
                K("ifs food", "exacta", "IFS Food", "agregar", "109 impresiones y 2 clics (ARS 4.987) en el período, hoy en un anuncio genérico. En orgánico es la búsqueda de IFS más frecuente (1.263 impresiones)."),
                K("certificado ifs", "exacta", "IFS Food", "agregar", "30 impresiones; con «certificado ifs food», 2 clics y ARS 3.172."),
                K("certificacion ifs", "exacta", "IFS Food", "agregar", "19 impresiones sin clic: el anuncio actual no nombra IFS."),
                K("auditoria ifs", "exacta", "IFS Food", "agregar", "20 impresiones sin clic."),
                K("certificación ifs food", "frase", "IFS Food", "agregar", "Cubre las variantes («ifs food certificación», «certificado ifs food») sin abrir a todo lo que contenga «ifs»."),
                K("iso 22000", "exacta", "ISO 22000 y FSSC 22000", "agregar", "98 impresiones y 2 clics (ARS 3.553). Mezcla compra y lectura: las negativas de definición de la campaña filtran lo segundo."),
                K("certificacion iso 22000", "exacta", "ISO 22000 y FSSC 22000", "agregar", "La versión con intención de compra; todavía sin datos pagos. La página de ISO 22000 tiene 1.572 impresiones orgánicas."),
                K("auditoria iso 22000", "exacta", "ISO 22000 y FSSC 22000", "agregar", "Ídem, con «auditoría»."),
                K("fssc 22000", "exacta", "ISO 22000 y FSSC 22000", "agregar", "78 impresiones sin clic en el período: hoy cae en el anuncio genérico."),
                K("certificacion fssc 22000", "exacta", "ISO 22000 y FSSC 22000", "agregar", "La versión con intención de compra."),
            ],
            "negativas": [
                N("brcgs", "amplia", "«brcgs standard» (ARS 2.816) y «certificaciones brcgs» (ARS 2.403). BRCGS no tiene demanda ni contenido para pagarlo (30 impresiones orgánicas en el histórico)."),
                N("brc", "amplia", "«certificado brc que significa» (ARS 2.294)."),
                N("servsafe", "amplia", "«servsafe certification», «servsafe burger king»: es el curso de manipulación de alimentos de EE. UU."),
                N("food handler", "frase", "Carnet de manipulador en inglés: formación, no certificación."),
                N("manipulador", "amplia", "Carnet de manipulador de alimentos: formación."),
                N("food standards agency", "frase", "«food standards agency e learning»: la agencia británica."),
                N("que es", "frase", "«iso 22000 que es y para que sirve» (30 impresiones): la negativa actual es «qué es» con tilde y no lo cubre."),
                N("para que sirve", "frase", "Misma búsqueda de definición."),
                N("cuestionario", "amplia", "«cuestionario auditoria interna iso 22000» (ARS 1.861): material para estudiar."),
                N("test", "amplia", "«food safety test» (ARS 3.968): examen."),
                N("why", "amplia", "«why iso 22000 is important»: lectura, en inglés."),
                N("ifs", "amplia", "Para que las búsquedas de IFS vayan al grupo «IFS Food» y no a este.", grupo="Food Safety"),
                N("22000", "amplia", "Para que ISO 22000 y FSSC 22000 vayan a su grupo.", grupo="Food Safety"),
                N("fssc", "amplia", "Ídem, para «fssc» escrito sin el número.", grupo="Food Safety"),
            ],
            "negativas_decision": "Sí: 11 negativas de campaña (BRCGS, cursos de manipulación, definiciones) y 3 de grupo en «Food Safety» para que cada "
                                  "norma vaya a su grupo. Las que ya existen (gratis, curso, pdf, formación, qué es…) están bien.",
        },
        "anuncios": [
            {"grupo": "IFS Food", "accion": "Anuncio nuevo", "url": f"{CU_ES}ifs-food/",
             "motivo": "El grupo nuevo necesita su anuncio. Repite en los títulos lo que se busca («ifs food», «certificado ifs») y lleva a la página de IFS Food.",
             "titulos_propuestos": [
                 P("Certificación IFS Food", "Repite la búsqueda principal («ifs food», 109 impresiones).", True),
                 P("Certificado IFS Food", "«certificado ifs» y «certificado ifs food»: 40 impresiones.", True),
                 P("Auditores IFS en España", "Une la norma con el país y el equipo local.", True),
                 P("Certificamos IFS Food", "El verbo de Control Union."),
                 P("Auditoría IFS Food Versión 8", "IFS Food v8 es la versión vigente; confirmar con la unidad antes de publicarlo."),
                 P("Organismo Certificador", "Dice qué es Control Union."),
                 P("Control Union España", "Marca."),
                 P("Solicita Tu Auditoría IFS", "Llamado a la acción con el servicio."),
             ],
             "descripciones_propuestas": [
                 P("Certificamos IFS Food con equipo auditor local. Cuéntanos tu planta y coordinamos fechas.", "Norma, verbo de Control Union y un pedido concreto.", True),
                 P("IFS Food, norma reconocida por GFSI, para fabricantes y envasadores de alimentos.", "Dice para quién es y por qué la piden los clientes del fabricante.", True),
                 P("Más de 100 años certificando. Presencia en más de 80 países.", "Respaldo."),
             ]},
            {"grupo": "ISO 22000 y FSSC 22000", "accion": "Anuncio nuevo", "url": f"{CU_ES}iso-22000-food-safety-management-system/",
             "motivo": "El grupo nuevo necesita su anuncio, con las dos normas en los títulos.",
             "titulos_propuestos": [
                 P("Certificación ISO 22000", "Repite la búsqueda («iso 22000», 98 impresiones).", True),
                 P("Certificación FSSC 22000", "«fssc 22000», 78 impresiones sin clic hoy.", True),
                 P("Certificamos ISO 22000", "El verbo de Control Union."),
                 P("Auditoría ISO 22000", "Variante con «auditoría»."),
                 P("FSSC 22000 Reconocida GFSI", "El argumento por el que se elige FSSC sobre ISO 22000."),
                 P("Organismo Certificador", "Dice qué es Control Union."),
                 P("Control Union España", "Marca."),
                 P("Solicita Tu Auditoría", "Llamado a la acción."),
             ],
             "descripciones_propuestas": [
                 P("Certificamos ISO 22000 y FSSC 22000 con equipo auditor local en España.", "Las dos normas y el verbo de Control Union.", True),
                 P("FSSC 22000, reconocida por GFSI: certificamos tu sistema de seguridad alimentaria.", "Explica la diferencia con ISO 22000 en una línea.", True),
                 P("Más de 100 años certificando. Presencia en más de 80 países.", "Respaldo."),
             ]},
            anuncio_vigente(
                IFS, "Food Safety", 817970220944, accion="Ajustar",
                motivo="Con los grupos nuevos, este anuncio queda para «seguridad alimentaria» y HACCP. Hoy tiene tres títulos genéricos que no dicen qué "
                       "se certifica, uno con «gestión» (vocabulario de consultora) y una descripción con voseo («Pedí propuesta») en un anuncio para España.",
                quitar=[Q("Soporte técnico completo", "«Soporte» es de consultora; Control Union certifica."),
                        Q("Equipo técnico experto", "Genérico."),
                        Q("Auditorías para empresas", "Genérico."),
                        Q("Gestión Inocuidad Aliment.", "«Gestión» es de consultora y está abreviado."),
                        Q("Soporte para sistemas de inocuidad. Pedí propuesta y coordinamos auditoría.", "Voseo rioplatense en un anuncio para España, y «soporte» de consultora.")],
                titulos_propuestos=[
                    P("Certificación HACCP", "«haccp» es la búsqueda orgánica más grande del tema (575 impresiones, posición 13) y el grupo ya tiene la keyword.", True, "Gestión Inocuidad Aliment."),
                    P("Certificaciones Alimentarias", "Así lo busca la gente en orgánico (139 impresiones; «certificaciones de seguridad alimentaria», 256).", True, "Soporte técnico completo"),
                    P("Organismo Certificador", "Dice qué es Control Union.", False, "Equipo técnico experto"),
                    P("Auditoría HACCP", "Variante con «auditoría».", False, "Auditorías para empresas"),
                ],
                descripciones_propuestas=[
                    P("Certificamos seguridad alimentaria en España: IFS, ISO 22000, FSSC 22000 y HACCP.", "Nombra las normas con el verbo de Control Union y sin voseo.", True,
                      "Soporte para sistemas de inocuidad. Pedí propuesta y coordinamos auditoría."),
                ],
                terminos=terminos_de(IFS, "Food Safety", {
                    "ifs food": "parcial", "iso 22000": "nula", "certificado ifs food": "parcial", "norma iso 22000 2018": "nula", "brcgs standard": "nula",
                    "haccp certificado": "fuerte", "cuestionario auditoria interna iso 22000": "nula", "servsafe certification": "nula"}),
                nota="BRCGS no va en títulos: no hay demanda ni contenido (30 impresiones orgánicas en el histórico)."),
        ],
    },
    # ── SMETA ─────────────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-espana-smeta:social": {
        "titulo": "CU España - Smeta: pausar la amplia «smeta auditoria» (85% del gasto: trae competidores y normas ISO) · negativas y ajuste del anuncio",
        "detalle": "La keyword amplia «smeta auditoria» se llevó ARS 102.067 de ARS 120.022 (85%) y es la puerta de los competidores (Intertek, TÜV SÜD, "
                   "DNV, Veolia, OCA) y de búsquedas de ISO 9001/14001/45001. Pausarla y sumar [smeta auditoria] y [smeta] en exacta: las demás exactas "
                   "de SMETA ya están. Negativas de competidores e ISO, y sacar del anuncio el «prepara tu auditoría», que es de consultora.",
        "evidencia": {
            "acciones": ["pausa", "keywords", "negativas", "anuncio"],
            "resumen": "Pagar solo búsquedas de SMETA, no de competidores ni de ISO.",
            "por_que": f"{VENTANA}: 80 clics y ARS 120.022, sin conversiones. La amplia «smeta auditoria» (nivel de calidad 7) se llevó 67 clics y "
                       "ARS 102.067 (85%). Sus términos visibles: «intertek ibérica spain s l u» (ARS 4.493), «veolia» (ARS 4.223), «tüv sud» (ARS "
                       "3.272), «dnv», «oca global», «certificaciones bureau veritas», «aenor normas iso», y una serie de búsquedas de ISO («cuadro "
                       "comparativo normas iso 9001 iso 14001 y 45001», «norma iso 9001 ventajas y desventajas», «auditores iso»). También 7 clics "
                       "(ARS 6.518) en «control union»: la marca propia, que se gana en orgánico sin pagar.",
            "ya_hecho": "La campaña ya tiene las exactas y frases de SMETA (auditoría smeta, certificación smeta, smeta 2 y 4 pilares, auditoria sedex "
                        "smeta): con ellas alcanza para pausar la amplia.",
            "pasos": [
                {"accion": "pausa", "titulo": "Pausar la amplia «smeta auditoria»", "donde": f"{SMETA} › grupo «Social» · keyword amplia",
                 "detalle": "En su lugar van las dos exactas del paso 2."},
                {"accion": "keywords", "titulo": "Sumar [smeta auditoria] y [smeta]", "donde": f"{SMETA} › grupo «Social»"},
                {"accion": "negativas", "titulo": "Sumar 12 negativas de campaña", "donde": f"{SMETA} › toda la campaña",
                 "detalle": "Competidores y normas ISO. Con la amplia pausada son un seguro barato."},
                {"accion": "anuncio", "titulo": "Ajustar el anuncio", "donde": f"{SMETA} › grupo «Social» · anuncio id 817970221394"},
            ],
            "keywords": [
                K("smeta auditoria", "amplia", "Social", "pausar", "67 clics y ARS 102.067 (85% de la campaña); trae competidores y búsquedas de ISO."),
                K("smeta auditoria", "exacta", "Social", "agregar", "Reemplaza a la amplia: se paga solo esa búsqueda."),
                K("smeta", "exacta", "Social", "agregar", "123 impresiones y 4 clics (ARS 4.747) en el período; en orgánico el sitio está en posición 7,8 con 1.757 impresiones."),
            ],
            "negativas": [
                N("intertek", "amplia", "«intertek ibérica spain s l u»: ARS 4.493 por un clic. Competidor."),
                N("veolia", "amplia", "ARS 4.223, 2 clics."),
                N("tüv", "amplia", "«tüv sud»: ARS 3.272 por un clic."),
                N("tuv", "amplia", "La misma marca escrita sin diéresis."),
                N("dnv", "amplia", "ARS 2.575 por un clic. Competidor."),
                N("oca", "amplia", "«oca global»: competidor."),
                N("veritas", "amplia", "«certificaciones bureau veritas»: 2 clics. Competidor."),
                N("aenor", "amplia", "«aenor normas iso»: competidor."),
                N("isocert", "amplia", "«certificaciones iso calidad isocert»: competidor."),
                N("iso", "amplia", "Corta de una vez las búsquedas de ISO 9001, 14001 y 45001 que entraron por la amplia («cuadro comparativo…», «auditores iso», «normas iso 2019»). Nadie busca SMETA con «iso»."),
                N("ohsas", "amplia", "«normas iso ohsas»: 2 clics."),
                N("software", "amplia", "«sigea software»: un programa de gestión."),
            ],
            "negativas_decision": "Sí: 12 negativas de campaña. Con la amplia pausada casi no deberían hacer falta, pero cuestan nada y cubren las "
                                  "variantes que pueda traer la frase. No se negativiza «control union»: con la amplia pausada deja de pagarse sola.",
        },
        "anuncios": [anuncio_vigente(
            SMETA, "Social", 817970221394, accion="Ajustar",
            motivo="El anuncio está bien en general (el problema era la keyword). Dos textos dicen «prepara tu auditoría»: preparar es lo que hace una "
                   "consultora, no un organismo que audita. Y no dice «social» ni «4 pilares», que son las búsquedas con mejor nivel de calidad.",
            quitar=[Q("Prepara Tu Auditoría", "Preparar la auditoría es de consultora: Control Union audita."),
                    Q("Solicita Información", "Genérico."),
                    Q("Contacta con Control Union y prepara tu auditoría SMETA con soporte local.", "Mismo problema: «prepara» y «soporte».")],
            titulos_propuestos=[
                P("Auditoría SMETA 4 Pilares", "«smeta 4 pilares»: nivel de calidad 7 y 101 impresiones orgánicas en posición 7,6.", True, "Prepara Tu Auditoría"),
                P("Auditoría Social Sedex", "Nombra «social» y Sedex: «auditoria social smeta» tiene nivel de calidad 3 porque el anuncio no lo dice.", True),
                P("Solicita Tu Auditoría SMETA", "Llamado a la acción con el servicio.", False, "Solicita Información"),
                P("Auditores SMETA en España", "Equipo local."),
                P("Auditoría Ética y Laboral", "Lo que se audita, en palabras del cliente."),
            ],
            descripciones_propuestas=[
                P("Cuéntanos tu planta y tu cliente y coordinamos la auditoría SMETA en fecha.", "Mismo cierre sin «prepara»: pide lo que necesita el auditor.", True,
                  "Contacta con Control Union y prepara tu auditoría SMETA con soporte local."),
            ],
            terminos=terminos_de(SMETA, "Social", {
                "control union": "parcial", "smeta": "fuerte", "intertek ibérica spain s l u": "nula", "veolia": "nula", "tüv sud": "nula",
                "auditoria smeta": "fuerte", "dnv": "nula", "cuadro comparativo normas iso 9001 iso 14001 y 45001": "nula"}),
        )],
    },
    # ── Plásticos PT ──────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-portugal-plasticos:une-15343": {
        "titulo": "CU Portugal - Plásticos: pausar las dos amplias de UNE 15343 (97% del gasto del grupo, fuera de tema) · negativas y corregir los dos anuncios",
        "detalle": "En el grupo «UNE 15343», las amplias «une 15343» y «norma 15343» se llevaron ARS 64.310 de ARS 66.380 (97%) con búsquedas de economía "
                   "circular, PPWR, ODS y consultoras. Pausarlas (las exactas y frases de la norma ya están), sumar negativas, y corregir los dos "
                   "anuncios: textos de consultoría («apoia», «orientação») y un título en castellano en el anuncio de RecyClass.",
        "grupo": "UNE 15343",
        "evidencia": {
            "acciones": ["pausa", "keywords", "negativas", "anuncio"],
            "resumen": "Que el grupo de UNE 15343 pague solo búsquedas de la norma, y anuncios con el vocabulario de una certificadora.",
            "por_que": f"{VENTANA}: el grupo «UNE 15343» llevó 20 clics y ARS 66.380. «une 15343» (amplia) se llevó ARS 43.876 y «norma 15343» "
                       "(amplia) ARS 20.434: el 97%. De sus términos con clic, uno solo es de la norma («une en 15343», ARS 2.070); el resto son «ods "
                       "pt», «regulamento 2025 40», «bso consulting», «ppwr webinar», «epd», «como reduzir a produção de resíduos». En orgánico el sitio "
                       "está 3º para «en 15343». En «RecyClass» la exacta y la frase ya existen (20 clics, ARS 41.573) y el sitio también rankea 3º.",
            "ya_hecho": "«recyclass» ya está en exacta, como se propuso en septiembre. Faltaba el tope: queda como revisión (paso 5).",
            "pasos": [
                {"accion": "pausa", "titulo": "Pausar las amplias «une 15343» y «norma 15343»", "donde": f"{PLAST} › grupo «UNE 15343»",
                 "detalle": "El grupo queda con sus 12 exactas y frases de la norma."},
                {"accion": "keywords", "titulo": "Sumar la frase «en 15343»", "donde": f"{PLAST} › grupo «UNE 15343»"},
                {"accion": "negativas", "titulo": "Sumar 11 negativas de campaña", "donde": f"{PLAST} › toda la campaña"},
                {"accion": "anuncio", "titulo": "Corregir los dos anuncios", "donde": f"{PLAST} › «UNE 15343» (id 817970230922) y «RecyClass» (id 817970230925)"},
                {"accion": "revisar", "titulo": "En 30 días, decidir RecyClass", "donde": f"{PLAST} › grupo «RecyClass»",
                 "detalle": "El sitio está 3º en orgánico para «recyclass». Si en 30 días los clics pagos no traen contactos, pausar la frase "
                            "«recyclass» y dejar solo la exacta."},
            ],
            "keywords": [
                K("une 15343", "amplia", "UNE 15343", "pausar", "13 clics y ARS 43.876 (66% del grupo), casi todo fuera de tema."),
                K("norma 15343", "amplia", "UNE 15343", "pausar", "6 clics y ARS 20.434 (31%): «bso consulting», «ods pt», «como reduzir a produção de resíduos»."),
                K("en 15343", "frase", "UNE 15343", "agregar", "Así la cita la gente, con o sin año («une en 15343 2008», «une-en 15343:2008»). En orgánico, 45 impresiones en posición 3,2."),
            ],
            "negativas": [
                N("ppwr", "amplia", "«ppwr», «ppwr webinar», «ppwr regulation»: el reglamento europeo de envases, no la norma."),
                N("regulamento", "amplia", "«regulamento 2025 40» (ARS 4.487 por un clic): el mismo reglamento."),
                N("ods", "amplia", "«ods pt» (ARS 4.521), «ods»: Objetivos de Desarrollo Sostenible."),
                N("circular", "amplia", "«economia circular» (65 impresiones), «ecónomia circular», «empresas de economia circular»: una sola negativa cubre las tres."),
                N("resíduos", "amplia", "«gestão de resíduos», «como reduzir a produção de resíduos» (ARS 2.767)."),
                N("epd", "amplia", "Declaración ambiental de producto, otro servicio (ARS 3.141)."),
                N("consulting", "amplia", "«bso consulting»: una consultora (ARS 4.418)."),
                N("ecocert", "amplia", "Competidor."),
                N("14001", "amplia", "«iso 14001»: otra norma."),
                N("precious plastic", "frase", "Un proyecto de reciclaje casero."),
                N("audit tool", "frase", "«recyclass audit tool»: la herramienta en línea de RecyClass, no la certificación."),
            ],
            "negativas_decision": "Sí: 11 negativas de campaña. Las que ya existen (download, curso, pdf, emprego…) están bien.",
        },
        "anuncios": [
            anuncio_vigente(
                PLAST, "UNE 15343", 817970230922, accion="Ajustar",
                motivo="Dos descripciones usan vocabulario de consultoría: «A Control Union apoia…» y «receba orientação». Control Union certifica: no "
                       "apoya ni orienta. Y ningún título cita la norma con el año, que es como la escribe quien la necesita («une en 15343 2008»).",
                quitar=[Q("Cumprir EN 15343", "Habla del trabajo del cliente, no del servicio."),
                        Q("Peça Informação", "Genérico."),
                        Q("A Control Union apoia a certificação UNE-EN 15343 de ponta a ponta.", "«Apoia» es de consultora: Control Union certifica."),
                        Q("Peça informação e receba orientação para iniciar a certificação.", "«Orientação» es asesoramiento: conflicto de interés para una certificadora.")],
                titulos_propuestos=[
                    P("Certificação UNE-EN 15343:2008", "Cita la norma como la buscan, con el año.", True, "Cumprir EN 15343"),
                    P("Certificamos EN 15343", "El verbo de Control Union.", True),
                    P("Peça a Sua Certificação", "Llamado a la acción con el servicio, no «información».", False, "Peça Informação"),
                    P("Plástico Reciclado Certificado", "Lo que obtiene el cliente."),
                    P("Organismo de Certificação", "Dice qué es Control Union."),
                ],
                descripciones_propuestas=[
                    P("Certificamos UNE-EN 15343:2008: rastreabilidade e conteúdo reciclado em plásticos.", "Mismo tema que la descripción que se va, con el verbo correcto.", True,
                      "A Control Union apoia a certificação UNE-EN 15343 de ponta a ponta."),
                    P("Auditoria com equipa local em Portugal. Diga-nos o seu processo e confirmamos o âmbito.", "Cierre concreto sin «orientação».", True,
                      "Peça informação e receba orientação para iniciar a certificação."),
                ],
                terminos=terminos_de(PLAST, "UNE 15343", {
                    "ods pt": "nula", "regulamento 2025 40": "nula", "bso consulting": "nula", "ppwr webinar": "nula", "epd": "nula",
                    "como reduzir a produção de resíduos": "nula", "reciclagem polimeros": "parcial", "une en 15343": "fuerte"})),
            anuncio_vigente(
                PLAST, "RecyClass", 817970230925, accion="Corregir",
                motivo="Tiene un título en castellano en un anuncio en portugués («Equipo Auditor Local») y la misma descripción con «orientação».",
                quitar=[Q("Equipo Auditor Local", "Está en castellano: en portugués es «equipa»."),
                        Q("Peça informação e receba orientação para iniciar a certificação.", "«Orientação» es asesoramiento.")],
                titulos_propuestos=[P("Equipa Auditora Local", "El mismo título, en portugués.", True, "Equipo Auditor Local")],
                descripciones_propuestas=[
                    P("Auditoria RecyClass com equipa local. Diga-nos o seu processo e confirmamos o âmbito.", "Cierre concreto sin «orientação».", True,
                      "Peça informação e receba orientação para iniciar a certificação.")],
                terminos=terminos_de(PLAST, "RecyClass", {"recyclass": "fuerte", "recyclass certification": "fuerte", "recyclass audit tool": "nula", "recyclass certificate": "fuerte"})),
        ],
    },
    # ── Textile PT ────────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-portugal-textile:gots": {
        "titulo": "CU Portugal - Textile: cortar OEKO-TEX y el ruido de GRS · exactas de GOTS · anuncio de GOTS sin «apoio»",
        "detalle": "Campaña sana con dos fugas: la amplia «certificação gots portugal» trae OEKO-TEX (Control Union no lo certifica) y la amplia «global "
                   "recycled standard» trae PPWR y ODS. Pausar la primera, negativas para las dos, exactas para las búsquedas de GOTS que más compran, y "
                   "sacar del anuncio de GOTS el «Apoio a marcas», que es de consultora.",
        "evidencia": {
            "acciones": ["pausa", "keywords", "negativas", "anuncio"],
            "resumen": "Cortar OEKO-TEX y el ruido de GRS, y hablar como certificadora.",
            "por_que": f"{VENTANA}: 78 clics y ARS 117.016. «oeko tex» y «oeko tex standard 100» costaron ARS 8.762 (5 clics), casi todo por la "
                       "amplia «certificação gots portugal» (6 clics, ARS 9.446): Control Union no certifica OEKO-TEX (en el análisis de España, cero "
                       "apariciones en 20.561 búsquedas orgánicas). La amplia «global recycled standard» (ARS 16.494) trae «ppwr», «ods», «sdgs un», "
                       "«sustainable 17 goals». La búsqueda que más clics trajo, «gots certification» (6 clics, ARS 9.043), entra por otra keyword.",
            "ya_hecho": "«grs portugal» ya está en exacta, como se propuso en septiembre.",
            "pasos": [
                {"accion": "pausa", "titulo": "Pausar la amplia «certificação gots portugal»", "donde": f"{TEXT} › grupo «GOTS»",
                 "detalle": "Las frases y exactas de «certificação gots» cubren lo mismo sin OEKO-TEX."},
                {"accion": "keywords", "titulo": "Sumar 3 exactas de GOTS", "donde": f"{TEXT} › grupo «GOTS»"},
                {"accion": "negativas", "titulo": "Sumar 8 negativas de campaña", "donde": f"{TEXT} › toda la campaña",
                 "detalle": "La campaña no tiene ninguna negativa propia: las de descarga y empleo están repetidas en cada grupo."},
                {"accion": "anuncio", "titulo": "Ajustar el anuncio de GOTS", "donde": f"{TEXT} › grupo «GOTS» · anuncio id 817970230778"},
            ],
            "keywords": [
                K("certificação gots portugal", "amplia", "GOTS", "pausar", "6 clics y ARS 9.446, casi todos en búsquedas de OEKO-TEX."),
                K("gots certification", "exacta", "GOTS", "agregar", "La búsqueda con más clics del período (6, ARS 9.043), hoy por «global organic textile standard»."),
                K("gots", "exacta", "GOTS", "agregar", "156 impresiones y 4 clics (ARS 3.433). En orgánico el sitio está en posición 5,8 con 1.310 impresiones: el pago suma."),
                K("certificado gots", "exacta", "GOTS", "agregar", "3 clics en el período y 85 impresiones orgánicas en posición 4,5."),
            ],
            "negativas": [
                N("oeko", "amplia", "«oeko tex», «oeko tex standard 100»: ARS 8.762. Control Union no certifica OEKO-TEX."),
                N("oekotex", "amplia", "La misma marca escrita junta."),
                N("ppwr", "amplia", "Reglamento europeo de envases (ARS 2.951)."),
                N("ods", "amplia", "Objetivos de Desarrollo Sostenible (ARS 2.908)."),
                N("sdgs", "amplia", "Lo mismo en inglés («sdgs un», ARS 1.478)."),
                N("goals", "amplia", "«sustainable 17 goals» (ARS 1.298)."),
                N("resíduos", "amplia", "«gestão de resíduos industriais» (ARS 1.217)."),
                N("database", "amplia", "«gots database»: busca un certificado ajeno en la base de GOTS."),
            ],
            "negativas_decision": "Sí: 8 negativas de campaña. Corrige la tarjeta de septiembre en un punto: «wordly» no va a negativo todavía. Higg "
                                  "pasó a llamarse Worldly (a confirmar), así que «wordly fem» (1 clic, ARS 2.929) puede ser la misma búsqueda "
                                  "que «higg fem». Si en 30 días no trae contactos, negativizar.",
        },
        "anuncios": [anuncio_vigente(
            TEXT, "GOTS", 817970230778, accion="Ajustar",
            motivo="«Apoio a marcas, fabricantes e fornecedores» es vocabulario de consultora; Control Union certifica. Y no dice «norma» ni «certificamos», "
                   "que es como busca quien compra («norma gots», «certificado gots»). Tiene 7 títulos: hay lugar para sumar.",
            quitar=[Q("Peça Informação", "Genérico."),
                    Q("Apoio a marcas, fabricantes e fornecedores têxteis em Portugal.", "«Apoio» es de consultora.")],
            titulos_propuestos=[
                P("Norma GOTS: Certificamos", "«norma gots» (2 clics) con el verbo de Control Union.", True),
                P("Peça a Sua Certificação GOTS", "Llamado a la acción con el servicio, no «informação».", True, "Peça Informação"),
                P("Certificado GOTS", "«certificado gots»: 3 clics en el período.", True),
                P("Organismo de Certificação", "Dice qué es Control Union."),
                P("Símbolo GOTS Para a Sua Marca", "«gots symbol»: quien quiere usar el sello en su producto."),
                P("Certificação GOTS 8.0", "«gots 8.0» tuvo 15 impresiones. Confirmar con la unidad que ya audita sobre esa versión antes de publicarlo."),
            ],
            descripciones_propuestas=[
                P("Certificamos GOTS: têxteis orgânicos com rastreabilidade da fibra ao produto final.", "Dice qué certifica y con qué alcance.", True,
                  "Apoio a marcas, fabricantes e fornecedores têxteis em Portugal."),
            ],
            terminos=terminos_de(TEXT, "GOTS", {
                "gots certification": "fuerte", "oeko tex": "nula", "global organic textile standard": "fuerte", "gots": "fuerte",
                "certificado gots": "fuerte", "certificação gots": "fuerte", "gots symbol": "parcial", "norma gots": "fuerte", "gots database": "nula"}),
        )],
    },
    # ── USDA NOP ──────────────────────────────────────────────────────────────────────────────────────────────────
    "CU:SEM:anuncio:cu-united-states-organic-usda-nop:switch-get-certified": {
        "titulo": "CU USA - Organic USDA NOP: negativas de definición y competidores (41% de los términos visibles) · que el anuncio diga «Control Union»",
        "detalle": "Es la campaña más cara (ARS 552.452 en el período, cero conversiones). De los términos visibles, el 41% son definiciones («what does "
                   "certified organic mean»), competidores (QCS, OneCert, QAI), quien quiere ser certificador y la base de datos del USDA. Negativas de "
                   "campaña y un anuncio que use «Control Union», que es lo que la gente busca, en lugar de «CUC USA».",
        "evidencia": {
            "acciones": ["negativas", "anuncio", "revisar"],
            "resumen": "Dejar de pagar definiciones y competidores en la campaña más cara.",
            "por_que": f"{VENTANA}: ARS 552.452 y 63 clics (ARS 8.769 por clic), sin conversiones. De ARS 265.887 en términos visibles, ARS 109.862 "
                       "(41%) son: definiciones («what does certified organic mean» ARS 18.726, «what is certified organic» ARS 8.733), competidores "
                       "(«qcs organic» ARS 17.523, «one cert organic» ARS 14.832, «qai certified organic» ARS 6.715), quien quiere ser certificador («how "
                       "to become an organic certifier» ARS 11.087), la formación del USDA («organic integrity learning center» ARS 15.818) y una "
                       "empresa («mister specialties llc» ARS 16.429). La keyword exacta «organic certification» (nivel de calidad 3) se lleva ARS "
                       "136.588, el 25% de la campaña.",
            "ya_hecho": "Ninguna de las negativas propuestas en septiembre está cargada.",
            "pasos": [
                {"accion": "negativas", "titulo": "Sumar 11 negativas de campaña", "donde": f"{NOP} › toda la campaña",
                 "detalle": "Las 54 que ya tiene (portal, cosmetics, jobs, gots…) están bien."},
                {"accion": "anuncio", "titulo": "Cambiar 4 títulos y 1 descripción", "donde": f"{NOP} › grupo «Switch & Get Certified» · anuncio id 821810301980",
                 "detalle": "El anuncio ya tiene los 15 títulos que permite Google: cada título nuevo reemplaza a uno."},
                {"accion": "revisar", "titulo": "Decidir «organic chicken certification» con la unidad", "donde": f"{NOP} › grupo «Switch & Get Certified»",
                 "detalle": "Costó ARS 11.056 en septiembre. Si el alcance de CU USA incluye ganadería (livestock), queda; si no, va a negativo."},
                {"accion": "revisar", "titulo": "Poner un tope de CPC", "donde": f"{NOP} › configuración de la campaña › estrategia «Maximizar clics»",
                 "detalle": "El clic sale ARS 8.769 en promedio, pero hubo clics sueltos de ARS 14.800 a 17.500 en competidores y búsquedas ajenas («qcs organic», «mister specialties llc», «organic integrity learning center»). Un límite de CPC máximo los evita."},
            ],
            "keywords": [],
            "negativas": [
                N("what does", "frase", "«what does certified organic mean»: ARS 18.726 por 2 clics."),
                N("what is", "frase", "«what is certified organic»: ARS 8.733 por un clic."),
                N("meaning", "amplia", "Definiciones."),
                N("mean", "amplia", "Definiciones."),
                N("become an organic certifier", "frase", "«how to become an organic certifier» (ARS 11.087): quiere trabajar de certificador."),
                N("qcs", "amplia", "«qcs organic» (ARS 17.523): Quality Certification Services, competidor."),
                N("one cert", "frase", "«one cert organic» (ARS 14.832): competidor."),
                N("onecert", "amplia", "El mismo competidor escrito junto."),
                N("qai", "amplia", "«qai certified organic» (ARS 6.715): competidor."),
                N("learning center", "frase", "«organic integrity learning center» (ARS 15.818): la capacitación del USDA."),
                N("mister specialties", "frase", "«mister specialties llc» (ARS 16.429): una empresa puntual."),
            ],
            "negativas_decision": "Sí: 11 negativas de campaña. «how to get certified organic» no va a negativo: es un productor que quiere "
                                  "certificarse, el cliente. «organic chicken» queda a decidir con la unidad (paso 3).",
        },
        "anuncios": [anuncio_vigente(
            NOP, "Switch & Get Certified", 821810301980, accion="Ajustar",
            motivo="La gente busca «control union organic certification» (3 clics) y «certified organic by control union», pero el anuncio dice «CUC "
                   "USA», que nadie busca. Además tiene títulos sin contenido («Named Contact, Every Time», «Organic Cert, Simplified») y una "
                   "descripción con un error («USDA NOP Approved-organic»). Ya tiene 15 títulos, el máximo: cada uno nuevo reemplaza a uno.",
            quitar=[Q("Named Contact, Every Time", "Promesa vaga, sin norma ni servicio."),
                    Q("CUC USA: 80+ Countries", "«CUC» no lo busca nadie, y repite «Global Organic Certifier»."),
                    Q("Organic Cert by CUC USA", "Repite «CUC USA Organic Certification»."),
                    Q("Organic Cert, Simplified", "Genérico."),
                    Q("CUC USA: USDA NOP Approved-organic certification for U.S. businesses.", "«Approved-organic» está mal escrito y «CUC USA» no es el nombre que se busca.")],
            titulos_propuestos=[
                P("Control Union USA", "Es la marca que la gente escribe («control union organic certification», ARS 15.281).", True, "Organic Cert by CUC USA"),
                P("How to Get Certified Organic", "Repite tres búsquedas de productores que quieren certificarse (unos ARS 25.000 en el período).", True, "Organic Cert, Simplified"),
                P("NOP-Accredited Certifier", "Nombra el programa (NOP), que también se busca («nop certificate»).", False, "CUC USA: 80+ Countries"),
                P("Organic Certification: Farms", "Nombra el alcance. Confirmar con la unidad.", False, "Named Contact, Every Time"),
            ],
            descripciones_propuestas=[
                P("USDA NOP-accredited organic certifier for farms, handlers and processors in the U.S.",
                  "Corrige el error y nombra para quién es. Confirmar el alcance con la unidad.", True,
                  "CUC USA: USDA NOP Approved-organic certification for U.S. businesses."),
            ],
            terminos=terminos_de(NOP, "Switch & Get Certified", {
                "organic certification": "fuerte", "what does certified organic mean": "nula", "control union organic certification": "fuerte",
                "certified organic": "parcial", "third party organic certifiers": "fuerte", "how to become an organic certifier": "nula",
                "organic certifications": "fuerte", "how to get organic certified": "fuerte"}),
            nota="El alcance (farms, handlers, processors) es un supuesto: la campaña tiene un grupo de handlers y procesadores, pero confirmarlo con CU USA antes de publicar.",
        )],
    },
    # ── PS ESG ────────────────────────────────────────────────────────────────────────────────────────────────────
    "PS:SEM:anuncio:ps-argentina-suse-esg-reportes:reportes-esg": {
        "titulo": "PS Argentina - ESG: negativas para «gri + número» · títulos para CSRD y estándares GRI",
        "detalle": "La campaña más sana de Peterson. La frase «reporte GRI» (65% del gasto) trae 70 variantes de «gri + número» (quien lee un "
                   "indicador puntual): 8 clics y ARS 9.379. Negativas para los números con clic y «ejemplos»; en el anuncio, títulos para CSRD y "
                   "estándares GRI, que son las búsquedas que más se repiten.",
        "evidencia": {
            "acciones": ["negativas", "anuncio"],
            "resumen": "Dejar de pagar lectores de indicadores GRI y hablarle a quien tiene que reportar.",
            "por_que": f"{VENTANA}: 74 clics y ARS 113.464. «reporte GRI» (frase, nivel de calidad 3) se lleva ARS 74.136 (65%). Por ahí entraron 70 "
                       "variantes de «gri + número» («gri 404 1», «gri 204», «gri 201»…): 8 clics y ARS 9.379. Quien busca un indicador puntual "
                       "está leyendo la norma, no buscando quién le haga el reporte. Lo que sí se repite y el anuncio no nombra: «csrd» (76 "
                       "impresiones, 2 clics), «estándares gri» (31), «indicadores gri» (15, 2 clics).",
            "ya_hecho": "«que es», «definicion», «ejemplo» y «plantilla» ya son negativas de campaña.",
            "pasos": [
                {"accion": "negativas", "titulo": "Sumar 8 negativas de campaña", "donde": f"{ESG} › toda la campaña"},
                {"accion": "anuncio", "titulo": "Cambiar 3 títulos y 2 descripciones", "donde": f"{ESG} › grupo «Reportes ESG» · anuncio id 817970221367",
                 "detalle": "Tiene 14 títulos de 15 y las 4 descripciones: cada propuesta reemplaza a una."},
            ],
            "keywords": [],
            "negativas": [
                N("201", "amplia", "«gri 201»: indicador puntual (ARS 1.554)."),
                N("204", "amplia", "«gri 204» (ARS 2.036)."),
                N("404", "amplia", "«gri 404 1» (ARS 2.171), «gri 404» (ARS 448)."),
                N("402", "amplia", "«gri 402» (ARS 881)."),
                N("403", "amplia", "«gri 403» (ARS 671)."),
                N("300", "amplia", "«gri 300» (ARS 334)."),
                N("13", "amplia", "«gri 13» (ARS 1.283)."),
                N("ejemplos", "amplia", "«matriz de materialidad ejemplos» (ARS 2.525): la negativa actual es «ejemplo», en singular, y no cubre el plural."),
            ],
            "negativas_decision": "Sí: 8 negativas, solo los números que tuvieron clic. No se pueden negativizar los 70 de una vez (Google no acepta "
                                  "patrones); los demás tuvieron impresiones sin clic. Revisar el mes que viene. No se suman exactas de «csrd» ni "
                                  "«estándares gri» sueltas: ya entran por «reporte CSRD» y «reporte GRI», y solas son mayormente lectura.",
        },
        "anuncios": [anuncio_vigente(
            ESG, "Reportes ESG", 817970221367, accion="Ajustar",
            motivo="Es el anuncio que mejor anda (fuerza Buena, 67 clics). No nombra «estándares GRI», «indicadores» ni «doble materialidad», que es como "
                   "busca quien tiene que reportar. Dos descripciones están en «usted» genérico («Defina…», «Ordene…»): la voz de Peterson es "
                   "«nosotros» y el protagonista es el cliente.",
            quitar=[Q("Datos ESG", "Genérico."),
                    Q("Impacto ESG", "Genérico."),
                    Q("Plan ESG Empresa", "Genérico y mal escrito."),
                    Q("Defina estrategia ESG, reportes y materialidad con soporte experto.", "El cliente hace todo y nosotros solo damos «soporte»: no es la voz de Peterson."),
                    Q("Ordene datos, indicadores y prioridades para sostenibilidad corporativa.", "Genérico.")],
            titulos_propuestos=[
                P("CSRD y Doble Materialidad", "«csrd» es la búsqueda con más impresiones (76) y el anuncio no la nombra.", True, "Datos ESG"),
                P("Reportes con Estándares GRI", "«estándares gri» (31 impresiones) y «reportes gri»: dicho como servicio.", True, "Impacto ESG"),
                P("Indicadores GRI: Te Guiamos", "«indicadores gri»: 2 clics. Peterson acompaña.", False, "Plan ESG Empresa"),
            ],
            descripciones_propuestas=[
                P("Co-desarrollamos tu reporte de sostenibilidad: estándares GRI, indicadores y materialidad.",
                  "Voz de Peterson («co-desarrollamos») y las tres cosas que se buscan.", True,
                  "Defina estrategia ESG, reportes y materialidad con soporte experto."),
                P("Doble materialidad y CSRD con una hoja de ruta clara. Te acompañamos en todo el proceso.",
                  "Nombra CSRD, la búsqueda más frecuente, en el texto largo.", True,
                  "Ordene datos, indicadores y prioridades para sostenibilidad corporativa."),
            ],
            terminos=terminos_de(ESG, "Reportes ESG", {
                "csrd": "fuerte", "indicadores gri": "parcial", "standard gri": "fuerte", "estandar gri": "fuerte", "gri sustentabilidad": "fuerte",
                "estándares gri en español": "parcial", "gri l": "nula", "informes gri": "fuerte"}),
            nota="El grupo «Materialidad» (anuncio id 817970221361) tiene el mismo texto: «Matriz de Materialidad» iría mejor ahí.",
        )],
    },
    # ── PS Huella de agua ─────────────────────────────────────────────────────────────────────────────────────────
    "PS:SEM:anuncio:ps-argentina-suse-huella-de-agua:gestion-agua": {
        "titulo": "PS Argentina - Huella de agua: pausar «gestion del agua industrial» (97% del gasto, todo tratamiento de efluentes) · anuncio sin textos internos",
        "detalle": "La frase «gestion del agua industrial» se llevó ARS 95.754 de ARS 99.102 (97%) en búsquedas de tratamiento de efluentes, un servicio "
                   "que Peterson no da. Pausarla y sumar negativas. Además, los anuncios de la campaña publican dos notas internas como descripciones "
                   "(«Testee demanda en sectores…», «…definir alcance y viabilidad del servicio»): cambiarlas ya.",
        "grupo": "Huella hidrica",
        "evidencia": {
            "acciones": ["pausa", "negativas", "anuncio"],
            "resumen": "Dejar de pagar tratamiento de efluentes y sacar las notas internas de los anuncios.",
            "por_que": f"{VENTANA}: 37 clics y ARS 99.102, sin conversiones. «gestion del agua industrial» (frase) se llevó 32 clics y ARS 95.754 "
                       "(97%), todos en tratamiento de agua y efluentes: «tratamiento de efluentes industriales argentina», «tratamiento de aguas "
                       "industriales», «planta de tratamiento de efluentes industriales». El grupo «Huella hidrica», que es el servicio, gastó ARS "
                       "3.348; ahí entran calculadoras («calculadora huella hidrica», «fundacion aquae calculadora huella hidrica»).",
            "ya_hecho": "Nada de lo propuesto en septiembre: la keyword sigue activa y la campaña no tiene negativas propias.",
            "pasos": [
                {"accion": "pausa", "titulo": "Pausar la keyword «gestion del agua industrial»", "donde": f"{AGUA} › grupo «Gestion agua» · keyword en frase",
                 "detalle": "El grupo queda con 5 keywords de eficiencia y medición, que no tuvieron clics."},
                {"accion": "negativas", "titulo": "Sumar 5 negativas de campaña", "donde": f"{AGUA} › toda la campaña"},
                {"accion": "anuncio", "titulo": "Cambiar 4 títulos y las 2 descripciones internas", "donde": f"{AGUA} › grupo «Huella hidrica» · anuncio id 817970221139",
                 "detalle": "Hacer lo mismo con las dos descripciones en los anuncios de «Gestion agua» (id 817970221142) y «Riesgo hidrico» (id 817970221145), que tienen el mismo texto."},
            ],
            "keywords": [K("gestion del agua industrial", "frase", "Gestion agua", "pausar", "32 clics y ARS 95.754 (97% de la campaña), todos en tratamiento de efluentes.")],
            "negativas": [
                N("tratamiento", "amplia", "«tratamiento de efluentes industriales argentina» (ARS 4.006), «tratamiento de aguas industriales» (ARS 3.096)."),
                N("efluentes", "amplia", "El mismo servicio, dicho de otra forma."),
                N("residuales", "amplia", "«tratamiento de aguas residuales en la industria papelera»."),
                N("planta", "amplia", "«planta de tratamiento de efluentes industriales»."),
                N("calculadora", "amplia", "«calculadora huella hidrica» y variantes: 6 clics. Buscan una herramienta gratis; la negativa actual es «calculadora gratis»."),
            ],
            "negativas_decision": "Sí: 5 negativas de campaña. Las de grupo que ya existen (curso, pdf, que es, definicion…) quedan.",
        },
        "anuncios": [anuncio_vigente(
            AGUA, "Huella hidrica", 817970221139, accion="Ajustar",
            motivo="Dos descripciones son notas de planificación publicadas por error: «Testee demanda en sectores con alto consumo de agua y presion ESG» "
                   "y «Hable con Peterson para definir alcance y viabilidad del servicio». Y cuatro títulos («Gestion Del Agua», «Agua En Industria»…) le "
                   "dicen a Google que el anuncio es de tratamiento de agua, que es justo lo que trae las búsquedas equivocadas.",
            quitar=[Q("Gestion Del Agua", "Atrae tratamiento de agua."),
                    Q("Agua En Industria", "Ídem."),
                    Q("Consumo De Agua", "Ídem."),
                    Q("Agua Agroindustrial", "Ídem."),
                    Q("Testee demanda en sectores con alto consumo de agua y presion ESG.", "Es una nota interna de planificación, no un texto para el cliente."),
                    Q("Hable con Peterson para definir alcance y viabilidad del servicio.", "«Viabilidad del servicio» es interno: le dice al cliente que el servicio está en prueba.")],
            titulos_propuestos=[
                P("Huella Hídrica Corporativa", "Lo que Peterson mide, con la palabra que la diferencia del tratamiento de agua.", True, "Gestion Del Agua"),
                P("Medimos Tu Huella Hídrica", "Voz de Peterson y protagonista el cliente.", True, "Agua En Industria"),
                P("Riesgo Hídrico en Tu Cadena", "El otro servicio de la campaña.", False, "Consumo De Agua"),
                P("Huella de Agua ISO 14046", "Nombra la norma de huella hídrica. Confirmar que el servicio la usa antes de publicarlo.", False, "Agua Agroindustrial"),
            ],
            descripciones_propuestas=[
                P("Te acompañamos a medir la huella hídrica de tu empresa y de tu producto.", "Reemplaza la nota interna con lo que hace Peterson.", True,
                  "Testee demanda en sectores con alto consumo de agua y presion ESG."),
                P("Hablemos de tu consumo de agua: te decimos por dónde empezar a medir.", "Cierre con un pedido concreto, sin hablar de «viabilidad».", True,
                  "Hable con Peterson para definir alcance y viabilidad del servicio."),
            ],
            terminos=terminos_de(AGUA, "Gestion agua", {
                "tratamiento de efluentes industriales argentina": "nula", "tratamiento de aguas industriales": "nula", "tratamiento de efluentes industriales": "nula",
                "tratamiento de aguas residuales en la industria papelera": "nula", "tratamiento de aguas industriales miguel rigola lapeña": "nula"}),
            nota="Los términos son del grupo «Gestion agua», que es donde está el gasto; el anuncio que se cambia es el de «Huella hidrica», que es el que sigue.",
        )],
    },
}


# ─────────────────────────────── qué cargar, paso por paso (Felipe, 28 oct: «comentá concretamente qué hacer»)
# Cada paso lleva `items`: la lista exacta de negativas, keywords, recursos de anuncio o grupos, con su destino.
def _destino_neg(n):
    return f"Grupo «{n['grupo']}»" if n.get("nivel") == "grupo" else "Toda la campaña"


def _items_anuncio(a):
    """Recursos de un anuncio: reemplazos (quitar → poner), quitas sueltas y agregados."""
    dest = f"Anuncio id {a['anuncio_id']} · grupo «{a['grupo']}»" if a.get("anuncio_id") else f"Anuncio nuevo · grupo «{a['grupo']}»"
    tipo_de = {t: "titulo" for t in a.get("titulos_hoy") or []} | {d: "descripcion" for d in a.get("descripciones_hoy") or []}
    props = [(p, "titulo") for p in a.get("titulos_propuestos") or []] + [(p, "descripcion") for p in a.get("descripciones_propuestas") or []]
    props = [(P(p) if isinstance(p, str) else p, tp) for p, tp in props]
    reemplazados = {p.get("reemplaza") for p, _ in props}
    out = []
    for q in a.get("quitar") or []:
        q = q if isinstance(q, dict) else {"texto": q}
        if q["texto"] not in reemplazados:
            out.append({"accion": "quitar", "tipo": tipo_de.get(q["texto"], "titulo"), "texto": q["texto"], "destino": dest, "motivo": q.get("motivo")})
    for p, tp in props:
        it = {"accion": "reemplazar" if p.get("reemplaza") else "agregar", "tipo": tp, "texto": p["texto"], "destino": dest,
              "reemplaza": p.get("reemplaza"), "prioritario": p.get("prioritario"), "opcional": None if p.get("prioritario") else True, "motivo": p.get("motivo")}
        out.append(it)
    # primero lo que hay que hacer sí o sí
    out.sort(key=lambda i: (i["accion"] == "agregar" and bool(i.get("opcional")), not i.get("prioritario") and i["accion"] != "quitar"))
    return [{k: v for k, v in i.items() if v not in (None, False)} for i in out]


def con_items(ev, extras):
    """Agrega a cada paso la lista concreta de qué cargar. `extras` = {índice de paso: [items]} para lo que no sale solo."""
    kws, negs, ads = ev.get("keywords") or [], ev.get("negativas") or [], ev.get("anuncios") or []
    grupos_nuevos = [re.search(r"«(.+?)»", p["titulo"]).group(1) for p in ev["pasos"] if p["accion"] == "estructura" and "«" in p["titulo"]]
    kw = lambda k, accion, **x: {"accion": accion, "tipo": "keyword", "texto": k["texto"], "concordancia": k["concordancia"],
                                 "destino": f"Grupo «{k['grupo']}»" if k.get("grupo") else "Toda la campaña", "motivo": k.get("motivo"), **x}
    pasos = []
    for i, p in enumerate(ev["pasos"]):
        p, items = dict(p), []
        if p["accion"] == "negativas":
            items = [{"accion": "agregar", "tipo": "negativa", "texto": n["texto"], "concordancia": n["concordancia"], "destino": _destino_neg(n), "motivo": n.get("motivo")} for n in negs]
        elif p["accion"] == "keywords":
            for k in kws:
                if k.get("grupo") in grupos_nuevos:
                    continue
                m = re.match(r"cambiar de (\w+) a (\w+)", k["accion"])
                if m:  # Google Ads no cambia la concordancia de una keyword: se agrega la nueva y se pausa la vieja
                    items += [kw(dict(k, concordancia=m.group(2)), "agregar"),
                              kw(dict(k, concordancia=m.group(1), motivo="Se pausa la versión vieja: Google Ads no deja cambiar la concordancia de una keyword existente."), "pausar")]
                elif k["accion"] == "agregar":
                    items.append(kw(k, "agregar"))
        elif p["accion"] == "pausa":
            items = [kw(k, "pausar") for k in kws if k["accion"] == "pausar"]
        elif p["accion"] == "revisar":
            items = [kw(k, "decidir" if "decidir" in k["accion"] else "agregar", **({} if "decidir" in k["accion"] else {"opcional": True}))
                     for k in kws if "decidir" in k["accion"] or "si se confirma" in k["accion"]]
        elif p["accion"] == "estructura":
            g = re.search(r"«(.+?)»", p["titulo"]).group(1)
            a = next((a for a in ads if a["grupo"] == g), None)
            items = [{"accion": "crear", "tipo": "grupo", "texto": g, "destino": "La campaña", "motivo": f"URL final: {a['url']}" if a else None}]
            items += [kw(k, "agregar") for k in kws if k.get("grupo") == g]
            items += _items_anuncio(a) if a else []
        elif p["accion"] == "anuncio":
            ids = re.findall(r"id (\d+)", p.get("donde") or "")
            items = [x for a in ads if a.get("anuncio_id") in ids for x in _items_anuncio(a)]
        items += extras.get(i, [])
        if items:
            p["items"] = [{k: v for k, v in it.items() if v is not None} for it in items]
        pasos.append(p)
    return pasos


EXTRAS = {
    "CU:SEM:anuncio:cu-united-states-organic-usda-nop:switch-get-certified": {
        2: [{"accion": "decidir", "tipo": "texto", "texto": "¿CU USA certifica ganadería orgánica (livestock)?", "destino": "Consulta a CU USA"},
            {"accion": "agregar", "tipo": "negativa", "texto": "organic chicken", "concordancia": "frase", "destino": "Toda la campaña", "opcional": True,
             "motivo": "Solo si la respuesta es no: «organic chicken certification» costó ARS 11.056 por un clic en septiembre."}],
        3: [{"accion": "cambiar", "tipo": "texto", "texto": "Límite de oferta de CPC máximo: ARS 12.000", "destino": "Configuración de la campaña › Ofertas › Maximizar clics",
             "motivo": "Deja pasar los clics que valen (promedio ARS 8.769; «organic certification», la keyword principal, ARS 10.843) y corta los de ARS 14.800–17.500."}],
    },
    "CU:SEM:anuncio:cu-portugal-plasticos:une-15343": {
        4: [{"accion": "pausar", "tipo": "keyword", "texto": "recyclass", "concordancia": "frase", "destino": "Grupo «RecyClass»", "opcional": True,
             "motivo": "Solo si al 28 nov los clics pagos de RecyClass no trajeron contactos. La exacta [recyclass] queda."}],
    },
    "CU:SEM:anuncio:cu-espana-ifs:food-safety": {
        4: [{"accion": "crear", "tipo": "grupo", "texto": "FSSC 22000", "destino": "La campaña", "opcional": True,
             "motivo": f"Solo si «fssc 22000» pasa de ~100 impresiones por mes. URL final: {CU_ES}fssc-22000-food-safety-system-certification/ · mover ahí [fssc 22000] y [certificacion fssc 22000]."}],
    },
    "PS:SEM:anuncio:ps-argentina-suse-huella-de-agua:gestion-agua": {
        2: [{"accion": "reemplazar", "tipo": "descripcion", "texto": t, "reemplaza": r, "destino": f"Anuncio id {ad} · grupo «{g}»", "prioritario": True,
             "motivo": "Mismo texto interno que en «Huella hidrica»."}
            for ad, g in (("817970221142", "Gestion agua"), ("817970221145", "Riesgo hidrico"))
            for r, t in (("Testee demanda en sectores con alto consumo de agua y presion ESG.", "Te acompañamos a medir la huella hídrica de tu empresa y de tu producto."),
                         ("Hable con Peterson para definir alcance y viabilidad del servicio.", "Hablemos de tu consumo de agua: te decimos por dónde empezar a medir."))],
    },
}


def completar(t):
    """Aplica MANUAL sobre la tarjeta que armó unificar(): reemplaza título, detalle, grupo, campos de evidencia y anuncios."""
    m = MANUAL.get(t["clave"])
    if not m:
        return t
    t = dict(t, **{k: m[k] for k in ("titulo", "detalle", "prioridad", "grupo") if k in m})
    ev = dict(t["evidencia"], **m.get("evidencia", {}))
    ev["resumen"] = ev.get("resumen") or t["titulo"]
    if "anuncios" in m:
        ev["anuncios"] = m["anuncios"]
    t["evidencia"] = ev
    return t


def validar(t):
    errores = []
    marca = t["clave"].split(":")[0]
    for a in t["evidencia"].get("anuncios", []):
        for campo, limite in (("titulos_propuestos", 30), ("descripciones_propuestas", 90)):
            for p in a.get(campo, []):
                texto = p["texto"] if isinstance(p, dict) else p
                if len(texto) > limite:
                    errores.append(f"{t['clave']}: «{texto}» tiene {len(texto)} caracteres (máx. {limite})")
                if re.search(PROHIBIDO[marca], texto, re.I):
                    errores.append(f"{t['clave']}: vocabulario prohibido en «{texto}»")
    return errores


def q(v):
    if v is None:
        return "null"
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def main():
    tarjetas = [ISCC, EUDR] + [completar(unificar(a, p)) for a, p in PARES]
    for t in tarjetas:
        t["evidencia"]["pasos"] = con_items(t["evidencia"], EXTRAS.get(t["clave"], {}))
    errores = [e for t in tarjetas for e in validar(t) + validar_campana(t["clave"], t["evidencia"])]
    if errores:
        raise SystemExit("\n".join(errores))
    out = [f"-- Unificación de tarjetas SEM ({MES}): una acción, una tarjeta, con dónde y por qué. Generado por unificar_tarjetas_sem.py.", "begin;"]
    for t in tarjetas:
        ev = dict(t["evidencia"], revisiones=[{"mes": MES, "accion": "unificación", "datos_hasta": FECHA_DATOS}])
        out.append(
            f"update seo_sem.recomendaciones r set titulo = {q(t['titulo'])}, detalle = {q(t['detalle'])}, prioridad = {q(t['prioridad'])}, evidencia = {q(ev)}, "
            f"campana_id = c.id, grupo_id = g.id, actualizada_por = {q(USUARIO)}\n"
            f"from seo_sem.campanas c left join seo_sem.grupos g on g.campana_id = c.id and g.nombre = {q(t.get('grupo'))}\n"
            f"where r.clave = {q(t['clave'])} and c.cuenta = 'actual' and c.nombre = {q(t['campana'])};")
        if t.get("descarta"):
            motivo = f"Unificada en «{t['titulo']}»: una acción, una tarjeta."
            out.append(
                f"with r as (update seo_sem.recomendaciones set estado = 'descartada', motivo_descarte = {q(motivo)}, mes_cierre = {q(MES)}, actualizada_por = {q(USUARIO)} "
                f"where clave = {q(t['descarta'])} and estado <> 'descartada' returning id, (select estado from seo_sem.recomendaciones x where x.clave = {q(t['descarta'])}) as antes)\n"
                f"insert into seo_sem.recomendacion_eventos (recomendacion_id, de_estado, a_estado, motivo, usuario) select id, antes, 'descartada', {q(motivo)}, {q(USUARIO)} from r;")
    for clave, campanas in CAMPANAS_EXPLICITAS.items():
        out.append(f"update seo_sem.recomendaciones set evidencia = evidencia || {q({'campanas': campanas})} where clave = {q(clave)};")
    out.append("commit;")
    ruta = os.path.join(ROOT, "informe", f"unificacion_sem_{MES}.sql")
    open(ruta, "w", encoding="utf-8").write("\n".join(out) + "\n")
    json.dump(tarjetas, open(os.path.join(ROOT, "informe", f"unificacion_sem_{MES}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(f"-> {ruta}: {len(tarjetas)} tarjetas reescritas, {sum(1 for t in tarjetas if t.get('descarta'))} unificadas, {len(CAMPANAS_EXPLICITAS)} con campañas explícitas")
    for t in tarjetas:
        print(" ·", t["titulo"])


if __name__ == "__main__":
    main()
