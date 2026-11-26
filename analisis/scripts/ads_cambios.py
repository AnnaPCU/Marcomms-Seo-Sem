# -*- coding: utf-8 -*-
"""
ads_cambios.py — historial de cambios de Google Ads (change_event, solo lectura), para la vista «Impacto» del tablero:
qué se cargó de verdad en cada campaña (keywords, negativas, pausas, anuncios, grupos, presupuesto) y cuándo.

Google guarda el historial solo 30 días: correr al menos una vez por mes (lo hace el cierre de mes, día 4) y, si se
quiere, cada semana. La carga en la base es idempotente (clave = id del evento), así que no importa solapar ventanas.

Uso:
  python ads_cambios.py                          últimos 29 días hasta hoy
  python ads_cambios.py --desde 2026-10-20 --hasta 2026-11-10

Salida:
  datos/ads/api/<marca>/ads_<marca>_cambios_<desde>_<hasta>.csv   archivo por marca (nunca uno común)
  informe/datos_cambios_ads.json                                  lo que carga scripts/publicar.py --solo cambios
No guarda el correo de quién hizo el cambio: el tablero solo necesita qué y cuándo.
"""
import argparse, datetime as dt, json, os
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf.json_format import MessageToDict
from ads_export import YAML, CUENTAS, marca_de

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
HOY = dt.date.today()

GAQL = """SELECT change_event.resource_name, change_event.change_date_time, change_event.change_resource_type,
  change_event.resource_change_operation, change_event.changed_fields, change_event.client_type,
  change_event.old_resource, change_event.new_resource, change_event.change_resource_name, campaign.id, campaign.name, ad_group.name
FROM change_event
WHERE change_event.change_date_time >= '{a}' AND change_event.change_date_time <= '{b} 23:59:59'
ORDER BY change_event.change_date_time
LIMIT 10000"""

CONC = {"EXACT": "exacta", "PHRASE": "frase", "BROAD": "amplia"}


def keyword(texto, match):
    """Texto y concordancia de una keyword. En la interfaz se pueden escribir con [ ] o « " » y Google no informa el tipo."""
    t = (texto or "").strip()
    c = CONC.get(match or "")
    if t.startswith("[") and t.endswith("]"):
        t, c = t[1:-1].strip(), c or "exacta"
    elif t.startswith('"') and t.endswith('"'):
        t, c = t[1:-1].strip(), c or "frase"
    return t, c or ("amplia" if t else None)


def textos(lista):
    return [x.get("text", "") for x in (lista or []) if x.get("text")]


def detalle(tipo, viejo, nuevo):
    """Lo que importa de cada cambio, en un dict plano (vacíos fuera)."""
    d = {}
    if tipo in ("AD_GROUP_CRITERION", "CAMPAIGN_CRITERION"):
        k = "ad_group_criterion" if tipo == "AD_GROUP_CRITERION" else "campaign_criterion"
        n, v = nuevo.get(k, {}), viejo.get(k, {})
        kw = n.get("keyword") or v.get("keyword") or {}
        d["texto"], d["concordancia"] = keyword(kw.get("text"), kw.get("match_type"))
        neg = n.get("negative", v.get("negative"))
        d["negativa"] = bool(neg) if neg is not None else (tipo == "CAMPAIGN_CRITERION")
        d["estado_antes"], d["estado_despues"] = v.get("status"), n.get("status")
        d["criterio"] = n.get("resource_name") or v.get("resource_name")
        d["urls_despues"] = n.get("final_urls")
    elif tipo in ("AD", "AD_GROUP_AD"):
        na = nuevo.get("ad") or nuevo.get("ad_group_ad", {}).get("ad") or {}
        va = viejo.get("ad") or viejo.get("ad_group_ad", {}).get("ad") or {}
        rn, rv = na.get("responsive_search_ad", {}), va.get("responsive_search_ad", {})
        d["titulos_antes"], d["titulos_despues"] = textos(rv.get("headlines")), textos(rn.get("headlines"))
        d["descripciones_antes"], d["descripciones_despues"] = textos(rv.get("descriptions")), textos(rn.get("descriptions"))
        d["urls_antes"], d["urls_despues"] = va.get("final_urls"), na.get("final_urls")
        d["anuncio_id"] = str(na.get("id") or va.get("id") or "") or None
        d["estado_antes"] = viejo.get("ad_group_ad", {}).get("status")
        d["estado_despues"] = nuevo.get("ad_group_ad", {}).get("status")
    elif tipo == "AD_GROUP":
        n, v = nuevo.get("ad_group", {}), viejo.get("ad_group", {})
        d["nombre"] = n.get("name") or v.get("name")
        d["estado_antes"], d["estado_despues"] = v.get("status"), n.get("status")
    elif tipo == "CAMPAIGN_BUDGET":
        n, v = nuevo.get("campaign_budget", {}), viejo.get("campaign_budget", {})
        if "amount_micros" in v: d["presupuesto_antes"] = int(v["amount_micros"]) / 1e6
        if "amount_micros" in n: d["presupuesto_despues"] = int(n["amount_micros"]) / 1e6
    elif tipo == "CAMPAIGN":
        n, v = nuevo.get("campaign", {}), viejo.get("campaign", {})
        d["estado_antes"], d["estado_despues"] = v.get("status"), n.get("status")
        d["puja"] = n.get("bidding_strategy_type")
    if tipo in ("AD", "AD_GROUP_AD"):
        # solo lo que entró y lo que salió: las listas completas no hacen falta para saber qué se cambió
        for campo, corto in (("titulos", "titulos"), ("descripciones", "descripciones")):
            antes, despues = d.pop(f"{campo}_antes", []), d.pop(f"{campo}_despues", [])
            fem = "as" if campo == "descripciones" else "os"
            d[f"{corto}_agregad{fem}"] = [x for x in despues if x not in antes]
            d[f"{corto}_quitad{fem}"] = [x for x in antes if x not in despues]
        if d.get("urls_despues") == d.get("urls_antes"):
            d.pop("urls_despues", None)
        d.pop("urls_antes", None)
    return {k: x for k, x in d.items() if x not in (None, "", [])}


