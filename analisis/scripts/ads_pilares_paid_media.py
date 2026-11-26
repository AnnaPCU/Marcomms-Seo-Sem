# -*- coding: utf-8 -*-
"""
ads_pilares_paid_media.py — histórico completo de campañas de Google Ads (todas: activas, pausadas y eliminadas,
de cualquier tipo) para cargarlas en MarComms Hub → Pilares → Paid Media (tabla public.campaigns, type = 'paid').

Recorre las dos cuentas (solo lectura):
  · la actual, «Control Union - (en ARG)» (google-ads.cuentas.json → cuentas.principal), en pesos;
  · la anterior, «Peterson Technologies» (→ historicas), en euros.
Una fila por campaña: si la misma campaña existe en las dos cuentas (se migró en jul 2026) se junta en una sola,
con los dos ids y el gasto sumado. Growr y las campañas sin prefijo de marca (Peterson Technologies) no se exportan:
Felipe decidió no cargarlas (22 oct 2026).

El gasto se pasa a dólares con el promedio mensual del tipo de cambio de referencia del BCRA (pesos por USD y por EUR,
API de estadísticas cambiarias), mes por mes, igual que ads_historico.py.

Uso:  python ads_pilares_paid_media.py
Salida: informe/pilares_paid_media/paid_media_google_ads_<cu|ps|pcu>.xlsx   (para revisar; un archivo por marca)
        informe/pilares_paid_media/paid_media_google_ads_<cu|ps|pcu>.json   (mismos datos, para la carga)
"""
import datetime as dt, json, os, re, unicodedata
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from ads_export import CUENTAS, marca_de, aplanar
from ads_historico import cliente, tipo_cambio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "informe", "pilares_paid_media")
HOY = dt.date.today()
AYER = HOY - dt.timedelta(days=1)
SIN_FIN = "2037-12-30"  # Google Ads devuelve esta fecha cuando la campaña no tiene fecha de fin

GAQL_ATTR = """SELECT customer.currency_code, customer.descriptive_name, campaign.id, campaign.name, campaign.status,
  campaign.primary_status, campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
  campaign.start_date_time, campaign.end_date_time, campaign.bidding_strategy_type, campaign_budget.amount_micros
FROM campaign"""
GAQL_DIA = f"""SELECT campaign.id, segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
FROM campaign WHERE segments.date BETWEEN '2015-01-01' AND '{AYER}' AND metrics.impressions > 0"""
GAQL_CRIT = """SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
  campaign_criterion.location.geo_target_constant, campaign_criterion.language.language_constant
FROM campaign_criterion WHERE campaign_criterion.type IN ('LOCATION', 'LANGUAGE')"""
GAQL_GRUPOS = "SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status FROM ad_group WHERE ad_group.status != 'REMOVED'"
GAQL_KW = """SELECT campaign.id, ad_group_criterion.criterion_id FROM ad_group_criterion
WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'"""
GAQL_URL = "SELECT campaign.id, ad_group_ad.ad.final_urls FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"

# valores de país tal como los usa MarComms Hub (campaigns.country)
PAISES = {"argentina": "Argentina", "canada": "Canada", "espana": "España", "spain": "España", "portugal": "Portugal",
          "united states": "Estados Unidos", "us": "Estados Unidos", "usa": "Estados Unidos", "estados unidos": "Estados Unidos",
          "mexico": "Mexico", "brasil": "Brasil", "brazil": "Brasil", "br": "Brasil", "chile": "Chile", "peru": "Peru",
          "paraguay": "Paraguay", "uruguay": "Uruguay", "ar": "Argentina", "ca": "Canada", "es": "España", "pt": "Portugal",
          "mx": "Mexico", "cl": "Chile", "pe": "Peru", "py": "Paraguay", "uy": "Uruguay"}
