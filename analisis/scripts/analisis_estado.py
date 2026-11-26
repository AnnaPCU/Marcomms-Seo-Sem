# -*- coding: utf-8 -*-
"""
analisis_estado.py — estado actual de la cuenta por campaña, antes y después de la auditoría:
gasto diario en las dos ventanas, clics, conversiones, keywords, negativos, si se aplicó lo propuesto,
relación término → anuncio (ventana reciente) y campañas nuevas. Sale a informe/datos_estado.json.
"""
import glob, json, os, re, unicodedata
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
W1, D1 = "2026-08-01_2026-09-11", 42
W2, D2 = "2026-09-12_2026-09-24", 13
EST = sorted(glob.glob(os.path.join(API, "estructura_*")))[-1]
MARCAS = ("cu", "ps", "pcu")


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r'["\[\]]', "", s)).strip()


def load(m, r, w):
    p = os.path.join(API, m, f"ads_{m}_{r}_{w}.csv")
    return pd.read_csv(p, encoding="utf-8-sig") if os.path.exists(p) else pd.DataFrame()


k1 = pd.concat([load(m, "keywords", W1) for m in MARCAS]); k2 = pd.concat([load(m, "keywords", W2) for m in MARCAS])
camp = pd.read_csv(os.path.join(EST, "campanas.csv"), encoding="utf-8-sig")
kw = pd.read_csv(os.path.join(EST, "keywords.csv"), encoding="utf-8-sig"); kw = kw[kw["ad_group_criterion.negative"] != True]
neg = pd.read_csv(os.path.join(EST, "negativos_campana.csv"), encoding="utf-8-sig"); neg["t"] = neg["campaign_criterion.keyword.text"].map(norm)
gr = pd.read_csv(os.path.join(EST, "grupos.csv"), encoding="utf-8-sig")
an = pd.read_csv(os.path.join(EST, "anuncios.csv"), encoding="utf-8-sig")
rel1 = json.load(open(os.path.join(INF, f"datos_relacion_{W1}.json"), encoding="utf-8"))
rel2 = json.load(open(os.path.join(INF, f"datos_relacion_{W2}.json"), encoding="utf-8"))
aud = pd.read_csv(os.path.join(ROOT, "datos", "ads", "Informe de palabras clave de busqueda.csv"), skiprows=2, dtype=str)
aud = aud[aud["Campaña"].notna() & aud["Campaña"].str.match(r"^(CU|PS) ")]
aud_camps = set(aud["Campaña"].str.replace(r"^CU (España|Argentina) - (Competidores )?ISO 27001", r"PCU \1 - \2ISO 27001", regex=True))

# Anexo A: tokens de negativos propuestos por campaña (prefijo)
ANEXO = {"CU España - CAEs": ["vivienda", "particular", "gratis", "ce3x", "certicalia", "online"],
         "CU España - Textile": ["oeko", "organic cotton"], "CU España - IFS": ["servsafe", "curso", "manipulacion", "food handler"],
         "CU España - Forestal": ["rainforest", "medio ambiente"], "CU Canada - Forestry": ["rpf", "forester", "enform", "training", "job", "courses"],
         "CU Canada - Canada Gap": ["supply chain", "indocert", "consultant", "cargill"], "CU United States - Organic - USDA NOP": ["omri", "chicken", "organic land"],
         "PS Argentina - SuSo - Agricultura": ["syngenta", "bayer", "agtech", "tecnologia agricola", "rizobacter", "corteva", "sintropica", "permacultura"],
         "PS Argentina - SuSe - Huella de carbono": ["bonos de carbono", "verra", "carbono neutral", "iso 14001", "creditos de carbono"],
         "PS Argentina - SuSe - Huella de agua": ["tratamiento", "efluentes", "calculadora"], "PS Argentina - Bioenergia": ["biogas", "planta de", "que es"],
         "PS Argentina - SuSe - ESG": ["gri 403", "gri 401", "que es", "verdantix"], "PS Argentina - SuSo - Abastecimiento": ["issa", "logistica verde"],
         "PCU Argentina - ISO 27001": ["nist"], "CU Portugal - Textile": ["wordly", "database"]}
