# -*- coding: utf-8 -*-
"""
analisis_trafico_landings.py — cuánto tráfico reciben las landings de industrias y de programas de certificación
de cada sitio de Control Union, comparado con las landings principales (home, nosotros, industrias, programas,
academy, vacantes, contacto, servicios, certificaciones, gestión de garantías, inspecciones de commodities)
y con el resto del sitio.

Entradas: informe/datos_ga4_paginas.json (ga4_paginas.py) y datos/landings/<sitio>.<tipo>.txt (sitemaps, 22 oct 2026).
Salida:   informe/trafico_landings.json y .md
"""
import json, os, re, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITIOS = ["northamerica", "espana", "peru", "argentina", "portugal", "brasil", "mexico", "chile"]
NOMBRE = {"northamerica": "Norteamérica", "espana": "España", "peru": "Perú", "argentina": "Argentina",
          "portugal": "Portugal", "brasil": "Brasil", "mexico": "México", "chile": "Chile"}
GRUPOS = {"1 · NA + España + Perú": ["northamerica", "espana", "peru"],
          "2 · Argentina + Portugal + Brasil": ["argentina", "portugal", "brasil"],
          "3 · México + Chile": ["mexico", "chile"]}

# landings principales: una ruta por rol y por sitio (idioma local), elegida por patrón sobre las rutas con tráfico
PRINCIPALES = {
    "home": r"^/$",
    "nosotros": r"^/(about-us|nosotros|sobre-nos|sobre-nosotros|quienes-somos|quem-somos)$",
    "industrias (hub)": r"^/(industries|industrias)$",
    "programas (hub)": r"^/(certification-programs|programas-de-certificacion|esquemas-de-certificacao|programas-de-certificacao)$",
    "academy": r"^/(academy|academy-home)$",
    "vacantes": r"^/(vacancies|vacantes|vagas|vacantes-chile|careers|carreiras)$",
    "contacto": r"^/(contact|contacto|contato|contacto-mexico|contact-us)$",
    "servicios (hub)": r"^/(services|servicios|servicos|soluciones|solutions)$",
    "certificaciones": r"^/(service/(certification|certificaciones|certificacoes)|certificacoes)$",  # Portugal: /certificacoes es la viva, /service/certification quedó huérfana
    "gestión de garantías": r"^/(service/(collateral-management|gestion-de-garantias|gestao-de-garantias)|servicios-garantias|servicios-cma)$",
    "inspecciones de commodities": r"^/service/(commodity-inspections|inspecciones-de-commodities|servicos/inspeccoes)$",
}


def norm(ruta):
    ruta = ruta.split("?")[0].strip().lower()
    ruta = re.sub(r"/+", "/", ruta)
    return ruta.rstrip("/") or "/"


def sitemap(sitio, tipo):
    out = {"local": set(), "en": set(), "otro": set()}
    for linea in open(os.path.join(ROOT, "datos", "landings", f"{sitio}.{tipo}.txt"), encoding="utf-8"):
        u = linea.strip()
        if not u:
            continue
        p = norm(u.split(".controlunion.com", 1)[1])
        if p.startswith("/en/"):
            out["en"].add(p)
        elif p.startswith("/es/es/") or p.startswith("/pt-pt/"):
            out["otro"].add(p)
        else:
            out["local"].add(p)
    return out


