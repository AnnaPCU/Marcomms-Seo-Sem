# -*- coding: utf-8 -*-
"""
meta_subir.py — sube a Meta Ads una campaña armada en un JSON (campaña → conjuntos → anuncios), siempre en PAUSA.

Tres modos, de menos a más:
  python meta_subir.py campanas/<carpeta>/meta.json              revisa el JSON en local y muestra lo que se mandaría
  python meta_subir.py campanas/<carpeta>/meta.json --validar    se lo manda a Meta con validate_only: Meta lo revisa
                                                                  completo y no crea nada
  python meta_subir.py campanas/<carpeta>/meta.json --subir      lo crea de verdad, todo en PAUSA

Nunca activa nada: campaña, conjuntos y anuncios se crean PAUSED aunque el JSON diga otra cosa. Activar (y
empezar a gastar) se hace a mano en Administrador de anuncios o con una orden explícita aparte.
Cada subida deja un registro con los id creados en la carpeta del JSON (meta_subida_<fecha-hora>.json).

Formato del JSON (importes en la moneda de la cuenta, por día):
{
  "cuenta": "act_1234567890",
  "marca": "CU",                                   # CU | PS | PCU: decide prefijo, dominio y vocabulario
  "campana": {"name": "CU Argentina - EUDR - Leads", "objective": "OUTCOME_LEADS",
              "special_ad_categories": [], "buying_type": "AUCTION",
              "daily_budget": 15000, "bid_strategy": "LOWEST_COST_WITHOUT_CAP"},      # presupuesto acá = Advantage+ (CBO);
                                                                                      # si no, va en cada conjunto
  "conjuntos": [{
      "name": "...", "daily_budget": 10000, "optimization_goal": "LEAD_GENERATION", "billing_event": "IMPRESSIONS",
      "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "start_time": "2026-11-05T09:00:00-0300",
      "promoted_object": {"page_id": "..."}, "destination_type": "...",
      "targeting": {"geo_locations": {"countries": ["AR"]}, "age_min": 25, "age_max": 65, ...},
      "anuncios": [{"name": "...", "page_id": "...", "instagram_user_id": "...",
                    "link": "https://argentina.controlunion.com/...", "texto": "...", "titulo": "...",
                    "descripcion": "...", "cta": "LEARN_MORE", "imagen": "img/eudr.jpg"}]   # imagen: ruta local o image_hash
  }]
}
"""
import argparse, datetime as dt, json, os, re, sys
from meta_api import Meta
from aplicar_revision import PROHIBIDO

DOMINIO = {"CU": "controlunion.com", "PCU": "controlunion.com", "PS": "peterson-solutions.com"}
DECIMALES = {"ARS": 100, "USD": 100, "EUR": 100, "BRL": 100, "CLP": 1, "COP": 1, "MXN": 100, "PEN": 100, "CAD": 100}
# largos que Meta muestra sin cortar en la mayoría de las ubicaciones (avisos, no errores)
LARGO = {"texto": 125, "titulo": 40, "descripcion": 30}


def revisar(spec):
    errores, avisos = [], []
    marca = spec.get("marca")
    if marca not in DOMINIO:
        errores.append(f"marca «{marca}»: tiene que ser CU, PS o PCU")
        return errores, avisos
    if not str(spec.get("cuenta", "")).startswith("act_"):
        errores.append("cuenta: tiene que ser el id con prefijo act_")
    c = spec.get("campana") or {}
    for k in ("name", "objective"):
        if not c.get(k):
            errores.append(f"campaña: falta {k}")
    if not str(c.get("name", "")).startswith((marca + " ", marca + "_")):
        errores.append(f"campaña «{c.get('name')}»: el nombre tiene que empezar con «{marca} »")
    if "special_ad_categories" not in c:
        errores.append("campaña: falta special_ad_categories (lista vacía si no aplica)")
    cbo = bool(c.get("daily_budget") or c.get("lifetime_budget"))
    if not spec.get("conjuntos"):
        errores.append("no hay conjuntos de anuncios")
    for s in spec.get("conjuntos", []):
        n = s.get("name", "?")
        for k in ("name", "optimization_goal", "billing_event", "targeting"):
            if not s.get(k):
                errores.append(f"conjunto «{n}»: falta {k}")
        if not cbo and not (s.get("daily_budget") or s.get("lifetime_budget")):
            errores.append(f"conjunto «{n}»: sin presupuesto (ni en la campaña ni en el conjunto)")
        if cbo and (s.get("daily_budget") or s.get("lifetime_budget")):
            errores.append(f"conjunto «{n}»: tiene presupuesto propio y la campaña también (elegir uno)")
        if not s.get("anuncios"):
            errores.append(f"conjunto «{n}»: sin anuncios")
        for x in s.get("anuncios", []):
            an = x.get("name", "?")
            for k in ("name", "page_id", "link", "texto", "titulo", "imagen"):
                if not x.get(k):
                    errores.append(f"anuncio «{an}»: falta {k}")
            if x.get("link") and DOMINIO[marca] not in x["link"]:
                errores.append(f"anuncio «{an}»: el enlace no es de {DOMINIO[marca]} ({x['link']})")
            for k, tope in LARGO.items():
                t = x.get(k) or ""
                if re.search(PROHIBIDO[marca], t, re.I):
                    errores.append(f"anuncio «{an}» ({k}): vocabulario prohibido para {marca}: «{re.search(PROHIBIDO[marca], t, re.I).group(0)}»")
                if len(t) > tope:
                    avisos.append(f"anuncio «{an}» ({k}): {len(t)} caracteres, se corta en algunas ubicaciones (>{tope})")
            img = x.get("imagen", "")
            if img and not re.fullmatch(r"[0-9a-f]{32}", img) and not os.path.exists(os.path.join(spec["_carpeta"], img)):
                errores.append(f"anuncio «{an}»: no encuentro la imagen {img}")
    return errores, avisos


