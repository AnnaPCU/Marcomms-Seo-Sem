# -*- coding: utf-8 -*-
"""
cargar_lotes.py — convierte los lotes de tarjetas reescritas (informe/concretar_2026-10/*.json, ver BRIEF.md) en SQL
para el tablero, un archivo por tarjeta (para mandarlos de a uno por el conector y verificar cada uno), más el md5 que
tiene que devolver la base para cada evidencia.

  · Clave existente: se reescriben título, detalle, prioridad y evidencia; el estado no se toca (lo que el equipo tomó
    sigue «en proceso»). La campaña se actualiza si la tarjeta nombra una; si no, queda la que tenía.
  · Clave nueva: se inserta en «propuesta», mes de alta 2026-10.
  · `unifica` y `descartes`: solo tarjetas en «propuesta» pasan a «descartada», con motivo y movimiento en el historial.

Uso: python cargar_lotes.py <carpeta de salida> informe/concretar_2026-10/sem_espana.json [...]
"""
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aplicar_revision import q  # noqa: E402

MES, USUARIO, ORIGEN = "2026-10", "Concretar tarjetas (Claude)", "concretar-2026-10"


def pg(v):
    """Texto de un jsonb como lo serializa Postgres (claves por largo y después por bytes), para comparar md5."""
    if isinstance(v, dict):
        ks = sorted(v, key=lambda k: (len(k.encode()), k.encode()))
        return "{" + ", ".join(json.dumps(k, ensure_ascii=False) + ": " + pg(v[k]) for k in ks) + "}"
    if isinstance(v, list):
        return "[" + ", ".join(pg(x) for x in v) + "]"
    if isinstance(v, bool) or v is None:
        return json.dumps(v)
    if isinstance(v, float) and v.is_integer():
        return str(v)
    return json.dumps(v, ensure_ascii=False)


def campana_id(nombre):
    return f"(select id from seo_sem.campanas where cuenta = 'actual' and nombre = {q(nombre)})" if nombre else "null"


def grupo_id(campana, grupo):
    if not (campana and grupo):
        return "null"
    return (f"(select g.id from seo_sem.grupos g join seo_sem.campanas c on c.id = g.campana_id "
            f"where c.cuenta = 'actual' and c.nombre = {q(campana)} and g.nombre = {q(grupo)})")


def descartar(clave, motivo):
    return (f"with r as (update seo_sem.recomendaciones set estado = 'descartada', motivo_descarte = {q(motivo)}, mes_cierre = {q(MES)}, "
            f"actualizada_por = {q(USUARIO)} where clave = {q(clave)} and estado = 'propuesta' returning id)\n"
            f"insert into seo_sem.recomendacion_eventos (recomendacion_id, de_estado, a_estado, motivo, usuario) "
            f"select id, 'propuesta', 'descartada', {q(motivo)}, {q(USUARIO)} from r;")


def main():
    salida, rutas = sys.argv[1], sys.argv[2:]
    viejas = {r["clave"] for r in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "informe", "recomendaciones.json"), encoding="utf-8"))}
    os.makedirs(salida, exist_ok=True)
    md5s, n = [], 0
    for ruta in rutas:
        lote = json.load(open(ruta, encoding="utf-8"))
        for t in lote.get("tarjetas", []):
            n += 1
            ev = dict(t["evidencia"], revisiones=[{"mes": MES, "accion": "concretar", "datos_hasta": t["evidencia"].get("datos_hasta")}])
            campana = t.get("campana") if ev.get("ficha") == "campana" else None
            if t["clave"] in viejas:
                sets = [f"titulo = {q(t['titulo'])}", f"detalle = {q(t['detalle'])}", f"prioridad = {q(t['prioridad'])}", f"evidencia = {q(ev)}",
                        f"actualizada_por = {q(USUARIO)}"]
                if campana:
                    sets += [f"campana_id = {campana_id(campana)}", f"grupo_id = {grupo_id(campana, t.get('grupo'))}"]
                sql = f"update seo_sem.recomendaciones set {', '.join(sets)} where clave = {q(t['clave'])};"
            else:
                sql = ("insert into seo_sem.recomendaciones (clave, marca, tipo, campana_id, grupo_id, sitio, titulo, detalle, evidencia, prioridad, estado, mes_alta, origen, actualizada_por)\n"
                       f"values ({q(t['clave'])}, {q(t['marca'])}, {q('SEO' if ev.get('ficha') == 'seo' else 'SEM')}, {campana_id(campana)}, {grupo_id(campana, t.get('grupo'))}, "
                       f"{q(t.get('sitio'))}, {q(t['titulo'])}, {q(t['detalle'])}, {q(ev)}, {q(t['prioridad'])}, 'propuesta', {q(MES)}, {q(ORIGEN)}, {q(USUARIO)}) "
                       "on conflict (clave) do nothing;")
            partes = [sql] + [descartar(k, f"Unificada en «{t['titulo']}»: una acción, una tarjeta.") for k in t.get("unifica") or [] if k != t["clave"]]
            partes.append(f"select md5(evidencia::text) as md5, estado from seo_sem.recomendaciones where clave = {q(t['clave'])};")
            open(os.path.join(salida, f"c{n:02d}.sql"), "w", encoding="utf-8").write("\n".join(partes) + "\n")
            md5s.append((f"c{n:02d}", t["clave"], hashlib.md5(pg(ev).encode()).hexdigest(), sum(map(len, partes))))
        for d in lote.get("descartes", []):
            n += 1
            open(os.path.join(salida, f"c{n:02d}.sql"), "w", encoding="utf-8").write(descartar(d["clave"], d["motivo"]) + "\n")
            md5s.append((f"c{n:02d}", d["clave"], "descarte", 0))
    with open(os.path.join(salida, "md5.txt"), "w", encoding="utf-8") as f:
        for m in md5s:
            f.write(" ".join(map(str, m)) + "\n")
    for m in md5s:
        print(*m)


if __name__ == "__main__":
    main()
