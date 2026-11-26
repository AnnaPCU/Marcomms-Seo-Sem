# -*- coding: utf-8 -*-
"""
analisis_ejecutivo.py — base de datos para los dos informes cortos:
  informe/datos_clientes.json   por unidad (campañas + orgánico), pain points cuantificados
  informe/datos_seo.json        por propiedad: quick wins, canibalización interna, CTR bajo, pérdidas, móvil

Usa las mismas fuentes que analisis.py (datos/ads, datos/gsc-historico, datos/gsc) y sus CSV de análisis.
"""
import json, os, re
import pandas as pd
from lib_analisis import *

INF = os.path.join(ROOT, "informe")
A, B = VENTANA_ADS
D = json.load(open(os.path.join(INF, "datos_informe.json"), encoding="utf-8"))

kw = cargar_keywords(); kw = kw[kw["marca"] != "?"]
st = cargar_terminos(); st = st[st["marca"] != "?"]
rel = pd.concat([pd.read_csv(os.path.join(HIST, m, "analisis", "cruce_terminos_relevantes.csv"), encoding="utf-8-sig") for m in ("cu", "ps")])
nc = pd.concat([pd.read_csv(os.path.join(HIST, m, "analisis", "demanda_no_comprada.csv"), encoding="utf-8-sig") for m in ("cu", "ps")])
H = {}
for m in ("cu", "ps"):
    H[m] = {c: cargar_hist(m, c) for c in ("queries", "queries_agg", "query_page", "pages", "daily", "device_total", "devices")}
    H[m]["queries"]["mes"] = H[m]["queries"]["date"].str[:7]
props = {"cu": list(H["cu"]["daily"]["property"].unique()), "ps": list(H["ps"]["daily"]["property"].unique())}
marca_de = {p: m for m in props for p in props[m]}


def hist(p, c):
    return H[marca_de[p]][c][H[marca_de[p]][c]["property"] == p]


PAIS_PROP = {"España": ["esp"], "Portugal": ["prt"], "Argentina": ["arg"], "Brasil": ["bra"], "México": ["mex"], "Chile": ["chl"],
             "Perú": ["per"], "Norteamérica": ["can", "usa"], "Américas": ["arg"], "Iberia": ["esp", "prt"]}

# ============================================================ desperdicio por término (misma regla que analisis.py)
from analisis_reglas import es_desperdicio_factory
st["desperdicio"] = es_desperdicio_factory()(st)

# ============================================================ CLIENTES
UNIDADES = [("CU", "España", "esp", "Control Union España"), ("CU", "Portugal", "prt", "Control Union Portugal"),
            ("CU", "Norteamérica", "can", "Control Union Canadá"), ("CU", "Norteamérica", "usa", "Control Union Estados Unidos"),
            ("CU", "Argentina", "arg", "Control Union Argentina"), ("PS", "Américas", "arg", "Peterson Solutions Argentina")]
