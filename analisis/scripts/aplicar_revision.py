# -*- coding: utf-8 -*-
"""
aplicar_revision.py — convierte la revisión mensual de mejoras SEM (informe/revision_sem_<AAAA-MM>.json) en SQL para el
tablero Marcomms SEO-SEM. Lo usa la rutina mensual (RUTINA_REVISION_MENSUAL_SEM.md).

El JSON de entrada (lo escribe Claude en la revisión):
{
  "mes": "2026-11",                    # mes de alta de las tarjetas nuevas (el mes en que se hace la revisión)
  "datos_hasta": "2026-10-31",         # último día de datos analizado
  "nuevas":   [{"clave": "CU:SEM:campana:cu-espana-smeta@2026-11", "marca": "CU", "campana": "CU España - Smeta - Search",
                "grupo": null, "titulo": "...", "detalle": "...", "prioridad": "alta|media|baja",
                "evidencia": {"ficha": "campana", "campana": "CU España - Smeta - Search", "unidad": "España",
                              "acciones": ["negativas", ...], "resumen": "...", "por_que": "...", "pasos": [...],
                              "keywords": [...], "negativas": [...], "negativas_decision": "...", "anuncios": [...],
                              "datos_hasta": "2026-10-31"}}],
              (campos completos de la ficha «campana»: RUTINA_REVISION_MENSUAL_SEM.md §6; ejemplo real:
               informe/unificacion_sem_2026-10.json)
  "ajustes":  [{"clave": "...", "titulo": "...", "detalle": "...", "prioridad": "...", "evidencia": {...}, "motivo": "..."}],
  "descartes":[{"clave": "...", "motivo": "..."}],
  "verificadas": [{"clave": "...", "nota": "..."}]
}
Reglas que aplica el SQL (no se pueden saltear desde el JSON):
  · nuevas: se insertan en «propuesta»; si la clave ya existe no se toca nada.
  · ajustes: cambian tarjetas en «propuesta» o «en proceso» (nunca hechas ni descartadas). La evidencia se combina
    con la anterior y se agrega una entrada en evidencia.revisiones con el mes, la fecha y el motivo: el tablero muestra
    la tarjeta como «Actualizada» (con el motivo) hasta la revisión siguiente. El motivo dice qué cambió y por qué.
  · descartes: solo «propuesta» → «descartada», con motivo, mes de cierre y un movimiento en el historial.
  · verificadas: solo tarjetas en «hecha»; marca verificada_api.
Valida antes de generar: marcas, prioridades, tipos de mejora, campañas que existan, vocabulario de marca.

Uso: python aplicar_revision.py informe/revision_sem_2026-11.json  →  informe/revision_sem_2026-11.sql
"""
import datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USUARIO = "Revisión mensual (Claude)"
ACCIONES = {"anuncio", "keywords", "negativas", "estructura", "pausa", "landing", "revisar", "contenido", "tecnico"}
PRIORIDADES = {"alta", "media", "baja"}
MARCAS = {"CU", "PCU", "PS"}
# Control Union y PCU certifican: nunca asesoran ni diseñan estrategias. Peterson Solutions es consultora: nunca certifica.
PROHIBIDO = {
    "CU": r"\b(asesor\w*|consultor\w*|diseñamos (tu|su) estrategia|te preparamos)\b",
    "PCU": r"\b(asesor\w*|consultor\w*|diseñamos (tu|su) estrategia|te preparamos)\b",
    "PS": r"\b(certificamos|emitimos (el )?certificado\w*)\b",
}


