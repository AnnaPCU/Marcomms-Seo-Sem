# -*- coding: utf-8 -*-
"""
meta_export.py — extracción de Meta Ads (Facebook e Instagram) por Marketing API, solo lectura.

Trae todo lo que la API expone, no solo métricas:
  cuentas          estado, moneda, zona horaria, tope de gasto, gastado, motivo de bloqueo
  campanas         objetivo, estado configurado y efectivo, estrategia de puja, presupuesto diario o total,
                   restante, categorías especiales, fechas, problemas (issues_info) y recomendaciones de Meta
  conjuntos        (ad sets) objetivo de optimización, evento de cobro, puja y tope, presupuesto, segmentación
                   completa, objeto promocionado (píxel/evento), atribución, fase de aprendizaje, problemas
  anuncios         estado, motivo de rechazo (ad_review_feedback), creativo completo (textos, enlace, CTA,
                   imagen/video), URL tags
  audiencias       públicos personalizados y similares con tamaño y estado
  pixeles          píxeles con última activación
  actividad        historial de cambios de la cuenta (quién cambió qué y cuándo) desde --desde
  insights_dia     por anuncio y por día: gasto, impresiones, alcance, frecuencia, clics, CTR, CPC, CPM,
                   acciones y costo por acción (una columna por tipo), valores, video y rankings de calidad
  desglose_*       por campaña en el período: edad × sexo, plataforma × ubicación, país y dispositivo

Uso:
  python meta_export.py --probar                     comprueba token, permisos y cuentas visibles
  python meta_export.py --desde 2026-09-01 --hasta 2026-10-30
  python meta_export.py                              por defecto, los últimos 42 días cerrados

Salida: datos/meta/api/<marca>/meta_<marca>_<tabla>_<fecha>.csv + el JSON crudo en datos/meta/api/<marca>/crudo_<fecha>/,
separada por marca según el prefijo del nombre de campaña (CU / PS / PCU): nunca un archivo común. Lo que es de la
cuenta y no de una campaña (cuentas, audiencias, píxeles, cambios sobre objetos sin prefijo) va a la carpeta «cuenta».
Cada corrida suma una línea a datos/meta/api/corridas.jsonl.
"""
import argparse, datetime as dt, json, os
import pandas as pd
from meta_api import Meta, marca_de, ROOT

HOY = dt.date.today()
OUT = os.path.join(ROOT, "datos", "meta", "api")
ESTADOS = ["ACTIVE", "PAUSED", "ARCHIVED", "IN_PROCESS", "WITH_ISSUES", "CAMPAIGN_PAUSED", "ADSET_PAUSED",
           "PENDING_REVIEW", "DISAPPROVED", "PREAPPROVED", "PENDING_BILLING_INFO"]   # todo menos DELETED

F = {
    "cuenta": "id,account_id,name,currency,timezone_name,account_status,disable_reason,amount_spent,spend_cap,"
              "balance,min_daily_budget,business{id,name},created_time",
    "campanas": "id,name,objective,status,configured_status,effective_status,buying_type,bid_strategy,daily_budget,"
                "lifetime_budget,budget_remaining,spend_cap,special_ad_categories,special_ad_category_country,"
                "start_time,stop_time,created_time,updated_time,issues_info,recommendations,pacing_type,"
                "smart_promotion_type,is_budget_schedule_enabled,source_campaign_id",
    "conjuntos": "id,name,campaign_id,status,configured_status,effective_status,optimization_goal,billing_event,"
                 "bid_strategy,bid_amount,bid_constraints,daily_budget,lifetime_budget,budget_remaining,daily_min_spend_target,"
                 "daily_spend_cap,targeting,promoted_object,destination_type,attribution_spec,start_time,end_time,"
                 "pacing_type,learning_stage_info,issues_info,recommendations,frequency_control_specs,is_dynamic_creative,"
                 "dsa_beneficiary,dsa_payor,created_time,updated_time",
    "anuncios": "id,name,adset_id,campaign_id,status,configured_status,effective_status,ad_review_feedback,issues_info,"
                "recommendations,tracking_specs,conversion_specs,preview_shareable_link,created_time,updated_time,"
                "creative{id,name,title,body,link_url,url_tags,call_to_action_type,image_url,image_hash,thumbnail_url,"
                "video_id,object_type,status,object_story_spec,asset_feed_spec,effective_object_story_id,"
                "instagram_permalink_url,degrees_of_freedom_spec}",
    "audiencias": "id,name,subtype,description,approximate_count_lower_bound,approximate_count_upper_bound,"
                  "operation_status,delivery_status,retention_days,rule,lookalike_spec,time_created,time_updated",
    "pixeles": "id,name,last_fired_time,is_unavailable,creation_time,data_use_setting",
    "actividad": "event_time,event_type,translated_event_type,object_id,object_name,object_type,actor_name,extra_data,date_time_in_timezone",
}
INSIGHTS = ("account_currency,campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,objective,optimization_goal,"
            "date_start,date_stop,spend,impressions,reach,frequency,clicks,unique_clicks,inline_link_clicks,"
            "outbound_clicks,ctr,inline_link_click_ctr,cpc,cpm,cpp,actions,action_values,cost_per_action_type,"
            "conversions,conversion_values,cost_per_conversion,video_p25_watched_actions,video_p50_watched_actions,"
            "video_p100_watched_actions,video_thruplay_watched_actions,quality_ranking,engagement_rate_ranking,"
            "conversion_rate_ranking")