def main():
    datos = json.load(open(os.path.join(ROOT, "informe", "datos_ga4_paginas.json"), encoding="utf-8"))
    meses = datos["dias"] / 30.44
    resultado = {"periodo": f"{datos['desde']} a {datos['hasta']}", "dias": datos["dias"], "meses": round(meses, 2), "sitios": {}}
    md = [f"# Tráfico de landings de industrias y programas · Control Union\n",
          f"Período GA4: {datos['desde']} a {datos['hasta']} ({datos['dias']} días = {meses:.1f} meses). Métrica: vistas de página (screenPageViews), "
          f"expresadas en vistas por mes. Las landings se identifican por el sitemap del 22 oct 2026.\n"]

    for sitio in SITIOS:
        host = f"{sitio}.controlunion.com"
        filas = datos["sitios"][host]
        vistas = {}
        for f in filas:
            r = norm(f["ruta"])
            vistas[r] = vistas.get(r, 0) + f["vistas"]
        ind, prg = sitemap(sitio, "industry"), sitemap(sitio, "certi_program")
        v = lambda r: vistas.get(r, 0) / meses

        principales = {}
        for rol, pat in PRINCIPALES.items():
            cand = sorted([r for r in set(vistas) | ind["local"] | prg["local"] if re.match(pat, r)], key=lambda r: -vistas.get(r, 0))
            if cand:
                principales[rol] = {"ruta": cand[0], "vistas_mes": round(v(cand[0]), 1)}
        prom_princ = st.mean(p["vistas_mes"] for p in principales.values())
        prom_princ_sin_home = st.mean(p["vistas_mes"] for rol, p in principales.items() if rol != "home")

        def grupo(rutas):
            vals = sorted((v(r) for r in rutas), reverse=True)
            if not vals:
                return {}
            total = sum(vals)
            return {"paginas": len(vals), "total_mes": round(total, 1), "promedio": round(total / len(vals), 2),
                    "mediana": round(st.median(vals), 2), "max": round(vals[0], 1),
                    "con_0_vistas": sum(1 for x in vals if x == 0),
                    "menos_1_mes": sum(1 for x in vals if x < 1), "1_a_5_mes": sum(1 for x in vals if 1 <= x < 5),
                    "5_a_20_mes": sum(1 for x in vals if 5 <= x < 20), "20_o_mas_mes": sum(1 for x in vals if x >= 20),
                    "top": [(r, round(v(r), 1)) for r in sorted(rutas, key=lambda r: -vistas.get(r, 0))[:5]]}

        total_sitio = sum(vistas.values()) / meses
        todas = sorted((x / meses for x in vistas.values()), reverse=True)
        mediana_sitio = st.median(todas)
        # resto del sitio: todas las rutas con tráfico que no son principales, ni industrias ni programas (en ningún idioma)
        excl = set(p["ruta"] for p in principales.values()) | ind["local"] | ind["en"] | ind["otro"] | prg["local"] | prg["en"] | prg["otro"]
        resto = [v(r) for r in vistas if r not in excl]

        g_ind, g_prg = grupo(ind["local"]), grupo(prg["local"])
        g_ind_en, g_prg_en = grupo(ind["en"]), grupo(prg["en"])
        s = {"nombre": NOMBRE[sitio], "vistas_mes_sitio": round(total_sitio, 1), "rutas_con_trafico": len(vistas),
             "mediana_sitio": round(mediana_sitio, 2),
             "principales": principales, "promedio_principales": round(prom_princ, 1), "promedio_principales_sin_home": round(prom_princ_sin_home, 1),
             "industrias": g_ind, "programas": g_prg, "industrias_en": g_ind_en, "programas_en": g_prg_en,
             "resto": {"paginas": len(resto), "promedio": round(st.mean(resto), 2) if resto else 0, "mediana": round(st.median(resto), 2) if resto else 0},
             "participacion": {"industrias": round(100 * g_ind["total_mes"] / total_sitio, 1), "programas": round(100 * g_prg["total_mes"] / total_sitio, 1),
                               "industrias_en": round(100 * g_ind_en["total_mes"] / total_sitio, 1) if g_ind_en else 0,
                               "programas_en": round(100 * g_prg_en["total_mes"] / total_sitio, 1) if g_prg_en else 0,
                               "principales": round(100 * sum(p["vistas_mes"] for p in principales.values()) / total_sitio, 1)}}
        resultado["sitios"][sitio] = s

        md.append(f"\n## {NOMBRE[sitio]} · {total_sitio:,.0f} vistas/mes en {len(vistas)} rutas\n")
        md.append("| Landing principal | Ruta | Vistas/mes |\n|---|---|---:|")
        for rol, p in principales.items():
            md.append(f"| {rol} | `{p['ruta']}` | {p['vistas_mes']:.1f} |")
        md.append(f"| **promedio principales** | | **{prom_princ:.1f}** |\n| promedio sin home | | {prom_princ_sin_home:.1f} |\n")
        md.append("| Grupo | Páginas | Vistas/mes total | Prom. por página | Mediana | Máx. | <1/mes | 1–5 | 5–20 | ≥20 | % del sitio |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for et, g, k in (("Industrias (idioma local)", g_ind, "industrias"), ("Programas (idioma local)", g_prg, "programas"),
                         ("Industrias /en/", g_ind_en, "industrias_en"), ("Programas /en/", g_prg_en, "programas_en")):
            if g:
                md.append(f"| {et} | {g['paginas']} | {g['total_mes']:.1f} | {g['promedio']:.2f} | {g['mediana']:.2f} | {g['max']:.1f} | {g['menos_1_mes']} | {g['1_a_5_mes']} | {g['5_a_20_mes']} | {g['20_o_mas_mes']} | {s['participacion'][k]:.1f}% |")
        md.append(f"| Resto del sitio | {len(resto)} | {sum(resto):.1f} | {st.mean(resto):.2f} | {st.median(resto):.2f} | | | | | | |\n")
        md.append("Top 5 industrias: " + " · ".join(f"`{r}` {x:.1f}" for r, x in g_ind["top"]))
        md.append("\nTop 5 programas: " + " · ".join(f"`{r}` {x:.1f}" for r, x in g_prg["top"]))

    # grupos pedidos
    md.append("\n\n## Resumen por grupo (idioma local; vistas/mes)\n")
    md.append("| Grupo | Sitio | Prom. principales | Industrias: prom/pág · mediana · total | Programas: prom/pág · mediana · total | Ind. ≥5/mes | Prog. ≥5/mes |\n|---|---|---:|---|---|---:|---:|")
    resultado["grupos"] = {}
    for gn, lista in GRUPOS.items():
        acc = {"principales": [], "ind": [], "prg": []}
        for sitio in lista:
            s = resultado["sitios"][sitio]
            gi, gp = s["industrias"], s["programas"]
            md.append(f"| {gn} | {s['nombre']} | {s['promedio_principales']:.0f} | {gi['promedio']:.1f} · {gi['mediana']:.1f} · {gi['total_mes']:.0f} ({gi['paginas']} pág.) "
                      f"| {gp['promedio']:.1f} · {gp['mediana']:.1f} · {gp['total_mes']:.0f} ({gp['paginas']} pág.) | {gi['5_a_20_mes'] + gi['20_o_mas_mes']}/{gi['paginas']} | {gp['5_a_20_mes'] + gp['20_o_mas_mes']}/{gp['paginas']} |")
            acc["principales"].append(s["promedio_principales"]); acc["ind"].append(gi); acc["prg"].append(gp)
        resultado["grupos"][gn] = {"sitios": lista,
                                   "promedio_principales": round(st.mean(acc["principales"]), 1),
                                   "industrias": {"paginas": sum(g["paginas"] for g in acc["ind"]), "total_mes": round(sum(g["total_mes"] for g in acc["ind"]), 1),
                                                  "promedio": round(sum(g["total_mes"] for g in acc["ind"]) / sum(g["paginas"] for g in acc["ind"]), 2),
                                                  "5_o_mas": sum(g["5_a_20_mes"] + g["20_o_mas_mes"] for g in acc["ind"])},
                                   "programas": {"paginas": sum(g["paginas"] for g in acc["prg"]), "total_mes": round(sum(g["total_mes"] for g in acc["prg"]), 1),
                                                 "promedio": round(sum(g["total_mes"] for g in acc["prg"]) / sum(g["paginas"] for g in acc["prg"]), 2),
                                                 "5_o_mas": sum(g["5_a_20_mes"] + g["20_o_mas_mes"] for g in acc["prg"])}}

    base = os.path.join(ROOT, "informe", "trafico_landings")
    json.dump(resultado, open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(base + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\n-> {base}.json / .md")


if __name__ == "__main__":
    main()