def montos(d, factor):
    """importes en moneda → unidades mínimas que pide la API"""
    return {k: (int(round(float(v) * factor)) if k in ("daily_budget", "lifetime_budget", "bid_amount", "spend_cap") else v)
            for k, v in d.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--validar", action="store_true")
    g.add_argument("--subir", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    spec["_carpeta"] = os.path.dirname(os.path.abspath(a.spec))

    errores, avisos = revisar(spec)
    for w in avisos:
        print("  aviso:", w)
    if errores:
        print("\n".join("  ERROR: " + e for e in errores))
        sys.exit(1)
    n_conj = len(spec["conjuntos"]); n_an = sum(len(s["anuncios"]) for s in spec["conjuntos"])
    print(f"OK en local: «{spec['campana']['name']}», {n_conj} conjuntos, {n_an} anuncios, cuenta {spec['cuenta']}")
    if not (a.validar or a.subir):
        print(json.dumps({k: v for k, v in spec.items() if k != "_carpeta"}, ensure_ascii=False, indent=1)[:4000])
        return

    m = Meta()
    cuenta = spec["cuenta"]
    moneda = m.get(cuenta, fields="currency")["currency"]
    if moneda not in DECIMALES:
        sys.exit(f"moneda {moneda}: agregar su factor a DECIMALES antes de subir")
    factor = DECIMALES[moneda]
    extra = {"execution_options": ["validate_only"]} if a.validar else {}
    registro = {"spec": a.spec, "cuenta": cuenta, "moneda": moneda, "modo": "validar" if a.validar else "subir",
                "inicio": dt.datetime.now().isoformat(timespec="seconds"), "creados": []}

    def crear(ruta, datos, tipo):
        # en modo validar Meta no devuelve id: lo que cuelga de un objeto no creado no se puede validar contra la API
        padre = datos.get("campaign_id") or datos.get("adset_id") or ""
        if a.validar and (padre.startswith("<") or datos.get("_sin_imagen")):
            print(f"  (sin validar en Meta: {tipo} «{datos.get('name')}» depende de algo que en este modo no se crea)")
            return f"<{tipo}>"
        r = m.post(ruta, {**datos, "status": "PAUSED", **extra} if tipo != "creativo" else {**datos, **extra})
        registro["creados"].append({"tipo": tipo, "nombre": datos.get("name"), "id": r.get("id"), "respuesta": r})
        print(f"  {'validado' if a.validar else 'creado'} {tipo}: {datos.get('name')} {r.get('id', '')}")
        return r.get("id") or f"<{tipo}>"

    try:
        c = {k: v for k, v in spec["campana"].items() if k != "status"}
        id_camp = crear(f"{cuenta}/campaigns", montos(c, factor), "campaña")
        for s in spec["conjuntos"]:
            datos = {k: v for k, v in s.items() if k not in ("anuncios", "status")}
            id_conj = crear(f"{cuenta}/adsets", {**montos(datos, factor), "campaign_id": id_camp}, "conjunto")
            for x in s["anuncios"]:
                img, sin_imagen = x["imagen"], False
                if not re.fullmatch(r"[0-9a-f]{32}", img):
                    if a.validar:
                        sin_imagen = True          # no se sube la imagen solo para validar
                    else:
                        with open(os.path.join(spec["_carpeta"], img), "rb") as fh:
                            subida = m.post(f"{cuenta}/adimages", files={"filename": (os.path.basename(img), fh)})
                        img = next(iter(subida["images"].values()))["hash"]
                link = {"link": x["link"], "message": x["texto"], "name": x["titulo"], "image_hash": img,
                        "call_to_action": {"type": x.get("cta", "LEARN_MORE"), "value": {"link": x["link"]}}}
                if x.get("descripcion"):
                    link["description"] = x["descripcion"]
                historia = {"page_id": x["page_id"], "link_data": link}
                if x.get("instagram_user_id"):
                    historia["instagram_user_id"] = x["instagram_user_id"]
                creativo = {"name": x["name"] + " · creativo", "object_story_spec": historia, "url_tags": x.get("url_tags", "")}
                if sin_imagen:
                    creativo["_sin_imagen"] = True
                id_crea = crear(f"{cuenta}/adcreatives", creativo, "creativo")
                if not id_conj.startswith("<"):
                    crear(f"{cuenta}/ads", {"name": x["name"], "adset_id": id_conj, "creative": {"creative_id": id_crea}}, "anuncio")
    except RuntimeError as ex:
        registro["error"] = str(ex)
        print("\nERROR:", ex)
        if registro["creados"] and a.subir:
            print("Quedó creado lo de arriba, todo en PAUSA (no gasta). Revisarlo o borrarlo en Administrador de anuncios.")
    finally:
        registro["fin"] = dt.datetime.now().isoformat(timespec="seconds")
        if a.subir:
            out = os.path.join(spec["_carpeta"], f"meta_subida_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
            json.dump(registro, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("registro ->", out)
    if "error" in registro:
        sys.exit(1)


if __name__ == "__main__":
    main()