def q(v):
    if v is None:
        return "null"
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def validar_campana(c, ev):
    """Reglas de Felipe (21 oct 2026) para la ficha «campana»: dónde, porqué de cada anuncio, keywords y negativas."""
    errores = []
    if not (ev.get("campana") or ev.get("campanas")):
        errores.append(f"{c}: falta evidencia.campana (nombre completo) o evidencia.campanas")
    for k in ("resumen", "por_que", "datos_hasta"):
        if not ev.get(k):
            errores.append(f"{c}: falta evidencia.{k}")
    if not ev.get("pasos"):
        errores.append(f"{c}: falta evidencia.pasos (qué hacer, en orden)")
    for i, p in enumerate(ev.get("pasos") or [], 1):
        if not p.get("titulo") or not p.get("donde"):
            errores.append(f"{c}: paso {i} sin «titulo» o «donde» (campaña › grupo › anuncio)")
        # Felipe (28 oct): cada paso dice concretamente qué cargar, no «las de la tabla»
        if p.get("accion") in ("negativas", "keywords", "pausa", "anuncio", "estructura", "contenido", "tecnico") and not p.get("items"):
            errores.append(f"{c}: paso {i} («{p.get('titulo')}») sin «items»: la lista exacta de qué cargar")
        for it in p.get("items") or []:
            if not it.get("texto") or not it.get("destino") or not it.get("accion"):
                errores.append(f"{c}: paso {i}: cada item necesita accion, texto y destino")
                break
            if it.get("tipo") in ("negativa", "keyword") and it.get("concordancia") not in ("exacta", "frase", "amplia"):
                errores.append(f"{c}: paso {i}: «{it['texto']}» sin concordancia")
        marca = c.split(":")[0]
        for it in p.get("items") or []:
            if it.get("tipo") in ("titulo", "descripcion") and marca in PROHIBIDO and re.search(PROHIBIDO[marca], it.get("texto") or "", re.I):
                errores.append(f"{c}: paso {i}: vocabulario prohibido para {marca} en «{it['texto']}»")
            if it.get("tipo") == "titulo" and len(it.get("texto") or "") > 30 or it.get("tipo") == "descripcion" and len(it.get("texto") or "") > 90:
                errores.append(f"{c}: paso {i}: «{it['texto']}» pasa el largo máximo ({len(it['texto'])})")
        vago = re.search(r"de la tabla|de abajo|de arriba|anexo|ver la tarjeta", f"{p.get('titulo')} {p.get('detalle') or ''}", re.I)
        if vago:
            errores.append(f"{c}: paso {i} remite a algo que no está en el paso («{vago.group(0)}»): escribirlo")
    acciones = set(ev.get("acciones") or [])
    if "estructura" in acciones and not ev.get("keywords"):
        errores.append(f"{c}: propone estructura (grupo nuevo) sin keywords recomendadas")
    if ("estructura" in acciones or ev.get("keywords")) and not ev.get("negativas_decision"):
        errores.append(f"{c}: falta negativas_decision (si hay que agregar negativas y por qué, o por qué no)")
    for kw in ev.get("keywords") or []:
        if kw.get("concordancia") not in ("exacta", "frase", "amplia") or not kw.get("motivo"):
            errores.append(f"{c}: keyword «{kw.get('texto')}» sin concordancia válida o sin motivo")
    for ng in ev.get("negativas") or []:
        if ng.get("nivel") not in ("campaña", "grupo") or not ng.get("motivo"):
            errores.append(f"{c}: negativa «{ng.get('texto')}» sin nivel (campaña|grupo) o sin motivo")
    if "anuncio" in acciones and not ev.get("anuncios"):
        errores.append(f"{c}: la acción «anuncio» necesita evidencia.anuncios")
    for an in ev.get("anuncios") or []:
        nombre = an.get("anuncio_id") or an.get("grupo") or "?"
        if not an.get("grupo"):
            errores.append(f"{c}: anuncio {nombre} sin grupo")
        if not an.get("anuncio_id") and "nuevo" not in (an.get("accion") or "").lower():
            errores.append(f"{c}: anuncio del grupo «{an.get('grupo')}» sin anuncio_id (solo un anuncio nuevo puede no tenerlo)")
        if not an.get("motivo"):
            errores.append(f"{c}: anuncio {nombre} sin motivo del cambio")
        props = (an.get("titulos_propuestos") or []) + (an.get("descripciones_propuestas") or [])
        for p in props:
            if not isinstance(p, dict) or not p.get("texto") or not p.get("motivo"):
                errores.append(f"{c}: anuncio {nombre}: cada propuesta necesita «texto» y «motivo»")
                break
        if props and not any(isinstance(p, dict) and p.get("prioritario") for p in props):
            errores.append(f"{c}: anuncio {nombre}: marcá con prioritario las propuestas que de verdad conviene hacer")
        for p in an.get("titulos_propuestos") or []:
            if isinstance(p, dict) and len(p.get("texto") or "") > 30:
                errores.append(f"{c}: título de {len(p['texto'])} caracteres (máx. 30): «{p['texto']}»")
        for p in an.get("descripciones_propuestas") or []:
            if isinstance(p, dict) and len(p.get("texto") or "") > 90:
                errores.append(f"{c}: descripción de {len(p['texto'])} caracteres (máx. 90): «{p['texto']}»")
        # lo que se quita existe hoy, lo que se reemplaza está en «quitar», y no se pasa de 15 títulos y 4 descripciones
        hoy_t, hoy_d = an.get("titulos_hoy") or [], an.get("descripciones_hoy") or []
        quitar = {q["texto"] if isinstance(q, dict) else q for q in an.get("quitar") or []}
        if an.get("anuncio_id"):
            errores += [f"{c}: anuncio {nombre}: «{q}» se quita pero no está en titulos_hoy ni descripciones_hoy" for q in quitar if q not in hoy_t + hoy_d]
        errores += [f"{c}: anuncio {nombre}: «{p['reemplaza']}» se reemplaza pero no está en «quitar»"
                    for p in props if isinstance(p, dict) and p.get("reemplaza") and p["reemplaza"] not in quitar]
        n_t = len(hoy_t) - len(quitar & set(hoy_t)) + len(an.get("titulos_propuestos") or [])
        n_d = len(hoy_d) - len(quitar & set(hoy_d)) + len(an.get("descripciones_propuestas") or [])
        if n_t > 15 or n_d > 4:
            errores.append(f"{c}: anuncio {nombre}: quedaría con {n_t} títulos y {n_d} descripciones (máx. 15 y 4)")
    return errores