# Anexo B: exactas propuestas por campaña (prefijo)
ANEXO_B = {"CU Canada - Forestry": ["fsc", "fsc certified", "fsc canada"], "PCU Argentina - ISO 27001": ["iso 27001", "iso27001", "norma iso 27001"],
           "PCU España - ISO 27001": ["iso 27001", "certificarse en iso 27001"], "CU España - IFS": ["ifs food", "certificado ifs", "norma ifs"],
           "CU España - Textile": ["certificado gots", "sello gots", "grs global recycled standard"], "CU Portugal - Textile": ["gots", "certificado gots", "grs"],
           "CU España - Bioenergia": ["iscc", "certificado iscc"], "CU Portugal - Bioenergia": ["iscc", "iscc plus"], "CU España - Forestal": ["pefc", "certificacion forestal"],
           "CU Portugal - Forestal": ["pefc", "pefc certification"], "CU España - Smeta": ["smeta", "sedex"], "CU Portugal - Smeta": ["smeta", "smeta 4p"],
           "CU Canada - Smeta": ["smeta", "sedex smeta"], "CU Canada - Canada Gap": ["canada gap", "canadagap"], "CU Canada- Aqua": ["msc certified", "asc seafood certification"],
           "CU Canada - GLOBALG.A.P.": ["ggap"], "CU United States - Organic - USDA NOP": ["national organic program", "certified organic"],
           "CU United States - Organic - PrimusGFS": ["primusgfs", "primus gfs"], "CU España - CAEs": ["sistema de certificados de ahorro energetico", "sujeto delegado cae"],
           "PS Argentina - SuSe - Huella de carbono": ["consultoria ambiental", "iso 14064"], "PS Argentina - SuSe - ESG": ["csrd", "estandar gri", "consultora esg"],
           "PS Argentina - SuSo - Agricultura": ["agricultura regenerativa", "ganaderia regenerativa argentina"], "PS Argentina - SuSe - Huella de agua": ["huella hidrica corporativa", "iso 14046"]}

rel_por_camp = {}
for R in (rel1, rel2):
    for m, v in R["marcas"].items():
        for r in v["por_campana"]:
            rel_por_camp.setdefault(r["campana"], {})[R["ventana"]] = r