UNIDAD = {"cu": "Control Union", "ps": "Peterson Solutions", "pcu": "PCU"}
# quién paga, cuando no es la misma unidad y país de la campaña (Felipe, 22 oct 2026: las PCU las paga CU España)
FACTURA_A = {"PCU": dict(unidad="Control Union", pais="España")}
PUJA_OBJETIVO = {"MAXIMIZE_CONVERSIONS": "conversion", "TARGET_CPA": "conversion", "MAXIMIZE_CONVERSION_VALUE": "conversion",
                 "TARGET_ROAS": "conversion", "TARGET_SPEND": "posicionamiento", "TARGET_IMPRESSION_SHARE": "posicionamiento",
                 "MANUAL_CPM": "posicionamiento", "TARGET_CPM": "posicionamiento", "TARGET_CPV": "posicionamiento"}
PUJA_TEXTO = {"TARGET_SPEND": "Maximizar clics", "MAXIMIZE_CONVERSIONS": "Maximizar conversiones", "TARGET_CPA": "CPA objetivo",
              "MAXIMIZE_CONVERSION_VALUE": "Maximizar valor de conversión", "TARGET_ROAS": "ROAS objetivo",
              "TARGET_IMPRESSION_SHARE": "Cuota de impresiones objetivo", "MANUAL_CPC": "CPC manual", "MANUAL_CPM": "CPM manual"}
ESTADO = {"ENABLED": "Activa", "PAUSED": "Pausada", "REMOVED": "Eliminada"}


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def partes(nombre):
    """«CU Canada- Aqua / Fisheries - Search» → ('Canada', 'Aqua / Fisheries'); también «PCU - Argentina - …» y «CU_US_SEARCH_…»"""
    if "_" in nombre and " - " not in nombre:
        t = nombre.split("_")
        return PAISES.get(sin_tildes(t[1]), t[1]) if len(t) > 1 else "", " ".join(t[3:]) or nombre
    t = [x.strip() for x in re.split(r"\s*-\s+|\s+-\s*", nombre) if x.strip()]
    cab = re.sub(r"^(PCU|CU|PS)\b", "", t[0]).strip() if t else ""
    if not cab and len(t) > 1:
        cab, t = t[1], t[1:]
    pais = PAISES.get(sin_tildes(cab), cab)
    resto = [x for x in t[1:] if sin_tildes(x) not in ("search", "pmax", "display", "video")]
    return pais, " / ".join(resto)


def consulta(cli, cid, q):
    svc = cli.get_service("GoogleAdsService")
    return [aplanar(r) for b in svc.search_stream(customer_id=cid, query=q) for r in b.results]


def nombres(cli, cid, recursos, tabla):
    if not recursos:
        return {}
    lista = ", ".join(f"'{r}'" for r in sorted(recursos))
    campo = "name"
    filas = consulta(cli, cid, f"SELECT {tabla}.resource_name, {tabla}.{campo} FROM {tabla} WHERE {tabla}.resource_name IN ({lista})")
    return {f[f"{tabla}.resource_name"]: f[f"{tabla}.{campo}"] for f in filas}