def resumen(tipo, op, d, grupo):
    """Una línea legible: «Negativa agregada: "gap analysis" (frase)», «Keyword pausada: [global gap]»…"""
    en = f" en «{grupo}»" if grupo else ""
    if tipo in ("AD_GROUP_CRITERION", "CAMPAIGN_CRITERION"):
        if not d.get("texto"):
            return "Segmentación de la campaña editada (ubicación, idioma u otro criterio)" if tipo == "CAMPAIGN_CRITERION" else f"Criterio editado{en}"
        t = f"«{d.get('texto', '?')}» ({d.get('concordancia', '?')})"
        clase = "Negativa" if d.get("negativa") else "Keyword"
        if op == "CREATE": return f"{clase} agregada: {t}{en if tipo == 'AD_GROUP_CRITERION' else ' a la campaña'}"
        if op == "REMOVE": return f"{clase} quitada: {t}{en}"
        if d.get("estado_despues") == "PAUSED": return f"{clase} pausada: {t}{en}"
        if d.get("estado_despues") == "ENABLED" and d.get("estado_antes") == "PAUSED": return f"{clase} reactivada: {t}{en}"
        return f"{clase} editada: {t}{en}"
    if tipo in ("AD", "AD_GROUP_AD"):
        mas, menos = len(d.get("titulos_agregados", [])), len(d.get("titulos_quitados", []))
        dm = len(d.get("descripciones_agregadas", []))
        if op == "CREATE": return f"Anuncio nuevo{en} ({mas} títulos)"
        if d.get("estado_despues") and d.get("estado_despues") != d.get("estado_antes"):
            return f"Anuncio {'pausado' if d['estado_despues'] == 'PAUSED' else 'activado' if d['estado_despues'] == 'ENABLED' else d['estado_despues'].lower()}{en}"
        partes = [p for p in (f"+{mas} títulos" if mas else "", f"−{menos} títulos" if menos else "", f"{dm} descripciones nuevas" if dm else "",
                              "URL final cambiada" if d.get("urls_despues") else "") if p]
        return f"Anuncio editado{en}: " + (", ".join(partes) or "otros campos")
    if tipo == "AD_GROUP":
        if op == "CREATE": return f"Grupo creado: «{d.get('nombre', grupo)}»"
        return f"Grupo «{d.get('nombre', grupo)}» {'pausado' if d.get('estado_despues') == 'PAUSED' else 'activado' if d.get('estado_despues') == 'ENABLED' else 'quitado' if d.get('estado_despues') == 'REMOVED' else 'editado'}"
    if tipo == "CAMPAIGN_BUDGET":
        a, b = d.get("presupuesto_antes"), d.get("presupuesto_despues")
        return f"Presupuesto diario: ARS {a:,.0f} → ARS {b:,.0f}".replace(",", ".") if a and b else "Presupuesto editado"
    if tipo == "CAMPAIGN":
        return "Campaña creada" if op == "CREATE" else "Configuración de la campaña editada"
    if tipo == "CAMPAIGN_ASSET":
        return "Recurso agregado a la campaña (extensión)" if op == "CREATE" else "Recurso de la campaña editado"
    return f"{tipo.lower()} {op.lower()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde"); ap.add_argument("--hasta")
    a = ap.parse_args()
    hasta = dt.date.fromisoformat(a.hasta) if a.hasta else HOY
    desde = dt.date.fromisoformat(a.desde) if a.desde else hasta - dt.timedelta(days=29)
    if (HOY - desde).days > 30:
        raise SystemExit("Google guarda el historial de cambios solo 30 días: usá un --desde más reciente.")
    client = GoogleAdsClient.load_from_storage(YAML)
    svc = client.get_service("GoogleAdsService")
    cid = CUENTAS["cuentas"]["principal"]
    filas = []
    try:
        for lote in svc.search_stream(customer_id=cid, query=GAQL.format(a=desde, b=hasta)):
            for r in lote.results:
                ce = MessageToDict(r.change_event._pb, preserving_proto_field_name=True)
                tipo, op = ce.get("change_resource_type"), ce.get("resource_change_operation")
                d = detalle(tipo, ce.get("old_resource", {}), ce.get("new_resource", {}))
                if tipo in ("AD_GROUP_CRITERION", "CAMPAIGN_CRITERION"):
                    d["criterio"] = ce.get("change_resource_name") or d.get("criterio")
                if tipo == "AD_GROUP_AD":
                    d["anuncio_rn"] = ce.get("change_resource_name")
                grupo = r.ad_group.name or None
                filas.append(dict(evento_id=ce["resource_name"], ads_id=str(r.campaign.id), campana=r.campaign.name, grupo=grupo,
                                  fecha=ce["change_date_time"][:19], recurso=tipo, operacion=op, origen=ce.get("client_type"),
                                  campos=ce.get("changed_fields"), detalle=d, resumen=resumen(tipo, op, d, grupo)))
    except GoogleAdsException as ex:
        raise SystemExit("Google Ads API: " + "; ".join(e.message for e in ex.failure.errors))

    # Las pausas y ediciones de keywords no traen el texto: se completa con el estado actual del criterio (incluye los quitados).
    sin_texto = sorted({f["detalle"]["criterio"] for f in filas if f["recurso"] == "AD_GROUP_CRITERION" and f["detalle"].get("criterio") and not f["detalle"].get("texto")})
    info = {}
    for i in range(0, len(sin_texto), 500):
        lista = ", ".join(f"'{x}'" for x in sin_texto[i:i + 500])
        q = ("SELECT ad_group_criterion.resource_name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
             f"ad_group_criterion.negative FROM ad_group_criterion WHERE ad_group_criterion.resource_name IN ({lista})")
        for lote in svc.search_stream(customer_id=cid, query=q):
            for r in lote.results:
                c = r.ad_group_criterion
                info[c.resource_name] = (c.keyword.text, c.keyword.match_type.name, c.negative)
    for f in filas:
        d = f["detalle"]
        if d.get("criterio") in info:
            t, m, neg = info[d["criterio"]]
            d["texto"], d["concordancia"] = keyword(t, m)
            d["negativa"] = bool(neg)
            f["resumen"] = resumen(f["recurso"], f["operacion"], d, f["grupo"])
        d.pop("criterio", None)

    # Un anuncio que se activa (estaba en pausa) no trae sus textos: se completan con los actuales, porque desde ese día salen al aire.
    activados = {f["detalle"].get("anuncio_rn"): f for f in filas if f["recurso"] == "AD_GROUP_AD" and f["operacion"] == "UPDATE"
                 and f["detalle"].get("estado_despues") == "ENABLED" and not f["detalle"].get("titulos_agregados")}
    activados.pop(None, None)
    if activados:
        lista = ", ".join(f"'{x}'" for x in activados)
        q = ("SELECT ad_group_ad.resource_name, ad_group_ad.ad.id, ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines, "
             f"ad_group_ad.ad.responsive_search_ad.descriptions FROM ad_group_ad WHERE ad_group_ad.resource_name IN ({lista})")
        for lote in svc.search_stream(customer_id=cid, query=q):
            for r in lote.results:
                f = activados.get(r.ad_group_ad.resource_name)
                if not f:
                    continue
                ad = r.ad_group_ad.ad
                f["detalle"].update(anuncio_id=str(ad.id), titulos_agregados=[h.text for h in ad.responsive_search_ad.headlines],
                                    descripciones_agregadas=[d.text for d in ad.responsive_search_ad.descriptions], urls_despues=list(ad.final_urls))
                f["resumen"] = f"Anuncio activado en «{f['grupo']}» ({len(f['detalle']['titulos_agregados'])} títulos)"
    for f in filas:
        f["detalle"].pop("anuncio_rn", None)

    df = pd.DataFrame(filas)
    if df.empty:
        raise SystemExit(f"Sin cambios entre {desde} y {hasta}.")
    df["marca"] = df["campana"].map(marca_de)
    for m, g in df[df["marca"] != "otros"].groupby("marca"):
        os.makedirs(os.path.join(API, m), exist_ok=True)
        g.assign(detalle=g["detalle"].map(lambda x: json.dumps(x, ensure_ascii=False))).drop(columns="marca").to_csv(
            os.path.join(API, m, f"ads_{m}_cambios_{desde}_{hasta}.csv"), index=False, encoding="utf-8-sig")
    buenas = [f for f, m in zip(filas, df["marca"]) if m != "otros"]
    salida = dict(desde=str(desde), hasta=str(hasta), generado=dt.datetime.now().isoformat(timespec="seconds"), filas=buenas)
    json.dump(salida, open(os.path.join(INF, "datos_cambios_ads.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(buenas)} cambios en {df[df['marca'] != 'otros']['ads_id'].nunique()} campañas, {desde} a {hasta} "
          f"(textos completados: {len(info)}) -> informe/datos_cambios_ads.json")


if __name__ == "__main__":
    main()
