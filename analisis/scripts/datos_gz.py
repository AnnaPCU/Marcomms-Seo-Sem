# -*- coding: utf-8 -*-
"""
datos_gz.py — los CSV grandes de datos/ viajan comprimidos en el repo (GitHub no acepta archivos de más de 100 MB y el
histórico de Search Console crece todos los meses). En disco se trabaja siempre con el .csv: los scripts no cambian.

  python scripts/datos_gz.py comprimir      para cada .csv de datos/ de más de 5 MB: escribe <archivo>.csv.gz al lado
                                            (solo si cambió) y lo anota en datos/.gitignore para que git suba el .gz
                                            y no el .csv. Correrlo antes de cada commit que toque datos/.
  python scripts/datos_gz.py descomprimir   para cada .csv.gz: regenera el .csv si falta o es más viejo que el .gz.
                                            Lo corre el arranque de la sesión en la nube (nube/setup.sh).
"""
import gzip, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(ROOT, "datos")
LIMITE = 5_000_000
IGNORE = os.path.join(DATOS, ".gitignore")
CABECERA = "# Generado por scripts/datos_gz.py: estos CSV van comprimidos (.csv.gz) en el repo.\n"


def rel(p):
    return os.path.relpath(p, DATOS).replace("\\", "/")


def comprimir():
    grandes = []
    for r, _, fs in os.walk(DATOS):
        for f in fs:
            p = os.path.join(r, f)
            if f.endswith(".csv") and os.path.getsize(p) > LIMITE:
                grandes.append(p)
                gz = p + ".gz"
                if not os.path.exists(gz) or os.path.getmtime(gz) < os.path.getmtime(p):
                    with open(p, "rb") as a, open(gz, "wb") as g, gzip.GzipFile(fileobj=g, mode="wb", compresslevel=9, mtime=0) as b:
                        shutil.copyfileobj(a, b)
                    print(f"  {rel(gz)}: {os.path.getsize(p) / 1e6:.1f} MB → {os.path.getsize(gz) / 1e6:.1f} MB")
    previos = set()
    if os.path.exists(IGNORE):
        previos = {l.strip() for l in open(IGNORE, encoding="utf-8") if l.strip() and not l.startswith("#")}
    lineas = sorted(previos | {rel(p) for p in grandes})
    open(IGNORE, "w", encoding="utf-8").write(CABECERA + "\n".join(lineas) + "\n")
    print(f"{len(grandes)} CSV grandes comprimidos; datos/.gitignore con {len(lineas)} entradas")


def descomprimir():
    n = 0
    for r, _, fs in os.walk(DATOS):
        for f in fs:
            if f.endswith(".csv.gz"):
                gz = os.path.join(r, f)
                p = gz[:-3]
                if not os.path.exists(p) or os.path.getmtime(p) < os.path.getmtime(gz):
                    with gzip.open(gz, "rb") as a, open(p, "wb") as b:
                        shutil.copyfileobj(a, b)
                    n += 1
    print(f"{n} CSV descomprimidos")


if __name__ == "__main__":
    {"comprimir": comprimir, "descomprimir": descomprimir}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