def validar_seo(c, ev, marca=None):
    """Ficha «seo»: sitio y páginas exactas, por qué con datos de Search Console, y pasos con la lista de qué cambiar."""
    errores = []
    for k in ("sitio", "resumen", "por_que", "datos_hasta"):
        if not ev.get(k):
            errores.append(f"{c}: falta evidencia.{k}")
    if not ev.get("paginas"):
        errores.append(f"{c}: falta evidencia.paginas (URL exactas)")
    for p in ev.get("paginas") or []:
        if not str(p.get("url", "")).startswith("http"):
            errores.append(f"{c}: página sin URL completa: {p}")
    malas = set(ev.get("acciones") or []) - ACCIONES
    if not ev.get("acciones") or malas:
        errores.append(f"{c}: evidencia.acciones vacío o con valores inválidos {sorted(malas)}")
    if not ev.get("pasos"):
        errores.append(f"{c}: falta evidencia.pasos")
    for i, p in enumerate(ev.get("pasos") or [], 1):
        if not p.get("titulo") or not p.get("donde"):
            errores.append(f"{c}: paso {i} sin «titulo» o «donde»")
        if p.get("accion") in ("contenido", "tecnico", "landing", "estructura") and not p.get("items"):
            errores.append(f"{c}: paso {i} («{p.get('titulo')}») sin «items»")
        for it in p.get("items") or []:
            if not it.get("texto") or not it.get("destino") or not it.get("accion"):
                errores.append(f"{c}: paso {i}: cada item necesita accion, texto y destino")
                break
            largo = {"title": 60, "meta": 155, "h1": 70}.get(it.get("tipo"))
            if largo and len(it["texto"]) > largo:
                errores.append(f"{c}: {it['tipo']} de {len(it['texto'])} caracteres (máx. {largo}): «{it['texto']}»")
        vago = re.search(r"de la tabla|de abajo|de arriba|anexo|…", f"{p.get('titulo')} {p.get('detalle') or ''}", re.I)
        if vago:
            errores.append(f"{c}: paso {i} remite a algo que no está en el paso o está cortado («{vago.group(0)}»)")
    # el vocabulario de marca se controla en lo que se publica (los textos propuestos), no en los motivos
    if marca in PROHIBIDO:
        for it in (it for p in ev.get("pasos") or [] for it in p.get("items") or []):
            m = re.search(PROHIBIDO[marca], it.get("texto") or "", re.I)
            if m:
                errores.append(f"{c}: vocabulario prohibido para {marca} en «{it['texto']}»: «{m.group(0)}»")
    return errores


