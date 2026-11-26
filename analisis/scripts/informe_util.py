# -*- coding: utf-8 -*-
"""Helpers de formato y HTML compartidos por los generadores de informes."""
import html
from datetime import date

MESES = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may", "06": "jun", "07": "jul",
         "08": "ago", "09": "sep", "10": "oct", "11": "nov", "12": "dic"}


def n(x, dec=0):
    if x is None or x == "":
        return "—"
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if dec == 0:
        return f"{int(round(x)):,}".replace(",", ".")
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=0):
    return "—" if x is None else n(x, dec) + "%"


def ars(x):
    return "—" if x is None else "ARS " + n(x)


def e(s):
    return html.escape(str(s))


def fecha(s):
    y, m, d = str(s).split("-")
    return f"{int(d)} {MESES[m]} {y}"


def hoy():
    h = date.today()
    return f"{h.day} {MESES[f'{h.month:02d}']} {h.year}"


def tabla(cols, filas, cls="tight", total=None):
    th = "".join(f'<th class="{c[1]}">{e(c[0])}</th>' for c in cols)
    tr = "".join("<tr>" + "".join(f'<td class="{c[1]}">{v}</td>' for c, v in zip(cols, f)) + "</tr>" for f in filas)
    if total:
        tr += '<tr class="total">' + "".join(f'<td class="{c[1]}">{v}</td>' for c, v in zip(cols, total)) + "</tr>"
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def stat(num, tit, desc=""):
    return f'<div class="stat"><p class="n">{num}</p><p class="t">{e(tit)}</p><p class="d">{desc}</p></div>'


def kpi(num, lab):
    return f'<div class="kpi"><span class="kn">{num}</span><span class="kl">{e(lab)}</span></div>'


def chip(estado):
    cls = {"Resuelto": "ok", "Propuesto": "prop", "Decisión abierta": "open", "Nuevo": "new", "Corregido": "ok", "Alerta": "new"}.get(estado, "prop")
    return f'<span class="chip {cls}">{e(estado)}</span>'


def barra(valor, maximo, ancho=28):
    w = 0 if not maximo else max(2, round(valor / maximo * 100))
    return f'<span class="bar" style="width:{ancho}mm"><span style="width:{w}%"></span></span>'


def path_corto(p, largo=52):
    if not p:
        return "—"
    return e(p if len(p) <= largo else "…" + p[-(largo - 1):])


def nota_marca(fecha_txt):
    return (f'<p class="small">Pieza de circulación interna sin identidad de marca: cubre unidades de Control Union y de Peterson Solutions, '
            f'y el manual del grupo no admite piezas que combinen ambas marcas. Paleta limitada a los colores comunes a los dos manuales. '
            f'Cada hallazgo se resuelve dentro de su propia marca. Generado el {fecha_txt}.</p>')
