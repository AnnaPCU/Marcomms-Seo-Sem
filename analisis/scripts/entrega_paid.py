# -*- coding: utf-8 -*-
"""
entrega_paid.py — entrega mensual de Paid Media a MarComms-Reports (solo lectura en Google Ads y Meta Ads).

Arma, para el mes M, los archivos que pide el contrato docs/ENTREGA_PAID_DESDE_SEO_SEM.md del repo AnnaPCU/MarComms-Reports
y los deja en su carpeta metricas/paid-media/:

  google-ads/AAAA-MM/   campanas.csv · semanal_por_grupo.csv · terminos_y_keywords.csv · LEEME.md
                        (todas las campañas Search con actividad en el mes, del día 1 al último, moneda de la cuenta)
  meta-ads/AAAA-MM-<vuelo>/   diario · total · plataforma · edad · sexo · anuncios · destinos-anuncios · LEEME.md
                        (solo los vuelos de Meta que terminaron en M y que todavía no se entregaron)

Formato: CSV UTF-8 con comas, números sin separador de miles y con punto decimal, fechas AAAA-MM-DD. Los tres de Google
llevan arriba el título y el rango de fechas, como el export del Editor de informes (build_detail.py de MarComms-Reports
saltea esas dos líneas); el encabezado va en la tercera.

Después valida con el tooling del repo en modo prueba (build_month.py / build_meta.py --dry-run, que no escriben nada) y,
para el detalle por grupo, con build_detail.collect() (que tampoco escribe). Si un nombre de campaña no tiene prefijo
conocido (nomenclatura nueva, p. ej. CU_US_SEARCH_…), valida el resto sin esas campañas y las anota en el LEEME para que
allá se mapeen una vez.

Uso:
  python entrega_paid.py                      mes anterior, valida y NO pushea
  python entrega_paid.py --mes 2026-10        un mes puntual
  python entrega_paid.py --mes 2026-10 --push valida y, si todo pasa, commitea y pushea solo metricas/paid-media/ a main
  opciones: --sin-meta · --sin-google · --forzar (rehace un mes ya entregado) · --repo <clon de MarComms-Reports>

El clon es parcial (sparse: metricas/paid-media, scripts/paid, docs) porque el repo tiene archivos con «:» en el nombre,
que Windows no acepta. Nunca toca nada fuera de metricas/paid-media/.
"""
import argparse, calendar, csv, datetime as dt, io, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# clon de MarComms-Reports: en la compu, el sparse de _repos/paid-entrega; en la nube, el que deja add_repo junto a este
# repo (/home/user/marcomms-reports con permiso de push, /home/user/annapcu/marcomms-reports si es solo lectura)
CLONES = [os.path.join(ROOT, "..", "_repos", "paid-entrega"), os.path.join(ROOT, "..", "..", "marcomms-reports"),
          os.path.join(ROOT, "..", "..", "annapcu", "marcomms-reports")]
REPO_DEF = os.path.normpath(next((c for c in CLONES if os.path.isdir(os.path.join(c, ".git"))), CLONES[0]))
PREFIJOS_GOOGLE = ("CU España", "CU Portugal", "CU Canada", "PS Argentina", "CU United States", "CU Argentina",
                   "PCU - España", "PCU - Argentina")
AHORA = dt.datetime.now()


# ───────────────────────── utilidades ─────────────────────────
def mes_anterior(hoy=None):
    hoy = hoy or dt.date.today()
    d = hoy.replace(day=1) - dt.timedelta(days=1)
    return f"{d:%Y-%m}"


def rango(mes):
    a, m = map(int, mes.split("-"))
    return dt.date(a, m, 1), dt.date(a, m, calendar.monthrange(a, m)[1])


def n2(v):
    """número con punto decimal, sin miles, 2 decimales como máximo (enteros sin decimales)"""
    v = round(float(v or 0) + 0.0, 2)
    return str(int(v)) if v == int(v) else f"{v:.2f}"


def pct(v):
    return "" if v in (None, "") else f"{float(v) * 100:.2f}%"