def validar(rev, campanas):
    errores = []
    if not re.fullmatch(r"\d{4}-\d{2}", rev.get("mes", "")):
        errores.append("falta «mes» (AAAA-MM)")
    claves = [x["clave"] for k in ("nuevas", "ajustes", "descartes", "verificadas") for x in rev.get(k, [])]
    repetidas = {c for c in claves if claves.count(c) > 1}
    if repetidas:
        errores.append(f"claves repetidas entre secciones: {sorted(repetidas)}")
    for n in rev.get("nuevas", []):
        c = n.get("clave", "?")
        if n.get("marca") not in MARCAS:
            errores.append(f"{c}: marca inválida {n.get('marca')!r}")
        if n.get("prioridad") not in PRIORIDADES:
            errores.append(f"{c}: prioridad inválida {n.get('prioridad')!r}")
        if not n.get("titulo") or not n.get("detalle"):
            errores.append(f"{c}: falta título o detalle")
        ev = n.get("evidencia") or {}
        malas = set(ev.get("acciones") or []) - ACCIONES
        if not ev.get("acciones") or malas:
            errores.append(f"{c}: evidencia.acciones vacío o con valores inválidos {sorted(malas)}")
        if ":SEO:" in c:
            # SEO (desde nov 2026): ficha «seo», una tarjeta por sitio y tema
            if ev.get("ficha") != "seo":
                errores.append(f"{c}: una tarjeta SEO lleva evidencia.ficha «seo»")
            errores += validar_seo(c, ev, n.get("marca"))
            if not c.startswith(f"{n.get('marca')}:SEO:"):
                errores.append(f"{c}: la clave tiene que empezar con «{n.get('marca')}:SEO:»")
            continue
        if ev.get("ficha") != "campana":
            errores.append(f"{c}: evidencia.ficha tiene que ser «campana» (una tarjeta por acción y por campaña)")
        errores += validar_campana(c, ev)
        if n.get("campana") and campanas and n["campana"] not in campanas:
            errores.append(f"{c}: la campaña {n['campana']!r} no está en el catálogo actual")
        if not c.startswith(f"{n.get('marca')}:SEM:"):
            errores.append(f"{c}: la clave tiene que empezar con «{n.get('marca')}:SEM:»")
    for k in ("nuevas", "ajustes"):
        for n in rev.get(k, []):
            marca = n.get("marca") or n["clave"].split(":")[0]
            texto = " ".join(str(n.get(x) or "") for x in ("titulo", "detalle")) + " " + json.dumps(n.get("evidencia") or {}, ensure_ascii=False)
            if marca in PROHIBIDO and re.search(PROHIBIDO[marca], texto, re.I):
                errores.append(f"{n['clave']}: vocabulario prohibido para {marca}: «{re.search(PROHIBIDO[marca], texto, re.I).group(0)}»")
    for n in rev.get("ajustes", []):
        if n.get("prioridad") and n["prioridad"] not in PRIORIDADES:
            errores.append(f"{n['clave']}: prioridad inválida {n['prioridad']!r}")
        if (n.get("evidencia") or {}).get("ficha") == "campana":
            errores += validar_campana(n["clave"], n["evidencia"])
        elif (n.get("evidencia") or {}).get("ficha") == "seo":
            errores += validar_seo(n["clave"], n["evidencia"], n.get("marca") or n["clave"].split(":")[0])
    # Una acción, una tarjeta: dos nuevas sobre la misma campaña se juntan en una sola.
    por_campana = {}
    for n in rev.get("nuevas", []):
        if n.get("campana"):
            por_campana.setdefault(n["campana"], []).append(n["clave"])
    for camp, cs in por_campana.items():
        if len(cs) > 1:
            errores.append(f"{len(cs)} tarjetas nuevas para «{camp}» ({', '.join(cs)}): juntalas en una con pasos")
    for k in ("ajustes", "descartes"):
        for n in rev.get(k, []):
            if not n.get("motivo"):
                errores.append(f"{n['clave']}: {k} sin motivo")
    return errores