clientes = []
for marca, prop, pais, nombre in UNIDADES:
    k = kw[(kw["propiedad"] == prop) & (kw["pais"] == pais)]
    s = st[(st["propiedad"] == prop) & (st["pais"] == pais)]
    r = rel[(rel["propiedad"] == prop) & (rel["pais"] == pais)]
    camps = k.groupby("camp_corta").agg(coste=("coste", "sum"), clics=("clics", "sum"), conv=("conv", "sum"),
                                        keywords=("keyword", "count"), sin_impr=("impr", lambda x: int((x == 0).sum()))).reset_index()
    sv = s.groupby("camp_corta").agg(visible=("coste", "sum"), desperdicio=("coste", lambda x: x[s.loc[x.index, "desperdicio"]].sum())).reset_index()
    hv = r[r["grupo"] == "sin nada del tema"].groupby("camp_corta")["coste"].sum().rename("hueco").reset_index()
    camps = camps.merge(sv, on="camp_corta", how="left").merge(hv, on="camp_corta", how="left").fillna(0)
    camps["pct_fuera"] = [round(d / v * 100) if v else None for d, v in zip(camps["desperdicio"], camps["visible"])]
    camps = camps.sort_values("coste", ascending=False)
    # orgánico: ventana ads, país de la campaña
    bq = cargar_base(marca.lower(), "ads", "queries")
    bq = bq[(bq["property"] == prop) & (bq["country"] == pais)]
    qa = hist(prop, "queries_agg"); qa = qa[qa["country"] == pais]
    dev = D["dispositivos"][prop]
    ncp = nc[nc["property"] == prop].sort_values("impressions", ascending=False)
    clientes.append(dict(
        marca=marca, propiedad=prop, pais=pais, nombre=nombre,
        ads=dict(gasto=round(k["coste"].sum()), clics=int(k["clics"].sum()), conv=int(k["conv"].sum()), campanas=int(k["camp_corta"].nunique()),
                 keywords=len(k), sin_impr=int((k["impr"] == 0).sum()), visible=round(s["coste"].sum()),
                 desperdicio=round(s.loc[s["desperdicio"], "coste"].sum()),
                 huecos=round(r.loc[r["grupo"] == "sin nada del tema", "coste"].sum()),
                 huecos_terminos=int((r["grupo"] == "sin nada del tema").sum()),
                 relevante=round(r["coste"].sum()),
                 canib=round(r.loc[r["pos_org"].notna() & (r["pos_org"] < 3.5), "coste"].sum()),
                 zona=r[(r["pos_org"] >= 7.5) & (r["pos_org"] < 20.5)].sort_values("coste", ascending=False)[["termino", "coste", "pos_org", "impr_org"]].head(5).to_dict("records"),
                 cpc=round(k["coste"].sum() / k["clics"].sum()) if k["clics"].sum() else None),
        campanas=camps.to_dict("records"),
        gsc=dict(impr_ads=int(bq["impressions"].sum()), clics_ads=int(bq["clicks"].sum()), queries_ads=int(bq["query"].nunique()),
                 impr_hist=int(qa["impressions"].sum()), clics_hist=int(qa["clicks"].sum()),
                 pos_hist=round(float((qa["position"] * qa["impressions"]).sum() / qa["impressions"].sum()), 1) if len(qa) else None,
                 movil_pct=dev["MOBILE"]["pct_impr"], ctr_movil=dev["MOBILE"]["ctr"], ctr_desk=dev["DESKTOP"]["ctr"],
                 no_comprada=ncp[["query", "impressions", "clicks", "position", "norma"]].head(8).to_dict("records"),
                 no_comprada_n=len(ncp), no_comprada_impr=int(ncp["impressions"].sum()))))

# mercados sin campaña
sin = []
for marca, lista in (("CU", ["Perú", "Brasil", "México", "Chile"]), ("PS", ["Iberia"])):
    for p in lista:
        pan = next(x for x in D["panorama"] if x["propiedad"] == p)
        ncp = nc[nc["property"] == p].sort_values("impressions", ascending=False)
        dev = D["dispositivos"][p]
        sin.append(dict(marca=marca, propiedad=p, impr=pan["impr_total"], clics=pan["clics_total"], impr_ads=pan["impr_ads"], clics_ads=pan["clics_ads"],
                        pos=pan["pos_media_q"], movil_pct=dev["MOBILE"]["pct_impr"],
                        top=ncp[["query", "impressions", "clicks", "position", "norma"]].head(6).to_dict("records"),
                        no_comprada_n=len(ncp), no_comprada_impr=int(ncp["impressions"].sum())))