filas = []
for _, c in camp.iterrows():
    nombre = c["campaign.name"]
    if c["campaign.status"] == "REMOVED" or c["campaign.advertising_channel_type"] != "SEARCH":
        continue
    g1 = k1[k1["campaign.name"] == nombre]; g2 = k2[k2["campaign.name"] == nombre]
    kws = kw[kw["campaign.name"] == nombre]; act = kws[kws["ad_group_criterion.status"] == "ENABLED"]
    ng = neg[neg["campaign.name"] == nombre]
    pref = next((p for p in ANEXO if nombre.startswith(p)), None)
    anexo_a = None
    if pref:
        toks = ANEXO[pref]; pres = [t for t in toks if ng["t"].str.contains(re.escape(t)).any()]
        anexo_a = dict(propuestos=len(toks), aplicados=len(pres), cuales=pres)
    prefb = next((p for p in ANEXO_B if nombre.startswith(p)), None)
    anexo_b = None
    if prefb:
        ex = set(act.loc[act["ad_group_criterion.keyword.match_type"] == "EXACT", "ad_group_criterion.keyword.text"].map(norm))
        pres = [t for t in ANEXO_B[prefb] if norm(t) in ex]
        anexo_b = dict(propuestas=len(ANEXO_B[prefb]), aplicadas=len(pres), cuales=pres)
    marca = "cu" if nombre.startswith(("CU ", "CU_")) else ("ps" if nombre.startswith(("PS ", "PS_")) else "pcu")
    r1, r2 = rel_por_camp.get(nombre, {}).get(W1), rel_por_camp.get(nombre, {}).get(W2)
    filas.append(dict(
        campana=nombre, marca=marca, estado=c["campaign.status"], presupuesto_dia=round(float(c["campaign_budget.amount_micros"]) / 1e6),
        nueva=nombre not in aud_camps,
        coste_aud=round(float(g1["metrics.coste"].sum())), coste_dia_aud=round(float(g1["metrics.coste"].sum()) / D1),
        clics_aud=int(g1["metrics.clicks"].sum()), conv_aud=float(g1["metrics.conversions"].sum()) if len(g1) else 0,
        coste_post=round(float(g2["metrics.coste"].sum())), coste_dia_post=round(float(g2["metrics.coste"].sum()) / D2),
        clics_post=int(g2["metrics.clicks"].sum()), conv_post=float(g2["metrics.conversions"].sum()) if len(g2) else 0,
        keywords_activas=len(act), keywords_pausadas=int((kws["ad_group_criterion.status"] == "PAUSED").sum()),
        negativos=len(ng), consultant_negativo=bool(ng["t"].str.contains("consult|advisor|asesor").any()),
        grupos=[x for x in gr.loc[gr["campaign.name"] == nombre, "ad_group.name"]],
        anuncios=int((an["campaign.name"] == nombre).sum()),
        anexo_a=anexo_a, anexo_b=anexo_b,
        rel_aud=(dict(pct_nula=r1["pct_nula"], pct_fuerte=r1["pct_fuerte"], score=r1["score_medio"]) if r1 else None),
        rel_post=(dict(pct_nula=r2["pct_nula"], pct_fuerte=r2["pct_fuerte"], score=r2["score_medio"], relev_debajo=r2["relev_debajo"]) if r2 else None)))
df = pd.DataFrame(filas).sort_values("coste_post", ascending=False)
tot = dict(coste_aud=int(df["coste_aud"].sum()), coste_post=int(df["coste_post"].sum()), dia_aud=round(df["coste_aud"].sum() / D1), dia_post=round(df["coste_post"].sum() / D2),
           clics_aud=int(df["clics_aud"].sum()), clics_post=int(df["clics_post"].sum()), conv_aud=float(df["conv_aud"].sum()), conv_post=float(df["conv_post"].sum()),
           nuevas=int(df["nueva"].sum()), campanas=len(df))
out = dict(ventanas=dict(aud=[W1, D1], post=[W2, D2]), totales=tot, campanas=df.to_dict("records"),
           por_marca={m: dict(coste_dia_aud=round(df.loc[df.marca == m, "coste_aud"].sum() / D1), coste_dia_post=round(df.loc[df.marca == m, "coste_post"].sum() / D2),
                             conv_post=float(df.loc[df.marca == m, "conv_post"].sum()), conv_aud=float(df.loc[df.marca == m, "conv_aud"].sum()),
                             relacion_post=rel2["marcas"].get(m, {}).get("por_relacion"), relacion_aud=rel1["marcas"].get(m, {}).get("por_relacion"),
                             peores_post=rel2["marcas"].get(m, {}).get("peores", [])[:6]) for m in MARCAS})
json.dump(out, open(os.path.join(INF, "datos_estado.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
pd.set_option("display.width", 240)
print(df[["campana", "estado", "nueva", "presupuesto_dia", "coste_dia_aud", "coste_dia_post", "conv_post", "keywords_activas", "negativos", "consultant_negativo"]].to_string(index=False))
print("\nTOTALES:", tot)
print("\nAnexo A aplicado:", [(r["campana"][:32], r["anexo_a"]["aplicados"], "/", r["anexo_a"]["propuestos"]) for r in filas if r["anexo_a"]])
print("Anexo B aplicado:", [(r["campana"][:32], r["anexo_b"]["aplicadas"], "/", r["anexo_b"]["propuestas"], r["anexo_b"]["cuales"]) for r in filas if r["anexo_b"] and r["anexo_b"]["aplicadas"]])
print("-> informe/datos_estado.json")