def leer_cuenta(c):
    cli, cid = cliente(c.get("login")), c["id"]
    attr = consulta(cli, cid, GAQL_ATTR)
    dia = consulta(cli, cid, GAQL_DIA)
    crit = consulta(cli, cid, GAQL_CRIT)
    grupos = consulta(cli, cid, GAQL_GRUPOS)
    kws = consulta(cli, cid, GAQL_KW)
    urls = consulta(cli, cid, GAQL_URL)
    geo = nombres(cli, cid, {x["campaign_criterion.location.geo_target_constant"] for x in crit
                             if x.get("campaign_criterion.location.geo_target_constant")}, "geo_target_constant")
    idi = nombres(cli, cid, {x["campaign_criterion.language.language_constant"] for x in crit
                             if x.get("campaign_criterion.language.language_constant")}, "language_constant")
    moneda = attr[0]["customer.currency_code"] if attr else "ARS"
    camp = {}
    for a in attr:
        k = str(a["campaign.id"])
        camp[k] = dict(cuenta=c["cuenta"], cuenta_id=cid, cuenta_nombre=a["customer.descriptive_name"], moneda=moneda, ads_id=k,
                       nombre=a["campaign.name"], estado=a["campaign.status"], estado_detalle=a.get("campaign.primary_status", ""),
                       tipo=a["campaign.advertising_channel_type"], subtipo=a.get("campaign.advertising_channel_sub_type", ""),
                       inicio=str(a.get("campaign.start_date_time", ""))[:10], fin=str(a.get("campaign.end_date_time", ""))[:10],
                       puja=a.get("campaign.bidding_strategy_type", ""),
                       presupuesto_diario=float(a.get("campaign_budget.amount_micros") or 0) / 1e6,
                       ubicaciones=[], excluidas=[], idiomas=[], grupos=[], keywords=0, urls=set())
    for x in crit:
        k = str(x["campaign.id"])
        if k not in camp:
            continue
        if x.get("campaign_criterion.location.geo_target_constant"):
            n = geo.get(x["campaign_criterion.location.geo_target_constant"], x["campaign_criterion.location.geo_target_constant"])
            camp[k]["excluidas" if str(x.get("campaign_criterion.negative")) == "True" else "ubicaciones"].append(n)
        elif x.get("campaign_criterion.language.language_constant"):
            camp[k]["idiomas"].append(idi.get(x["campaign_criterion.language.language_constant"], ""))
    for g in grupos:
        if str(g["campaign.id"]) in camp:
            camp[str(g["campaign.id"])]["grupos"].append(g["ad_group.name"])
    for w in kws:
        if str(w["campaign.id"]) in camp:
            camp[str(w["campaign.id"])]["keywords"] += 1
    for u in urls:
        if str(u["campaign.id"]) in camp:
            for url in str(u.get("ad_group_ad.ad.final_urls") or "").split(" | "):
                if url.startswith("http"):
                    camp[str(u["campaign.id"])]["urls"].add(url.split("?")[0])
    d = pd.DataFrame(dia)
    if not d.empty:
        d = pd.DataFrame(dict(ads_id=d["campaign.id"].astype(str), fecha=d["segments.date"].astype(str),
                              coste=pd.to_numeric(d["metrics.cost_micros"]).fillna(0) / 1e6,
                              clics=pd.to_numeric(d["metrics.clicks"]).fillna(0).astype(int),
                              impresiones=pd.to_numeric(d["metrics.impressions"]).fillna(0).astype(int),
                              conversiones=pd.to_numeric(d["metrics.conversions"]).fillna(0)))
        d["moneda"], d["cuenta"] = moneda, c["cuenta"]
    print(f"{c['nombre']} ({cid}, {moneda}): {len(camp)} campañas, {len(d)} campaña-día con impresiones")
    return camp, d