json.dump(dict(clientes=clientes, sin_campana=sin, ads_total=round(kw["coste"].sum()), ads_clics=int(kw["clics"].sum()), ads_conv=int(kw["conv"].sum())),
          open(os.path.join(INF, "datos_clientes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("clientes ok")
for c in clientes:
    a = c["ads"]; g = c["gsc"]
    print(f"{c['nombre']:<32} gasto {a['gasto']:>9,} clics {a['clics']:>4} conv {a['conv']} | desp {a['desperdicio']:>7,} huecos {a['huecos']:>7,} canib {a['canib']:>6,} | org ads-win impr {g['impr_ads']:>7,} clics {g['clics_ads']:>5} | móvil {g['movil_pct']}% | no comprada {g['no_comprada_n']} q")

# ============================================================ SEO por propiedad
seo = {}
for m in ("cu", "ps"):
    for p in props[m]:
        paises = PAIS_PROP[p]
        qa = hist(p, "queries_agg")
        qp = agregar(qa[qa["country"].isin(paises)], ["query"])                       # país principal
        qp_all = agregar(qa, ["query"])
        qpg = hist(p, "query_page")
        pg = agregar(hist(p, "pages"), ["page"]).sort_values("impressions", ascending=False)
        top_page = qpg.sort_values("impressions", ascending=False).drop_duplicates("query").set_index("query")["page"]
        top_page_pos = qpg.sort_values("impressions", ascending=False).drop_duplicates("query").set_index("query")["position"]
        marca_rx = r"control ?union|peterson|\blogin\b|\bcu\b|\bpcu\b"
        pct_pais_total = round(qp["impressions"].sum() / qp_all["impressions"].sum() * 100) if qp_all["impressions"].sum() else None
        qp = qp[~qp["query"].map(lambda s: bool(re.search(marca_rx, normalizar(s))))]

        def con_pagina(df, n):
            out = []
            for _, r in df.head(n).iterrows():
                pgn = top_page.get(r["query"])
                out.append(dict(query=r["query"], impr=int(r["impressions"]), clics=int(r["clicks"]), pos=float(r["position"]),
                                ctr=round(r["clicks"] / r["impressions"] * 100, 2) if r["impressions"] else 0,
                                page=pgn, page_path=(re.sub(r"^https?://[^/]+", "", pgn) if isinstance(pgn, str) else None),
                                norma=etiquetar_norma(r["query"])))
            return out

        top_q = con_pagina(qp.sort_values("impressions", ascending=False), 10)
        # quick wins: posición 8–15 (redondeada), 150+ impresiones en el país principal
        qw = qp[(qp["position"] >= 7.5) & (qp["position"] < 15.5) & (qp["impressions"] >= 150)].sort_values("impressions", ascending=False)
        quick = con_pagina(qw, 10)
        # zona 16-30 con mucha demanda: necesita contenido, no solo ajuste
        prof = qp[(qp["position"] >= 15.5) & (qp["position"] < 30.5) & (qp["impressions"] >= 300)].sort_values("impressions", ascending=False)
        profundo = con_pagina(prof, 8)
        # canibalización interna: 2+ páginas con ≥20% de las impresiones de la query, 100+ impr
        can_int = []
        for q, g in qpg.groupby("query"):
            tot = g["impressions"].sum()
            if tot < 100 or len(g) < 2:
                continue
            g = g.sort_values("impressions", ascending=False)
            fuertes = g[g["impressions"] >= 0.2 * tot]
            if len(fuertes) >= 2:
                can_int.append(dict(query=q, impr=int(tot), paginas=[dict(path=re.sub(r"^https?://[^/]+", "", r["page"]), impr=int(r["impressions"]), pos=float(r["position"]))
                                                                for _, r in fuertes.head(3).iterrows()]))
        can_int = sorted(can_int, key=lambda x: -x["impr"])[:6]
        # CTR bajo en primera página: páginas con 1.000+ impr, pos ≤ 10, CTR < 0,6%
        pg["ctr_pct"] = (pg["clicks"] / pg["impressions"] * 100).round(2)
        low = pg[(pg["impressions"] >= 1000) & (pg["position"] <= 10) & (pg["ctr_pct"] < 0.6)].sort_values("impressions", ascending=False).head(6)
        low_ctr = [dict(path=re.sub(r"^https?://[^/]+", "", r["page"]), impr=int(r["impressions"]), clics=int(r["clicks"]), pos=float(r["position"]), ctr=float(r["ctr_pct"]))
                   for _, r in low.iterrows()]
        # páginas top por clics
        top_pages = [dict(path=re.sub(r"^https?://[^/]+", "", r["page"]), impr=int(r["impressions"]), clics=int(r["clicks"]), pos=float(r["position"]), ctr=float(r["ctr_pct"]))
                     for _, r in pg.sort_values("clicks", ascending=False).head(6).iterrows()]
        # pérdidas: queries con 300+ impr en el primer tramo y caída ≥70% en el último (mismo largo: 90 días vs 90 días)
        q = hist(p, "queries"); q = q[q["country"].isin(paises)]
        d0, d1 = q["date"].min(), q["date"].max()
        if p in ("Argentina", "México"):
            t1 = q[q["mes"].isin(["2025-06", "2025-07", "2025-08"])]; t2 = q[q["mes"].isin(["2026-06", "2026-07", "2026-08"])]; etiq = ("jun–ago 25", "jun–ago 26")
        else:
            t1 = q[q["date"] < "2026-06-01"]; t2 = q[q["date"] >= "2026-06-16"]; etiq = ("mar–may 26", "jun–sep 26")
        a1 = t1.groupby("query")["impressions"].sum(); a2 = t2.groupby("query")["impressions"].sum()
        comp = pd.DataFrame({"antes": a1, "despues": a2}).fillna(0)
        comp = comp[~comp.index.map(lambda s: bool(re.search(marca_rx, normalizar(s))))]
        perd = comp[(comp["antes"] >= 300) & (comp["despues"] <= 0.3 * comp["antes"])].sort_values("antes", ascending=False).head(6)
        gan = comp[(comp["despues"] >= 300) & (comp["antes"] <= 0.3 * comp["despues"])].sort_values("despues", ascending=False).head(6)
        perdidas = [dict(query=k, antes=int(r["antes"]), despues=int(r["despues"]), page_path=(re.sub(r"^https?://[^/]+", "", top_page[k]) if k in top_page.index else None)) for k, r in perd.iterrows()]
        ganadas = [dict(query=k, antes=int(r["antes"]), despues=int(r["despues"])) for k, r in gan.iterrows()]
        dev = D["dispositivos"][p]
        # demanda sin comprar con página o sin página
        ncp = nc[nc["property"] == p].sort_values("impressions", ascending=False).head(8)
        demanda = []
        for _, r in ncp.iterrows():
            pgn = top_page.get(r["query"])
            demanda.append(dict(query=r["query"], impr=int(r["impressions"]), clics=int(r["clicks"]), pos=float(r["position"]),
                                page_path=(re.sub(r"^https?://[^/]+", "", pgn) if isinstance(pgn, str) else None),
                                pos_page=(float(top_page_pos.get(r["query"])) if r["query"] in top_page_pos.index else None),
                                tiene_pagina=bool(isinstance(pgn, str) and any(t in normalizar(pgn).replace(" ", "-") for t in tokens_tema(r["query"]))),
                                norma=etiquetar_norma(r["query"])))
        pan = next(x for x in D["panorama"] if x["propiedad"] == p)
        seo[p] = dict(marca=m.upper(), paises=paises, tramos=etiq, impr=pan["impr_total"], clics=pan["clics_total"], queries=pan["queries_hist"], pos=pan["pos_media_q"],
                      ctr=round(pan["clics_total"] / pan["impr_total"] * 100, 2), primera=pan["primera"],
                      pct_pais=pct_pais_total,
                      impr_pais_sin_marca=int(qp["impressions"].sum()),
                      top_queries=top_q, quick_wins=quick, profundo=profundo, canibalizacion=can_int, low_ctr=low_ctr, top_pages=top_pages,
                      perdidas=perdidas, ganadas=ganadas, demanda=demanda,
                      movil=dict(pct=dev["MOBILE"]["pct_impr"], ctr_m=dev["MOBILE"]["ctr"], ctr_d=dev["DESKTOP"]["ctr"], pos_m=dev["MOBILE"]["pos"], pos_d=dev["DESKTOP"]["pos"]),
                      paginas_total=int(len(pg)), paginas_con_clic=int((pg["clicks"] > 0).sum()))
        print(f"\n{p}: quick wins {len(quick)} · profundo {len(profundo)} · canib interna {len(can_int)} · ctr bajo {len(low_ctr)} · perdidas {len(perdidas)} · ganadas {len(ganadas)} · páginas {len(pg)} ({(pg['clicks']>0).sum()} con clic)")
        for x in quick[:5]: print(f"   QW {x['query']:<40} impr {x['impr']:>6} pos {x['pos']:.1f} {x['page_path']}")
        for x in can_int[:3]: print(f"   CANIB {x['query']:<35} {x['impr']} -> {[(y['path'][:40], y['impr']) for y in x['paginas']]}")
        for x in low_ctr[:3]: print(f"   LOWCTR {x['path'][:60]:<60} impr {x['impr']} pos {x['pos']:.1f} ctr {x['ctr']}")
        for x in perdidas[:3]: print(f"   PERD {x['query']:<40} {x['antes']} -> {x['despues']}  {x['page_path']}")
        for x in demanda[:4]: print(f"   DEM {x['query']:<30} {x['impr']} pos {x['pos']:.1f} pág={x['tiene_pagina']} {x['page_path']}")
json.dump(seo, open(os.path.join(INF, "datos_seo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\nseo ok")
