# -*- coding: utf-8 -*-
"""
chequear_lote.py — valida un lote de tarjetas reescritas (informe/concretar_2026-10/*.json, formato en BRIEF.md) antes
de cargarlo al tablero: estructura de la ficha «campana» o «seo», que cada paso diga qué cargar, largos, vocabulario de
marca, que las claves viejas existan, que las campañas estén en el catálogo y que lo que se quita de un anuncio exista hoy.

Uso: python chequear_lote.py informe/concretar_2026-10/sem_a.json
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aplicar_revision as ar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ruta = sys.argv[1]
    lote = json.load(open(ruta, encoding="utf-8"))
    viejas = {r["clave"]: r for r in json.load(open(os.path.join(ROOT, "informe", "recomendaciones.json"), encoding="utf-8"))}
    campanas = ar.catalogo()
    errores = []
    usadas = []
    for t in lote.get("tarjetas", []):
        c, ev = t.get("clave", "?"), t.get("evidencia") or {}
        usadas += [c] + list(t.get("unifica") or [])
        if c not in viejas and not re.fullmatch(r"(CU|PCU|PS):SEM:campana:[a-z0-9-]+@2026-10", c):
            errores.append(f"{c}: no es una clave existente ni una clave nueva válida")
        for k in t.get("unifica") or []:
            if k not in viejas:
                errores.append(f"{c}: unifica «{k}», que no existe")
        if t.get("marca") not in ar.MARCAS or t.get("prioridad") not in ar.PRIORIDADES:
            errores.append(f"{c}: marca o prioridad inválida")
        if not t.get("titulo") or "…" in t["titulo"] or len(t["titulo"]) > 160:
            errores.append(f"{c}: título vacío, cortado con «…» o de más de 160 caracteres")
        if not t.get("detalle"):
            errores.append(f"{c}: falta detalle")
        if ev.get("ficha") == "campana":
            errores += ar.validar_campana(c, ev)
            for n in [ev.get("campana")] + list(ev.get("campanas") or []):
                if n and campanas and n not in campanas and "a crear" not in n and not n.startswith("Todas"):
                    errores.append(f"{c}: la campaña «{n}» no está en el catálogo (estructura_20261021)")
            if t.get("campana") and campanas and t["campana"] not in campanas:
                errores.append(f"{c}: campana «{t['campana']}» no está en el catálogo")
        elif ev.get("ficha") == "seo":
            errores += ar.validar_seo(c, ev, t.get("marca"))
        else:
            errores.append(f"{c}: evidencia.ficha tiene que ser «campana» o «seo»")
    for d in lote.get("descartes", []):
        usadas.append(d.get("clave"))
        if d.get("clave") not in viejas or not d.get("motivo"):
            errores.append(f"descarte {d.get('clave')}: clave inexistente o sin motivo")
    rep = {k for k in usadas if usadas.count(k) > 1}
    if rep:
        errores.append(f"claves usadas más de una vez: {sorted(rep)}")
    if errores:
        print(f"{len(errores)} errores:")
        for e in errores:
            print("  ·", e)
        sys.exit(1)
    print(f"OK: {len(lote.get('tarjetas', []))} tarjetas, {len(lote.get('descartes', []))} descartes")


if __name__ == "__main__":
    main()