def main():
    os.makedirs(OUT, exist_ok=True)
    cuentas = [dict(id=CUENTAS["cuentas"]["principal"], login=None, cuenta="actual", nombre="Control Union - (en ARG)")] + CUENTAS.get("historicas", [])
    camp, dias = {}, []
    for c in cuentas:
        cc, dd = leer_cuenta(c)
        camp.update({f"{c['cuenta']}:{k}": v for k, v in cc.items()})
        if not dd.empty:
            dd["clave"] = c["cuenta"] + ":" + dd["ads_id"]
            dias.append(dd)
    dia = pd.concat(dias, ignore_index=True)
    dia["mes"] = dia["fecha"].str[:7]

    # tipo de cambio: pesos por USD y por EUR, promedio del mes (BCRA)
    meses = set(dia["mes"])
    tc = {m: tipo_cambio(m, meses) for m in {"USD"} | (set(dia["moneda"]) - {"ARS"})}
    a_usd = lambda moneda, mes: (1.0 if moneda == "ARS" else tc[moneda][mes]["promedio"]) / tc["USD"][mes]["promedio"]
    dia["usd_por_unidad"] = [a_usd(m, mes) for m, mes in zip(dia["moneda"], dia["mes"])]
    dia["coste_usd"] = dia["coste"] * dia["usd_por_unidad"]

    # una fila por campaña: se juntan las que tienen el mismo nombre en las dos cuentas
    for k, v in camp.items():
        v["grupo_clave"] = re.sub(r"\s+", " ", sin_tildes(v["nombre"]))
    filas, revisar, mensual = [], [], []
    por_nombre = {}
    for k, v in camp.items():
        por_nombre.setdefault(v["grupo_clave"], []).append((k, v))
    for _, lista in sorted(por_nombre.items()):
        claves = [k for k, _ in lista]
        vs = [v for _, v in lista]
        actual = next((v for v in vs if v["cuenta"] == "actual"), vs[0])
        dd = dia[dia["clave"].isin(claves)]
        con_datos = not dd.empty
        primero = dd["fecha"].min() if con_datos else ""
        ultimo = dd["fecha"].max() if con_datos else ""
        coste_usd = round(float(dd["coste_usd"].sum()), 2)
        clics, impr, conv = int(dd["clics"].sum()), int(dd["impresiones"].sum()), round(float(dd["conversiones"].sum()), 2)
        orig = {m: round(float(g["coste"].sum()), 2) for m, g in dd.groupby("moneda")}
        marca = marca_de(actual["nombre"])
        pais, tema = partes(actual["nombre"])
        fin = actual["fin"] if actual["fin"] and actual["fin"] != SIN_FIN else ""
        activa = actual["estado"] == "ENABLED" and (not fin or fin >= str(HOY))
        estado = ESTADO.get(actual["estado"], actual["estado"])
        if actual["estado"] == "ENABLED" and fin and fin < str(HOY):
            estado = "Finalizada"
        if not con_datos:
            estado += " · nunca publicada"
        dias_total = (dt.date.fromisoformat(ultimo) - dt.date.fromisoformat(primero)).days + 1 if con_datos else 0
        if activa and not fin:
            duracion = f"Sin fecha de fin · desde {primero or actual['inicio']}"
        elif con_datos:
            duracion = f"{dias_total} días · {primero} a {ultimo}"
        else:
            duracion = ""
        one_shot = bool(fin) or bool(re.search(r"\b(event|evento|feria|expo|show)\b", actual["nombre"], re.I))
        objetivo = PUJA_OBJETIVO.get(actual["puja"], "")
        ubic = sorted(set(sum((v["ubicaciones"] for v in vs if v is actual), [])))
        idiomas = sorted({i for i in actual["idiomas"] if i})
        urls = sorted(set().union(*[v["urls"] for v in vs]))
        grupos = sorted(set(actual["grupos"]))
        tipo_txt = actual["tipo"].replace("_", " ").title().replace("Performance Max", "Performance Max")
        presup = f"{actual['presupuesto_diario']:,.0f} {actual['moneda']}/día".replace(",", ".") if actual["presupuesto_diario"] else "s/d"
        detalle = " · ".join(x for x in [
            f"Google Ads {tipo_txt}" + (f" ({tema})" if tema else ""),
            f"Puja: {PUJA_TEXTO.get(actual['puja'], actual['puja'].replace('_', ' ').lower())}",
            f"Presupuesto: {presup}",
            ("Ubicaciones: " + ", ".join(ubic)) if ubic else "",
            ("Idiomas: " + ", ".join(idiomas)) if idiomas else "",
            f"{len(grupos)} grupos de anuncios, {actual['keywords']} keywords" if grupos else "",
            ("Landing: " + ", ".join(urls[:3]) + (f" (+{len(urls) - 3})" if len(urls) > 3 else "")) if urls else "",
            "Cuentas: " + ", ".join(f"{v['cuenta_nombre']} ({v['cuenta_id']}) id {v['ads_id']}" for v in vs),
        ] if x)
        fila = dict(
            nombre_campana=actual["nombre"], pais=pais, unidad=UNIDAD.get(marca, ""), marca_ads=marca.upper(), tema=tema,
            facturar_a=" ".join(FACTURA_A[marca.upper()].values()) if marca.upper() in FACTURA_A else "",
            estado_ads=estado, plataformas="google", tipo_campana=tipo_txt,
            modalidad="one_shot" if one_shot else "always_on", modalidad_inferida="sí",
            objetivo=objetivo, objetivo_inferido="sí (por la estrategia de puja)" if objetivo else "no se pudo inferir",
            estrategia_puja=PUJA_TEXTO.get(actual["puja"], actual["puja"]),
            inversion_oficina_usd=coste_usd, duracion=duracion, fecha_inicio=primero or actual["inicio"], fecha_fin=ultimo if not activa else "",
            primer_dia_con_impresiones=primero, ultimo_dia_con_impresiones=ultimo, dias_con_datos=int(dd["fecha"].nunique()),
            detalle_brief=detalle,
            paso_brief_creatividades=True, paso_piezas_subidas=True, paso_campana_lanzada=con_datos,
            completada=bool(con_datos and not activa), completed_at=ultimo if (con_datos and not activa) else "",
            impresiones=impr, clics=clics, ctr_pct=round(clics / impr * 100, 2) if impr else None,
            cpc_usd=round(coste_usd / clics, 2) if clics else None, conversiones=conv,
            cpl_usd=round(coste_usd / conv, 2) if conv else None,
            gasto_ars=orig.get("ARS"), gasto_eur=orig.get("EUR"),
            presupuesto_diario=actual["presupuesto_diario"], moneda_presupuesto=actual["moneda"],
            ubicaciones=", ".join(ubic), ubicaciones_excluidas=", ".join(sorted(set(actual["excluidas"]))), idiomas=", ".join(idiomas),
            grupos_de_anuncios=" | ".join(grupos), cantidad_keywords=actual["keywords"], landings=" | ".join(urls),
            ads_ids=", ".join(f"{v['cuenta_id']}:{v['ads_id']}" for v in vs),
            clave_externa="gads:" + "+".join(sorted(f"{v['cuenta_id']}:{v['ads_id']}" for v in vs)),
            # campos que Google Ads no tiene: los completa el equipo en la herramienta
            fee_marcomms=None, moneda_fee=None, responsable=None, ticket_hubspot=None, deals_hubspot=None,
        )
        (revisar if marca == "otros" else filas).append(fila)  # «otros» = Growr y Peterson Technologies: no se exportan
        for (mes, moneda), g in dd.groupby(["mes", "moneda"]):
            mensual.append(dict(nombre_campana=actual["nombre"], clave_externa=fila["clave_externa"], mes=mes, moneda_original=moneda,
                                gasto_original=round(float(g["coste"].sum()), 2), usd_por_unidad=round(float(g["usd_por_unidad"].iloc[0]), 6),
                                gasto_usd=round(float(g["coste_usd"].sum()), 2), impresiones=int(g["impresiones"].sum()),
                                clics=int(g["clics"].sum()), conversiones=round(float(g["conversiones"].sum()), 2),
                                incluida="no (Revisar)" if marca == "otros" else "sí"))

    df = pd.DataFrame(filas).sort_values(["unidad", "pais", "fecha_inicio", "nombre_campana"])
    rv = pd.DataFrame(revisar)
    if not rv.empty:
        rv = rv.sort_values(["fecha_inicio", "nombre_campana"])
    mm = pd.DataFrame(mensual).sort_values(["nombre_campana", "mes"])
    tcf = pd.DataFrame([dict(mes=m, moneda=mon, pesos_por_unidad=v["promedio"], dias_habiles=v["dias"])
                        for mon, t in tc.items() for m, v in sorted(t.items())])

    generado = dt.datetime.now().isoformat(timespec="seconds")
    # regla del proyecto: los datos de cada marca van en archivos separados, nunca en uno común
    lotes = {m: df[df["marca_ads"] == m.upper()] for m in ("cu", "ps", "pcu")}
    # Growr y las campañas sin prefijo de marca (Peterson Technologies) no se cargan: decisión de Felipe, 22 oct 2026
    for m, d in lotes.items():
        if d.empty:
            continue
        dm = mm[mm["clave_externa"].isin(d["clave_externa"])]
        sin_publicar = d[~d["paso_campana_lanzada"].astype(bool)]
        d = d[d["paso_campana_lanzada"].astype(bool)]
        base = os.path.join(OUT, f"paid_media_google_ads_{m}")
        json.dump(dict(generado=generado, marca=m.upper(), fuente="Google Ads API (solo lectura), cuentas " + ", ".join(c["id"] for c in cuentas),
                       tipo_cambio="BCRA, promedio mensual de pesos por USD/EUR; gasto en USD convertido mes a mes",
                       campanas=[dict(r, hub=hub(r)) for r in json.loads(d.to_json(orient="records", force_ascii=False))],
                       mensual=json.loads(dm.to_json(orient="records", force_ascii=False))),
                  open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with pd.ExcelWriter(base + ".xlsx", engine="openpyxl") as xw:
            leeme(xw, d, m, generado, cuentas)
            d.to_excel(xw, sheet_name="Paid Media", index=False)
            dm.to_excel(xw, sheet_name="Mensual", index=False)
            if not sin_publicar.empty:
                sin_publicar.to_excel(xw, sheet_name="No publicadas", index=False)
            tcf[tcf["mes"].isin(dm["mes"])].to_excel(xw, sheet_name="Tipo de cambio", index=False)
            for nombre, ws in xw.sheets.items():
                if nombre == "Léeme":
                    continue
                for cel in ws[1]:
                    cel.font, cel.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1B1E42")
                    cel.alignment = Alignment(wrap_text=True, vertical="center")
                ws.freeze_panes, ws.auto_filter.ref = "B2", ws.dimensions
                for i, col in enumerate(ws.columns, 1):
                    largo = max(len(str(c.value or "")) for c in list(col)[:200])
                    ws.column_dimensions[get_column_letter(i)].width = min(max(10, largo + 2), 60)
        print(f"{m.upper()}: {len(d)} campañas, {d['inversion_oficina_usd'].sum():,.2f} USD -> {base}.xlsx")
    print(df.groupby(["unidad", "pais"]).agg(campanas=("nombre_campana", "count"), usd=("inversion_oficina_usd", "sum")).to_string())



def hub(r):
    """fila lista para public.campaigns de MarComms Hub (mismos nombres y valores que usa src/services/campaignsService.js)"""
    pasos = ["brief", "creativities"] + (["launch"] if r["paso_campana_lanzada"] else [])
    return dict(
        type="paid", name=r["nombre_campana"], country=r["pais"], business_unit=r["unidad"],
        platform_investment=r["inversion_oficina_usd"], completed_steps=pasos, completed_at=r["completed_at"] or None,
        data=dict(facturar_a=FACTURA_A.get(r["marca_ads"], dict(unidad=r["unidad"], pais=r["pais"])),
                  platforms=["google"], paidMode=r["modalidad"], duration=r["duracion"], objective=r["objetivo"], detail=r["detalle_brief"],
                  google_ads=dict(clave_externa=r["clave_externa"], ids=r["ads_ids"].split(", "), estado=r["estado_ads"], tipo=r["tipo_campana"],
                                  estrategia_puja=r["estrategia_puja"], primer_dia=r["primer_dia_con_impresiones"],
                                  ultimo_dia=r["ultimo_dia_con_impresiones"], landings=r["landings"].split(" | ") if r["landings"] else [],
                                  resultados=dict(impresiones=r["impresiones"], clics=r["clics"], ctr_pct=r["ctr_pct"], cpc_usd=r["cpc_usd"],
                                                  conversiones=r["conversiones"], cpl_usd=r["cpl_usd"]),
                                  gasto_original={k: v for k, v in (("ARS", r["gasto_ars"]), ("EUR", r["gasto_eur"])) if v},
                                  fuente="Google Ads API", extraido=dt.date.today().isoformat())),
    )


def leeme(xw, df, marca, generado, cuentas):
    titulo = {"cu": "Control Union", "ps": "Peterson Solutions", "pcu": "PCU (ISO 27001) · lo paga Control Union España"}[marca]
    t = [
        [f"Histórico de campañas de Google Ads para MarComms Hub → Pilares → Paid Media · {titulo}"],
        [f"Generado {generado} desde la API de Google Ads (solo lectura) · cuentas " + ", ".join(f"{c['nombre']} ({c['id']})" for c in cuentas)],
        [f"{len(df)} campañas · {df['inversion_oficina_usd'].sum():,.2f} USD de inversión total"],
        [""],
        ["Hojas"],
        ["Paid Media", "Una fila = un registro de Paid Media en la herramienta. Si la campaña existe en las dos cuentas (migración jul 2026) va una sola fila con el gasto sumado."],
        ["Mensual", "Gasto, impresiones, clics y conversiones por campaña y mes, con la moneda original y el factor a USD."],
        ["No publicadas", "Campañas creadas en Google Ads que nunca tuvieron impresiones: NO se cargan."],
        ["Tipo de cambio", "Promedio mensual BCRA (pesos por USD y por EUR) usado para pasar el gasto a dólares."],
        [""],
        ["Columna", "Campo en la herramienta", "Columna en Supabase (public.campaigns)", "Nota"],
        ["nombre_campana", "Nombre de la campaña", "name", "Nombre exacto en Google Ads"],
        ["pais", "País", "country", "Sacado del nombre; valores como los usa la herramienta (Argentina, Canada, España, Portugal, Estados Unidos…)"],
        ["unidad", "Unidad", "business_unit", "CU → Control Union; PS → Peterson Solutions; PCU → PCU"],
        ["facturar_a", "Quién paga", "data.facturar_a", "Vacío = la misma unidad y país; PCU → Control Union España"],
        ["plataformas", "Plataformas", "data.platforms", "Siempre ['google']"],
        ["modalidad", "Modalidad (opcional)", "(ver código de la app)", "always_on / one_shot · INFERIDA: one_shot si tiene fecha de fin o es de evento"],
        ["inversion_oficina_usd", "Inversión oficina (USD)", "platform_investment", "Gasto real total en USD"],
        ["duracion", "Duración", "data.duration", "Texto libre"],
        ["objetivo", "Objetivo", "data.objective", "posicionamiento / conversion · INFERIDO de la estrategia de puja"],
        ["detalle_brief", "Detalle / Brief", "data.detail", "Resumen técnico de la campaña"],
        ["paso_*", "Ejecución (3 pasos)", "completed_steps", "Brief y creatividades / Piezas subidas / Campaña lanzada"],
        ["impresiones … cpl_usd", "Resultados", "report", "Alcance no existe en Search: queda vacío"],
        ["completed_at", "Campaña cerrada", "completed_at", "Último día con impresiones, solo si ya no está activa"],
        ["clave_externa", "—", "(dónde la guarde la app, p. ej. data.google_ads_ids)", "Clave estable para no duplicar si se vuelve a cargar"],
        ["fee_marcomms, moneda_fee, responsable, ticket_hubspot, deals_hubspot", "Fee, Responsable, Ticket HubSpot, Deals", "budget, billing, service_owner, hubspot_link, deals_created", "Google Ads no los tiene: quedan vacíos para completar a mano"],
    ]
    pd.DataFrame(t).to_excel(xw, sheet_name="Léeme", index=False, header=False)
    ws = xw.sheets["Léeme"]
    ws["A1"].font = Font(bold=True, size=14, color="1B1E42")
    for r in (5, 11):
        for c in ws[r]:
            c.font = Font(bold=True)
    for col, w in zip("ABCD", (34, 40, 48, 90)):
        ws.column_dimensions[col].width = w


if __name__ == "__main__":
    main()