DESGLOSES = {"edad_sexo": "age,gender", "plataforma": "publisher_platform,platform_position",
             "pais": "country", "dispositivo": "impression_device"}
CORTOS = "campaign_id,campaign_name,spend,impressions,reach,clicks,inline_link_clicks,ctr,cpc,cpm,actions,cost_per_action_type"


def aplanar_acciones(fila):
    """[{action_type, value}] → columnas acc_<tipo> / cpa_<tipo> / val_<tipo>; el resto de listas y dicts queda en JSON"""
    out = {}
    for k, v in fila.items():
        pref = {"actions": "acc_", "cost_per_action_type": "cpa_", "action_values": "val_", "conversions": "conv_",
                "cost_per_conversion": "cpconv_", "conversion_values": "convval_"}.get(k)
        if pref and isinstance(v, list):
            for a in v:
                out[pref + a.get("action_type", "?")] = float(a.get("value", 0))
        elif k.endswith("_watched_actions") or k == "outbound_clicks":
            out[k] = sum(float(a.get("value", 0)) for a in v) if isinstance(v, list) else v
        else:
            out[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
    return out


def guardar(tabla, filas, campo_nombre, fecha, marca_cuenta):
    """CSV y JSON crudo por marca (nunca un archivo común). La marca sale de la cuenta publicitaria (meta-ads.json
    › cuentas); si la cuenta no está mapeada, del prefijo del nombre. Lo que no se puede asignar va a «cuenta»."""
    if not filas:
        print(f"  [{tabla}] 0 filas"); return
    marcas = [marca_cuenta.get(f.get("cuenta_id") or f.get("id")) or (marca_de(f.get(campo_nombre)) if f.get(campo_nombre) else "cuenta")
              for f in filas]
    marcas = ["cuenta" if m == "otros" else m.lower() for m in marcas]
    df = pd.DataFrame([aplanar_acciones(f) for f in filas])
    df["marca"] = marcas
    for marca in sorted(set(marcas)):
        d = os.path.join(OUT, marca); os.makedirs(os.path.join(d, f"crudo_{fecha}"), exist_ok=True)
        json.dump([f for f, mm in zip(filas, marcas) if mm == marca], open(os.path.join(d, f"crudo_{fecha}", f"{tabla}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        df[df["marca"] == marca].dropna(axis=1, how="all").to_csv(os.path.join(d, f"meta_{marca}_{tabla}_{fecha}.csv"), index=False, encoding="utf-8-sig")
    print(f"  [{tabla}] {len(df):,} filas · " + " ".join(f"{m}={n}" for m, n in df["marca"].value_counts().items()))


def probar(m):
    yo = m.get("me", fields="id,name")
    permisos = [p["permission"] for p in m.todos("me/permissions") if p.get("status") == "granted"]
    print(f"token de: {yo.get('name')} ({yo['id']}) · versión {m.c['version']}")
    print("permisos:", ", ".join(permisos) or "(no se pueden listar con este tipo de token)")
    faltan = {"ads_read"} - set(permisos) if permisos and "ads_management" not in permisos else set()
    if faltan:
        print("  ! falta ads_read o ads_management: no va a poder leer las cuentas")
    for a in m.todos("me/adaccounts", fields="id,name,currency,account_status,amount_spent,business{name}"):
        print(f"  {a['id']}  {a['name']}  · {a.get('currency')} · estado {a.get('account_status')} · "
              f"gastado {a.get('amount_spent')} · portfolio {(a.get('business') or {}).get('name')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probar", action="store_true")
    ap.add_argument("--desde", default=str(HOY - dt.timedelta(days=42)))
    ap.add_argument("--hasta", default=str(HOY - dt.timedelta(days=1)))
    a = ap.parse_args()
    m = Meta()
    if a.probar:
        return probar(m)

    fecha = f"{HOY:%Y%m%d}"
    os.makedirs(OUT, exist_ok=True)
    rango = json.dumps({"since": a.desde, "until": a.hasta})
    filtro = json.dumps([{"field": "effective_status", "operator": "IN", "value": ESTADOS}])
    T = {k: [] for k in ["cuentas", "campanas", "conjuntos", "anuncios", "audiencias", "pixeles", "actividad", "insights_dia"] + [f"desglose_{d}" for d in DESGLOSES]}

    for cuenta in m.cuentas():
        info = m.get(cuenta, fields=F["cuenta"])
        print(f"{cuenta} · {info.get('name')} · {info.get('currency')}")
        T["cuentas"].append(info)
        etiqueta = {"cuenta_id": cuenta, "cuenta_nombre": info.get("name"), "moneda": info.get("currency")}
        camp = m.todos(f"{cuenta}/campaigns", fields=F["campanas"], filtering=filtro)
        nombre_camp = {c["id"]: c["name"] for c in camp}
        T["campanas"] += [{**etiqueta, **c} for c in camp]
        T["conjuntos"] += [{**etiqueta, "campaign_name": nombre_camp.get(s["campaign_id"]), **s}
                           for s in m.todos(f"{cuenta}/adsets", fields=F["conjuntos"], filtering=filtro)]
        T["anuncios"] += [{**etiqueta, "campaign_name": nombre_camp.get(x["campaign_id"]), **x}
                          for x in m.todos(f"{cuenta}/ads", fields=F["anuncios"], filtering=filtro)]
        # audiencias, píxeles y actividad son de la cuenta, no de una campaña: van con el nombre de la cuenta
        for tabla, ruta, extra in (("audiencias", "customaudiences", {}), ("pixeles", "adspixels", {}),
                                   ("actividad", "activities", {"since": a.desde, "until": a.hasta})):
            try:
                T[tabla] += [{**etiqueta, **f} for f in m.todos(f"{cuenta}/{ruta}", fields=F[tabla], **extra)]
            except RuntimeError as ex:
                print(f"  ! {tabla}: {str(ex)[:160]}")
        T["insights_dia"] += [{**etiqueta, **f} for f in m.informe_async(cuenta, level="ad", fields=INSIGHTS, time_range=rango, time_increment=1,
                                                                          use_unified_attribution_setting="true", action_report_time="conversion")]
        for d, br in DESGLOSES.items():
            T[f"desglose_{d}"] += [{**etiqueta, **f} for f in m.todos(f"{cuenta}/insights", level="campaign", fields=CORTOS, breakdowns=br,
                                                                       time_range=rango, use_unified_attribution_setting="true")]

    for tabla, filas in T.items():
        campo = {"campanas": "name", "cuentas": "_", "audiencias": "_", "pixeles": "_", "actividad": "object_name"}.get(tabla, "campaign_name")
        guardar(tabla, filas, campo, fecha, m.c.get("cuentas") or {})
    with open(os.path.join(OUT, "corridas.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"fecha": fecha, "desde": a.desde, "hasta": a.hasta, "corrida": dt.datetime.now().isoformat(timespec="seconds"),
                             "version": m.c["version"], "filas": {k: len(v) for k, v in T.items()}}) + "\n")
    print("->", OUT)


if __name__ == "__main__":
    main()