def escribir(path, filas, columnas, preambulo=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        for linea in preambulo or []:
            f.write(linea + "\n")
        w = csv.writer(f)
        w.writerow(columnas)
        for r in filas:
            w.writerow([r.get(c, "") for c in columnas])


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


# ───────────────────────── Google Ads ─────────────────────────
def google(mes, carpeta):
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    from ads_export import aplanar, YAML, CUENTAS

    client = GoogleAdsClient.load_from_storage(YAML)
    cid = CUENTAS["cuentas"]["principal"]
    svc = client.get_service("GoogleAdsService")
    a, b = rango(mes)

    def q(gaql):
        try:
            return [aplanar(r) for lote in svc.search_stream(customer_id=cid, query=gaql) for r in lote.results]
        except GoogleAdsException as ex:
            raise SystemExit("Google Ads API: " + "; ".join(e.message for e in ex.failure.errors))

    def g(r, k, cast=float):
        v = r.get(k)
        return cast(v) if v not in (None, "") else cast(0)

    fechas = f"segments.date BETWEEN '{a}' AND '{b}'"
    search = "campaign.advertising_channel_type = 'SEARCH'"
    camp = q(f"""SELECT campaign.name, campaign.start_date_time, customer.currency_code, metrics.impressions,
                 metrics.clicks, metrics.cost_micros, metrics.conversions
                 FROM campaign WHERE {fechas} AND {search}""")
    sem = q(f"""SELECT campaign.name, ad_group.name, segments.week, customer.currency_code, metrics.impressions,
                metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
                FROM ad_group WHERE {fechas} AND {search}""")
    ter = q(f"""SELECT campaign.name, ad_group.name, segments.keyword.info.text, search_term_view.search_term,
                segments.search_term_match_type, customer.currency_code, metrics.impressions, metrics.clicks,
                metrics.cost_micros, metrics.conversions
                FROM search_term_view WHERE {fechas} AND {search}""")
    otras = q(f"""SELECT campaign.name, campaign.advertising_channel_type, metrics.cost_micros FROM campaign
                  WHERE {fechas} AND campaign.advertising_channel_type != 'SEARCH' AND metrics.cost_micros > 0""")

    titulo_rango = f"\"{a:%B} {a.day}, {a.year} - {b:%B} {b.day}, {b.year}\""
    activas = [r for r in camp if g(r, "metrics.impressions") or g(r, "metrics.clicks") or g(r, "metrics.cost_micros")]
    filas_c = [{"Campaign": r["campaign.name"], "Currency code": r.get("customer.currency_code", ""),
                "Impr.": int(g(r, "metrics.impressions")), "Clicks": int(g(r, "metrics.clicks")),
                "Cost": n2(g(r, "metrics.cost_micros") / 1e6), "Conversions": n2(g(r, "metrics.conversions"))}
               for r in sorted(activas, key=lambda r: -g(r, "metrics.cost_micros"))]
    nombres = {r["Campaign"] for r in filas_c}
    filas_s = [{"Campaign": r["campaign.name"], "Ad group": r.get("ad_group.name", ""), "Week": r.get("segments.week", ""),
                "Currency code": r.get("customer.currency_code", ""), "Impr.": int(g(r, "metrics.impressions")),
                "Clicks": int(g(r, "metrics.clicks")), "Cost": n2(g(r, "metrics.cost_micros") / 1e6),
                "Conversions": n2(g(r, "metrics.conversions")),
                "Search impr. share": pct(r.get("metrics.search_impression_share")),
                "Search lost IS (rank)": pct(r.get("metrics.search_rank_lost_impression_share"))}
               for r in sem if r["campaign.name"] in nombres
               and (g(r, "metrics.impressions") or g(r, "metrics.clicks") or g(r, "metrics.cost_micros"))]
    filas_s.sort(key=lambda r: (r["Campaign"], r["Ad group"], r["Week"]))
    TIPO = {"EXACT": "Exact match", "PHRASE": "Phrase match", "BROAD": "Broad match",
            "NEAR_EXACT": "Exact match (close variant)", "NEAR_PHRASE": "Phrase match (close variant)"}
    filas_t = [{"Campaign": r["campaign.name"], "Ad group": r.get("ad_group.name", ""),
                "Search keyword": r.get("segments.keyword.info.text", ""), "Search term": r.get("search_term_view.search_term", ""),
                "Search terms match type": TIPO.get(r.get("segments.search_term_match_type", ""), r.get("segments.search_term_match_type", "")),
                "Currency code": r.get("customer.currency_code", ""), "Impr.": int(g(r, "metrics.impressions")),
                "Clicks": int(g(r, "metrics.clicks")), "Cost": n2(g(r, "metrics.cost_micros") / 1e6),
                "Conversions": n2(g(r, "metrics.conversions"))} for r in ter]
    filas_t.sort(key=lambda r: (r["Campaign"], r["Ad group"], -float(r["Cost"]), r["Search term"]))

    escribir(os.path.join(carpeta, "campanas.csv"), filas_c,
             ["Campaign", "Currency code", "Impr.", "Clicks", "Cost", "Conversions"], ["Rendimiento de la campaña", titulo_rango])
    escribir(os.path.join(carpeta, "semanal_por_grupo.csv"), filas_s,
             ["Campaign", "Ad group", "Week", "Currency code", "Impr.", "Clicks", "Cost", "Conversions", "Search impr. share",
              "Search lost IS (rank)"], ["Semanal por grupo de anuncios", titulo_rango])
    escribir(os.path.join(carpeta, "terminos_y_keywords.csv"), filas_t,
             ["Campaign", "Ad group", "Search keyword", "Search term", "Search terms match type", "Currency code", "Impr.",
              "Clicks", "Cost", "Conversions"], ["Términos de búsqueda + Palabras Clave", titulo_rango])

    # control propio: el semanal tiene que sumar exactamente lo mismo que las campañas
    tot = lambda filas: (sum(int(r["Impr."]) for r in filas), sum(int(r["Clicks"]) for r in filas),
                         round(sum(float(r["Cost"]) for r in filas), 2))
    if tot(filas_c)[:2] != tot(filas_s)[:2] or abs(tot(filas_c)[2] - tot(filas_s)[2]) > 0.05 * max(1, len(filas_c)):
        print(f"  ⚠ campañas {tot(filas_c)} ≠ semanal {tot(filas_s)} (lo confirma build_month.py)")

    monedas = sorted({r["Currency code"] for r in filas_c})
    parciales = []
    for r in activas:
        ini = (r.get("campaign.start_date_time") or "")[:10]
        if ini and a < dt.date.fromisoformat(ini) <= b:
            parciales.append((r["campaign.name"], ini))
    sin_prefijo = sorted(n for n in nombres if not n.startswith(PREFIJOS_GOOGLE))
    no_search = sorted({(r["campaign.name"], r.get("campaign.advertising_channel_type", "")) for r in otras})
    leeme = [f"# Google Ads · {mes}", "",
             f"- Cuenta: {cid} (Google Ads, solo lectura por API). Moneda: {', '.join(monedas) or '—'}, sin convertir.",
             f"- Rango: {a} a {b} (mes completo, ya cerrado).",
             f"- Extraído: {AHORA:%Y-%m-%d %H:%M} (hora de Argentina) con `analisis/scripts/entrega_paid.py` de SEO-SEM.",
             f"- {len(filas_c)} campañas Search con actividad · {len(filas_s)} filas semanales · {len(filas_t)} términos.",
             f"- Totales: {tot(filas_c)[0]} impr. · {tot(filas_c)[1]} clics · {tot(filas_c)[2]:.2f} {'/'.join(monedas)} · "
             f"{n2(sum(float(r['Conversions']) for r in filas_c))} conv.", ""]
    leeme += ["## Campañas que arrancaron a mitad de mes (Parcial)", ""]
    leeme += [f"- {n}: desde el {i} (fecha de inicio de la campaña en Google Ads)" for n, i in sorted(parciales)] or ["- Ninguna."]
    leeme += ["", "## Nomenclatura nueva (sin prefijo de cuenta conocido)", ""]
    leeme += [f"- {n}" for n in sin_prefijo] or ["- Ninguna."]
    if sin_prefijo:
        leeme += ["", "Van en los archivos tal cual; hay que mapearlas a su cuenta en MarComms-Reports antes de procesar."]
    leeme += ["", "## Fuera de la entrega", ""]
    leeme += [f"- {n} ({t}): no es Search; tuvo gasto en el mes" for n, t in no_search] or ["- Nada: todo el gasto del mes es Search."]
    leeme += ["", "Lo que no se pudo extraer: nada (si una métrica no vino de la API, su celda está vacía)."]
    open(os.path.join(carpeta, "LEEME.md"), "w", encoding="utf-8").write("\n".join(leeme) + "\n")
    print(f"  Google Ads {mes}: {len(filas_c)} campañas · {len(filas_s)} semanales · {len(filas_t)} términos · "
          f"{tot(filas_c)[2]:.2f} {'/'.join(monedas)}" + (f" · {len(sin_prefijo)} sin prefijo" if sin_prefijo else ""))
    return sin_prefijo


# ───────────────────────── Meta Ads ─────────────────────────
def accion(lista, *tipos):
    for x in lista or []:
        if x.get("action_type") in tipos:
            return x.get("value")
    return None


def resultado(fila):
    res = (fila.get("results") or [{}])[0]
    vals = res.get("values") or []
    return (vals[0].get("value") if vals else "0" if res.get("indicator") else ""), res.get("indicator", "")


def fila_meta(r, moneda):
    valor, indicador = resultado(r)
    return {"Campaign name": r.get("campaign_name", ""), f"Amount spent ({moneda})": r.get("spend", "0"),
            "Impressions": r.get("impressions", "0"), "Reach": r.get("reach", ""), "Frequency": r.get("frequency", ""),
            "Link clicks": r.get("inline_link_clicks", "0"), "Unique link clicks": r.get("unique_inline_link_clicks", ""),
            "Outbound clicks": accion(r.get("outbound_clicks"), "outbound_click") or "0",
            "Landing page views": accion(r.get("actions"), "landing_page_view") or "",
            "Results": valor, "Result indicator": indicador,
            "Messaging conversations started": accion(r.get("actions"), "onsite_conversion.messaging_conversation_started_7d") or "",
            "Leads": accion(r.get("actions"), "onsite_conversion.lead_grouped", "leadgen_grouped") or ""}


CAMPOS = ("campaign_name,spend,impressions,reach,frequency,inline_link_clicks,unique_inline_link_clicks,outbound_clicks,"
          "actions,results,date_start,date_stop")


def destino(cr):
    """typeform / hsform / whatsapp / phone / web, según la URL final o el CTA del creativo"""
    texto = json.dumps(cr or {}, ensure_ascii=False).lower()
    if "typeform" in texto:
        return "typeform"
    if "hsforms" in texto or "hubspot" in texto:
        return "hsform"
    if "whatsapp" in texto or "wa.me" in texto:
        return "whatsapp"
    if '"call_now"' in texto or "tel:" in texto:
        return "phone"
    return "web"


def ya_entregado(repo, nombre):
    """el nombre de la campaña ya figura en algún archivo de texto de paid-media del remoto (entregado o procesado)"""
    r = subprocess.run(["git", "-C", repo, "grep", "-l", "-F", nombre, "origin/main", "--", "metricas/paid-media", "src/data"],
                       capture_output=True, text=True, encoding="utf-8")
    return bool(r.stdout.strip())


def meta(mes, base, repo):
    from meta_api import Meta
    m = Meta()
    a, b = rango(mes)
    hechas = []
    for cuenta in m.cuentas():
        info = m.get(cuenta, fields="name,currency")
        moneda = info["currency"]
        camps = m.todos(f"{cuenta}/campaigns", fields="id,name,effective_status,objective")
        vuelos = defaultdict(list)
        for c in camps:
            dias = m.todos(f"{c['id']}/insights", fields="spend", time_increment=1, date_preset="maximum")
            con_gasto = [d["date_start"] for d in dias if float(d.get("spend") or 0) > 0]
            if not con_gasto:
                continue
            c["desde"], c["hasta"] = min(con_gasto), max(con_gasto)
            partes = [p.strip() for p in c["name"].split(" - ")]
            vuelos[(partes[0], partes[1] if len(partes) > 1 else partes[0])].append(c)   # marca + evento
        for (marca, evento), cs in vuelos.items():
            desde, hasta = min(c["desde"] for c in cs), max(c["hasta"] for c in cs)
            if not (str(a) <= hasta <= str(b)) or any(c["effective_status"] == "ACTIVE" for c in cs):
                continue                     # no terminó en este mes o sigue activo
            if all(ya_entregado(repo, c["name"]) for c in cs):
                print(f"  Meta · {marca} - {evento}: ya entregado, se saltea")
                continue
            carpeta = os.path.join(base, f"{desde[:7]}-{slug(evento)}-{slug(marca)}")
            ids = [c["id"] for c in cs]
            rng = json.dumps({"since": desde, "until": hasta})
            filtro = json.dumps([{"field": "campaign.id", "operator": "IN", "value": ids}])

            def ins(**kw):
                return m.todos(f"{cuenta}/insights", level=kw.pop("level", "campaign"), fields=kw.pop("fields", CAMPOS),
                               time_range=rng, filtering=filtro, **kw)

            cols = ["Campaign name", f"Amount spent ({moneda})", "Impressions", "Reach", "Frequency", "Link clicks",
                    "Unique link clicks", "Outbound clicks", "Landing page views", "Results", "Result indicator",
                    "Messaging conversations started", "Leads"]
            diario = [dict(fila_meta(r, moneda), Day=r["date_start"]) for r in ins(time_increment=1)]
            escribir(os.path.join(carpeta, "diario.csv"), sorted(diario, key=lambda r: (r["Day"], r["Campaign name"])), ["Day"] + cols)
            escribir(os.path.join(carpeta, "total.csv"), [fila_meta(r, moneda) for r in ins()], cols)
            for arch, brk, col in (("plataforma", "publisher_platform", "Platform"), ("edad", "age", "Age"), ("sexo", "gender", "Gender")):
                filas = [dict(fila_meta(r, moneda), **{col: r.get(brk, "")}) for r in ins(breakdowns=brk)]
                escribir(os.path.join(carpeta, f"{arch}.csv"), filas, [col] + cols)
            anuncios = ins(level="ad", fields="ad_id,ad_name," + CAMPOS)
            escribir(os.path.join(carpeta, "anuncios.csv"),
                     [dict(fila_meta(r, moneda), **{"Ad name": r.get("ad_name", "")}) for r in anuncios], ["Ad name"] + cols)
            dest = []
            for r in anuncios:
                ad = m.get(r["ad_id"], fields="creative{object_story_spec,asset_feed_spec,call_to_action_type,link_url,object_url}")
                dest.append({"Campaign name": r.get("campaign_name", ""), "Ad name": r.get("ad_name", ""), "Destino": destino(ad.get("creative"))})
            escribir(os.path.join(carpeta, "destinos-anuncios.csv"), dest, ["Campaign name", "Ad name", "Destino"])
            leeme = [f"# Meta Ads · {marca} - {evento}", "",
                     f"- Cuenta: {info['name']} ({cuenta}). Moneda: {moneda}, sin convertir.",
                     f"- Rango: {desde} a {hasta} (primer y último día con gasto del vuelo).",
                     f"- Extraído: {AHORA:%Y-%m-%d %H:%M} (hora de Argentina) por Marketing API con `analisis/scripts/entrega_paid.py`.",
                     "- Campañas del vuelo:"] + [f"  - {c['name']} ({c['objective']}, {c['desde']} a {c['hasta']})" for c in cs] + [
                     "- Destinos: deducidos de la URL o el CTA de cada creativo (typeform / hsform / whatsapp / phone / web);"
                     " revisarlos si un anuncio lleva a otro lado.",
                     "- Hora del día: no se extrae (opcional).",
                     f"- Si el mismo evento tuvo campaña en Google Ads, es una campaña en paralelo (DECISIONES §22): reubicar"
                     f" la carpeta al procesar."]
            open(os.path.join(carpeta, "LEEME.md"), "w", encoding="utf-8").write("\n".join(leeme) + "\n")
            print(f"  Meta · {marca} - {evento}: {desde} a {hasta} · {len(cs)} campañas · {len(anuncios)} anuncios → {os.path.basename(carpeta)}")
            hechas.append(carpeta)
    return hechas


# ───────────────────────── validación ─────────────────────────
def sin_campanas(origen, quitar):
    """copia temporal de la carpeta de Google sin las campañas de nomenclatura nueva (para validar el resto)"""
    tmp = tempfile.mkdtemp(prefix="paid_")
    destino_ = os.path.join(tmp, os.path.basename(origen))
    os.makedirs(destino_)
    for f in os.listdir(origen):
        if not f.endswith(".csv"):
            continue
        lineas = open(os.path.join(origen, f), encoding="utf-8").read().splitlines()
        cab = next(i for i, l in enumerate(lineas) if l.startswith("Campaign,"))
        quedan = lineas[:cab + 1] + [l for l in lineas[cab + 1:] if next(csv.reader([l]))[0] not in quitar]
        open(os.path.join(destino_, f), "w", encoding="utf-8").write("\n".join(quedan) + "\n")
    return destino_


def validar_google(repo, carpeta, sin_prefijo):
    objetivo = sin_campanas(carpeta, set(sin_prefijo)) if sin_prefijo else carpeta
    r = subprocess.run([sys.executable, "-B", "scripts/paid/build_month.py", objetivo, "--dry-run"], cwd=repo,
                       capture_output=True, text=True, encoding="utf-8")
    print("\n".join("    " + l for l in r.stderr.splitlines() if l.strip()))
    if r.returncode:
        return False
    # el detalle por grupo (build_detail.collect) no escribe nada: confirma que lee los dos archivos
    code = ("import sys; sys.path.insert(0, 'scripts/paid'); from build_detail import collect; "
            f"d = collect({os.path.join(objetivo, 'semanal_por_grupo.csv')!r}, {os.path.join(objetivo, 'terminos_y_keywords.csv')!r}); "
            "print('    ✓ build_detail.collect: ' + str(sum(len(c) for c in d.values())) + ' campañas con detalle')")
    r2 = subprocess.run([sys.executable, "-B", "-c", code], cwd=repo, capture_output=True, text=True, encoding="utf-8")
    print(r2.stdout.rstrip() or r2.stderr.strip()[-600:])
    return r2.returncode == 0


def validar_meta(repo, carpeta):
    r = subprocess.run([sys.executable, "-B", "scripts/paid/build_meta.py", carpeta, "--dry-run"], cwd=repo,
                       capture_output=True, text=True, encoding="utf-8")
    print("\n".join("    " + l for l in (r.stdout + r.stderr).splitlines()[-15:] if l.strip()))
    return r.returncode == 0


# ───────────────────────── main ─────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mes", default=mes_anterior())
    ap.add_argument("--repo", default=REPO_DEF)
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--sin-meta", action="store_true")
    ap.add_argument("--sin-google", action="store_true")
    o = ap.parse_args()
    repo = os.path.abspath(o.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"No encuentro el clon de MarComms-Reports en {repo} (ver el encabezado de este script).")
    git(repo, "fetch", "-q", "origin")
    if git(repo, "status", "--porcelain", "--", "metricas/paid-media"):
        sys.exit("El clon tiene cambios sin subir en metricas/paid-media: revisalos antes de otra entrega.")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--ff-only", "origin/main")
    pm = os.path.join(repo, "metricas", "paid-media")
    print(f"Entrega Paid Media {o.mes} → {repo}")

    nuevas, ok = [], True
    if not o.sin_google:
        rel = f"metricas/paid-media/google-ads/{o.mes}"
        entregado = git(repo, "ls-tree", "-d", "--name-only", "origin/main", rel, f"metricas/paid-media/google-ads/_procesados/{o.mes}")
        if entregado and not o.forzar:
            print(f"  Google Ads {o.mes}: ya está en el repo ({entregado.splitlines()[0]}); no se rehace (--forzar para rehacerlo)")
        else:
            carpeta = os.path.join(pm, "google-ads", o.mes)
            shutil.rmtree(carpeta, ignore_errors=True)
            sin_prefijo = google(o.mes, carpeta)
            if validar_google(repo, carpeta, sin_prefijo):
                nuevas.append(carpeta)
            else:
                ok = False
                print("  ✗ Google Ads no pasa la validación de MarComms-Reports: no se entrega.")
    if not o.sin_meta:
        for carpeta in meta(o.mes, os.path.join(pm, "meta-ads"), repo):
            if validar_meta(repo, carpeta):
                nuevas.append(carpeta)
            else:
                ok = False
                print(f"  ✗ {os.path.basename(carpeta)} no pasa build_meta.py --dry-run: no se entrega.")

    if not nuevas:
        print("Nada nuevo para entregar." if ok else "No se entrega nada.")
        sys.exit(0 if ok else 1)
    if not ok:
        print("Hay partes que no validaron: no se pushea nada. Corregí la extracción y volvé a correr.")
        sys.exit(1)
    if not o.push:
        print("Validado. Sin --push: los archivos quedan en el clon y no se suben.")
        return
    for c in nuevas:
        git(repo, "add", "--", os.path.relpath(c, repo).replace("\\", "/"))
    fuera = [f for f in git(repo, "diff", "--cached", "--name-only").splitlines() if not f.startswith("metricas/paid-media/")]
    if fuera:
        sys.exit(f"Hay archivos fuera de metricas/paid-media en el commit: {fuera}")
    partes = " + ".join(x for x, y in (("Google Ads", any("google-ads" in c for c in nuevas)),
                                        ("Meta Ads", any("meta-ads" in c for c in nuevas))) if y)
    git(repo, "-c", "user.name=AnnaPCU", "-c", "user.email=anna@petersontech.app", "commit", "-q", "-m",
        f"Paid {o.mes}: entrega desde SEO-SEM ({partes})\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    git(repo, "push", "-q", "origin", "main")
    print(f"Subido a main: {git(repo, 'log', '--oneline', '-1')}")


if __name__ == "__main__":
    main()
