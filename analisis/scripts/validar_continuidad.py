# -*- coding: utf-8 -*-
"""
validar_continuidad.py — el histórico nuevo tiene que coincidir con la extracción
de 12 meses (datos/gsc/) en el tramo que se solapa.

Prueba dura:  pages+date sumado sobre cada ventana del baseline == pages del baseline
              (mismas páginas, mismas impresiones, mismos clics, fila por fila).
Prueba blanda: queries+country+date sumado sobre la ventana vs queries+country del
              baseline. No puede ser idéntico: con la dimensión date el umbral de
              anonimización se aplica por día y se pierden queries chicas. Se mide
              cuánto del baseline queda cubierto y que nada del histórico exceda al baseline.
Cobertura:    primera/última fecha y huecos por propiedad.
"""
import pandas as pd
from lib_analisis import *

pd.set_option("display.width", 220)
resultado = []


def marca_(m):
    hp = cargar_hist(m, "pages")
    hq = cargar_hist(m, "queries")
    hd = cargar_hist(m, "daily")
    print(f"\n{'=' * 70}\n{m.upper()}  hist: pages={len(hp):,} queries={len(hq):,} daily={len(hd):,}\n{'=' * 70}")

    # --- cobertura
    print("\nCobertura por propiedad (daily):")
    for prop, g in hd.groupby("property"):
        d = pd.to_datetime(g["date"]).sort_values()
        huecos = d.diff().dt.days
        gaps = [(d.iloc[i - 1].date(), d.iloc[i].date(), int(huecos.iloc[i]) - 1)
                for i in range(1, len(d)) if huecos.iloc[i] > 1]
        print(f"  {prop:<13} {d.min().date()} -> {d.max().date()}  {len(d)} días con datos"
              + (f"  HUECOS: {gaps}" if gaps else ""))
        resultado.append(dict(marca=m, prueba="cobertura", propiedad=prop, primera=str(d.min().date()),
                              ultima=str(d.max().date()), dias=len(d), huecos=str(gaps)))

    # --- daily == suma de pages+date por día? (no: por página cuenta más impresiones) -> se compara con queries no
    for vent, (a, b) in (("12m", VENTANA_12M), ("ads", VENTANA_ADS)):
        print(f"\n--- ventana {vent} {a}..{b}")
        # pages
        bp = cargar_base(m, vent, "pages")
        hpv = hp[(hp["date"] >= a) & (hp["date"] <= b)]
        hpa = agregar(hpv, ["property", "page"])
        mg = bp.merge(hpa, on=["property", "page"], how="outer", suffixes=("_base", "_hist"), indicator=True)
        solo_base = (mg["_merge"] == "left_only").sum()
        solo_hist = (mg["_merge"] == "right_only").sum()
        ambos = mg[mg["_merge"] == "both"]
        dif_imp = (ambos["impressions_base"] != ambos["impressions_hist"]).sum()
        dif_clk = (ambos["clicks_base"] != ambos["clicks_hist"]).sum()
        ok = solo_base == 0 and solo_hist == 0 and dif_imp == 0 and dif_clk == 0
        print(f"  pages   base={len(bp):,} hist={len(hpa):,}  solo_base={solo_base} solo_hist={solo_hist} "
              f"dif_impr={dif_imp} dif_clics={dif_clk}  -> {'IDÉNTICO' if ok else 'DIFIERE'}")
        if not ok:
            print(mg[(mg["_merge"] != "both") | (mg["impressions_base"] != mg["impressions_hist"])]
                  [["property", "page", "impressions_base", "impressions_hist", "clicks_base", "clicks_hist", "_merge"]]
                  .head(15).to_string())
        resultado.append(dict(marca=m, prueba=f"pages_{vent}", filas_base=len(bp), filas_hist=len(hpa),
                              solo_base=int(solo_base), solo_hist=int(solo_hist), dif_impr=int(dif_imp),
                              dif_clics=int(dif_clk), identico=bool(ok)))
        # queries
        bq = cargar_base(m, vent, "queries")
        hqv = hq[(hq["date"] >= a) & (hq["date"] <= b)]
        hqa = agregar(hqv, ["property", "query", "country"])
        mg = bq.merge(hqa, on=["property", "query", "country"], how="outer", suffixes=("_base", "_hist"), indicator=True)
        solo_hist = (mg["_merge"] == "right_only").sum()
        ambos = mg[mg["_merge"] == "both"]
        excede = (ambos["impressions_hist"] > ambos["impressions_base"]).sum()
        cob_filas = len(ambos) / len(bq) * 100
        cob_impr = ambos["impressions_base"].sum() / bq["impressions"].sum() * 100
        cob_clk = ambos["clicks_base"].sum() / bq["clicks"].sum() * 100
        exacto = (ambos["impressions_hist"] == ambos["impressions_base"]).sum()
        print(f"  queries base={len(bq):,} hist={len(hqa):,}  en ambos={len(ambos):,} ({cob_filas:.1f}% filas, "
              f"{cob_impr:.1f}% impr, {cob_clk:.1f}% clics del baseline)  solo_hist={solo_hist}  "
              f"hist>base={excede}  iguales={exacto:,}")
        resultado.append(dict(marca=m, prueba=f"queries_{vent}", filas_base=len(bq), filas_hist=len(hqa),
                              en_ambos=len(ambos), cobertura_filas=round(cob_filas, 1),
                              cobertura_impr=round(cob_impr, 1), cobertura_clics=round(cob_clk, 1),
                              solo_hist=int(solo_hist), hist_excede=int(excede)))
        # totales por propiedad: base pages vs hist daily (agregación distinta: página vs propiedad)
        hdv = hd[(hd["date"] >= a) & (hd["date"] <= b)].groupby("property")[["clicks", "impressions"]].sum()
        bpp = bp.groupby("property")[["clicks", "impressions"]].sum()
        t = bpp.join(hdv, lsuffix="_pages_base", rsuffix="_daily_hist")
        t["ratio_impr"] = (t["impressions_pages_base"] / t["impressions_daily_hist"]).round(3)
        print("  totales por propiedad (pages baseline vs daily hist; difieren por agregación página/propiedad):")
        print(t.to_string())


for m in ("cu", "ps"):
    resultado.clear()
    marca_(m)
    ruta = os.path.join(HIST, m, "validacion_continuidad.csv")
    pd.DataFrame(resultado).to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"\n-> {ruta}")