def sql(rev):
    mes, hasta = rev["mes"], rev.get("datos_hasta")
    out = [f"-- Revisión mensual SEM {mes} (datos hasta {hasta}). Generado por aplicar_revision.py. Idempotente.", "begin;"]
    for n in rev.get("nuevas", []):
        ev = dict(n.get("evidencia") or {}, revisiones=[{"mes": mes, "accion": "alta", "datos_hasta": hasta}])
        out.append(
            "insert into seo_sem.recomendaciones (clave, marca, tipo, campana_id, grupo_id, sitio, pagina, titulo, detalle, evidencia, prioridad, estado, mes_alta, origen, actualizada_por)\n"
            f"select {q(n['clave'])}, {q(n['marca'])}, {q('SEO' if ':SEO:' in n['clave'] else 'SEM')}, c.id, g.id, {q(n.get('sitio') or ev.get('sitio'))}, {q(n.get('pagina'))}, {q(n['titulo'])}, {q(n['detalle'])}, {q(ev)}, "
            f"{q(n['prioridad'])}, 'propuesta', {q(mes)}, {q('revision-mensual-' + mes)}, {q(USUARIO)}\n"
            f"from (select 1) x left join seo_sem.campanas c on c.cuenta = 'actual' and c.nombre = {q(n.get('campana'))}\n"
            f"left join seo_sem.grupos g on g.campana_id = c.id and g.nombre = {q(n.get('grupo'))}\n"
            "on conflict (clave) do nothing;")
    for a in rev.get("ajustes", []):
        sets = [f"{k} = {q(a[k])}" for k in ("titulo", "detalle", "prioridad") if a.get(k)]
        entrada = {"mes": mes, "accion": "ajuste", "motivo": a["motivo"], "datos_hasta": hasta, "fecha": datetime.date.today().isoformat()}
        sets.append(f"evidencia = (evidencia || {q(a.get('evidencia') or {})}) || jsonb_build_object('revisiones', coalesce(evidencia->'revisiones', '[]'::jsonb) || {q([entrada])})")
        sets.append(f"actualizada_por = {q(USUARIO)}")
        out.append(f"update seo_sem.recomendaciones set {', '.join(sets)} where clave = {q(a['clave'])} and estado in ('propuesta', 'en_proceso');")
    for d in rev.get("descartes", []):
        out.append(
            "with r as (update seo_sem.recomendaciones set estado = 'descartada', "
            f"motivo_descarte = {q(d['motivo'])}, mes_cierre = {q(mes)}, actualizada_por = {q(USUARIO)} "
            f"where clave = {q(d['clave'])} and estado = 'propuesta' returning id)\n"
            f"insert into seo_sem.recomendacion_eventos (recomendacion_id, de_estado, a_estado, motivo, usuario) select id, 'propuesta', 'descartada', {q(d['motivo'])}, {q(USUARIO)} from r;")
    for v in rev.get("verificadas", []):
        entrada = {"mes": mes, "accion": "verificada", "nota": v.get("nota")}
        out.append(
            "update seo_sem.recomendaciones set verificada_api = true, verificada_en = now(), "
            f"evidencia = evidencia || jsonb_build_object('revisiones', coalesce(evidencia->'revisiones', '[]'::jsonb) || {q([entrada])}) "
            f"where clave = {q(v['clave'])} and estado = 'hecha' and not verificada_api;")
    out.append("commit;")
    return "\n".join(out) + "\n"


def catalogo():
    """Nombres de campaña del snapshot de estructura más reciente (para validar)."""
    import glob
    import pandas as pd
    snaps = sorted(glob.glob(os.path.join(ROOT, "datos", "ads", "api", "estructura_*")))
    if not snaps:
        return set()
    return set(pd.read_csv(os.path.join(snaps[-1], "campanas.csv"), encoding="utf-8-sig")["campaign.name"].astype(str))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ruta = sys.argv[1]
    rev = json.load(open(ruta, encoding="utf-8"))
    errores = validar(rev, catalogo())
    if errores:
        print("La revisión tiene errores; no se generó SQL:")
        for e in errores:
            print("  ·", e)
        sys.exit(1)
    salida = os.path.splitext(ruta)[0] + ".sql"
    open(salida, "w", encoding="utf-8").write(sql(rev))
    print(f"-> {salida}: {len(rev.get('nuevas', []))} nuevas, {len(rev.get('ajustes', []))} ajustes, "
          f"{len(rev.get('descartes', []))} descartes, {len(rev.get('verificadas', []))} verificadas")


if __name__ == "__main__":
    main()
