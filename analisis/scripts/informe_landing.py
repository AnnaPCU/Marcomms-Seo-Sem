# -*- coding: utf-8 -*-
"""
informe_landing.py — convierte el contenido de una consulta de landing (JSON) en un informe HTML de una sola marca,
autocontenido (fuentes y logo embebidos), interactivo y listo para abrir, imprimir o publicar.

Marca: «cu» (Control Union, Style Guide v2.0) o «ps» (Peterson Solutions, Brand Guide 2024). Nunca se mezclan:
cada informe carga solo la paleta, la tipografía, el logo y la tagline de su marca (ver marca/<cu|ps>/estilo-*.css).

Uso:  python informe_landing.py ../informe/landings/<sitio>_<pagina>_<AAAA-MM-DD>.json
Sale: el mismo nombre con .html al lado del JSON.

Contenido (decidido por Felipe, 17 nov 2026, vale para todos los informes): solo recomendaciones de la página y del
sitio (SEO y contenido); nunca ajustes de campañas pagas, aunque los datos de SEM se usan como evidencia en el «por qué».
Sin etiqueta de documento ni fecha en la cabecera, sin línea de sitio, sin períodos, sin tarjetas de problema/solución,
sin avisos de paid media, sin tabla «Los números», sin «Límites de los datos» sin texto al pie (solo la tagline) y sin titular: el título es solo el nombre de la landing en español (campo «nombre», p. ej. «Certificación PrimusGFS») y debajo la URL.

Interacción: copiar cada texto a cargar (con contador de caracteres contra el tope), marcar pasos como hechos
(se recuerda en el navegador), filtrar SEO / SEM, plegar el detalle y imprimir con todo desplegado.
"""
import base64, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARCA_DIR = os.path.join(os.path.dirname(HERE), "marca")

MARCAS = {
    "cu": dict(nombre="Control Union", fuente="Sansa Pro", cuerpo="'Ubuntu','Calibri','Carlito',sans-serif",
               fuentes=[("SansaPro-Normal.otf", 400), ("SansaPro-SemiBold.otf", 600)],
               logo="control-union.svg", tagline="THE PROOF TO YOUR PROMISE",
               tokens=dict(accent="#3eb2ed", accent2="#008bcb", navy="#1b1e42", grey="#799495", ink="#4f6566",
                           tint="#eef7fc", tint2="#f3f5f6", hair="#d7dee0", page="#ffffff", warn="#1b1e42"),
               google="Ubuntu:wght@300;400;500;700"),
    "ps": dict(nombre="Peterson Solutions", fuente="Sansa Soft", cuerpo="'Sansa Soft','Ubuntu','Calibri',sans-serif",
               fuentes=[("SansaSoft-Normal.otf", 400), ("SansaSoft-SemiBold.otf", 600), ("SansaSoft-Bold.otf", 700)],
               logo="peterson-solutions-color.svg", tagline="For the world, for ourselves, for our families",
               tokens=dict(accent="#44cbce", accent2="#1b1e42", navy="#1b1e42", grey="#799495", ink="#4f6566",
                           tint="#f4f1e8", tint2="#eae3d2", hair="#dcd6c6", page="#ffffff", warn="#1b1e42", yellow="#f1e747"),
               google="Ubuntu:wght@300;400;500;700"),
}

e = lambda s: html.escape(str(s), quote=True)


def b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode()


def fuentes_css(m, cod):
    out = []
    for archivo, peso in m["fuentes"]:
        out.append(f"@font-face{{font-family:'{m['fuente']}';src:url(data:font/otf;base64,{b64(os.path.join(MARCA_DIR, cod, 'fuentes', archivo))}) format('opentype');font-weight:{peso};font-display:swap}}")
    return "\n".join(out)


def grafico_barras(g, t):
    """Barras por mes (serie 1) con una segunda serie como marcador; el último mes puede ser parcial."""
    meses, series = g["meses"], g["series"]
    W, H, pad_l, pad_b, pad_t = 640, 230, 44, 34, 18
    mx = max(max(s["valores"]) for s in series)
    paso = next(p for p in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 10**9) if p * 4 >= mx)
    top = paso * 4 * 1.08
    bw = (W - pad_l - 20) / len(meses)
    y = lambda v: pad_t + (H - pad_t - pad_b) * (1 - v / top)
    partes = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(g["titulo"])}" class="chart">',
              f'<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
              f'<rect width="6" height="6" fill="{t["accent"]}" opacity=".35"/><line x1="0" y1="0" x2="0" y2="6" stroke="{t["accent"]}" stroke-width="3"/></pattern></defs>']
    for i in range(5):
        v = paso * i
        yy = y(v)
        partes.append(f'<line x1="{pad_l}" x2="{W-10}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{t["hair"]}" stroke-width="1"/>'
                      f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{v:,}</text>'.replace(",", "."))
    s1 = series[0]
    for i, (mes, v) in enumerate(zip(meses, s1["valores"])):
        x = pad_l + i * bw + bw * .18
        parcial = g.get("ultimo_parcial") and i == len(meses) - 1
        fill = "url(#hatch)" if parcial else t["accent"]
        partes.append(f'<rect class="bar" x="{x:.1f}" y="{y(v):.1f}" width="{bw*.64:.1f}" height="{y(0)-y(v):.1f}" rx="3" fill="{fill}">'
                      f'<title>{e(mes)}: {v:,} {e(s1["nombre"])}{" (parcial)" if parcial else ""}</title></rect>'.replace(",", "."))
        partes.append(f'<text x="{x+bw*.32:.1f}" y="{y(v)-6:.1f}" text-anchor="middle" class="val">{v:,}</text>'.replace(",", "."))
        partes.append(f'<text x="{x+bw*.32:.1f}" y="{H-12}" text-anchor="middle" class="ax">{e(mes)}{"*" if parcial else ""}</text>')
    if len(series) > 1:
        s2 = series[1]
        pts = []
        for i, v in enumerate(s2["valores"]):
            cx = pad_l + i * bw + bw * .5
            pts.append(f"{cx:.1f},{y(v):.1f}")
        partes.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{t["navy"]}" stroke-width="2.2"/>')
        for i, v in enumerate(s2["valores"]):
            cx = pad_l + i * bw + bw * .5
            partes.append(f'<circle cx="{cx:.1f}" cy="{y(v):.1f}" r="4.2" fill="#fff" stroke="{t["navy"]}" stroke-width="2.2"><title>{e(meses[i])}: {v:,} {e(s2["nombre"])}</title></circle>'.replace(",", "."))
    partes.append("</svg>")
    ley = f'<span><i style="background:{t["accent"]}"></i>{e(s1["nombre"])}</span>'
    if len(series) > 1:
        ley += f'<span><i class="ln" style="border-color:{t["navy"]}"></i>{e(series[1]["nombre"])}</span>'
    if g.get("ultimo_parcial"):
        ley += '<span class="muted">* mes parcial</span>'
    return "".join(partes), ley


def grafico_posiciones(c, t):
    """Mancuerna de posición media: página A contra página B por búsqueda (menos es mejor)."""
    filas = c["filas"]
    W, fh, pad_l, pad_r = 460, 52, 150, 24
    H = 40 + fh * len(filas)
    mx = max(max(f["a"], f["b"]) for f in filas) * 1.1
    x = lambda p: pad_l + (W - pad_l - pad_r) * p / mx
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{e(c["titulo"])}">']
    for p in (1, 10, 20, 30, 40):
        if p <= mx:
            out.append(f'<line x1="{x(p):.1f}" x2="{x(p):.1f}" y1="18" y2="{H-14}" stroke="{t["hair"]}"/><text x="{x(p):.1f}" y="12" text-anchor="middle" class="ax">{p}</text>')
    out.append(f'<rect x="{x(1):.1f}" y="18" width="{x(10)-x(1):.1f}" height="{H-32}" fill="{t["tint"]}" opacity=".9"/>'
               f'<text x="{(x(1)+x(10))/2:.1f}" y="{H-2}" text-anchor="middle" class="ax">página 1</text>')
    for i, f in enumerate(filas):
        cy = 40 + i * fh
        out.append(f'<text x="{pad_l-14}" y="{cy+4}" text-anchor="end" class="lbl">{e(f["query"])}</text>')
        out.append(f'<line x1="{x(f["a"]):.1f}" x2="{x(f["b"]):.1f}" y1="{cy}" y2="{cy}" stroke="{t["grey"]}" stroke-width="3" stroke-linecap="round" opacity=".45"/>')
        out.append(f'<circle cx="{x(f["a"]):.1f}" cy="{cy}" r="7" fill="{t["accent"]}"><title>{e(c["a"])}: {f["a"]}</title></circle>'
                   f'<text x="{x(f["a"]):.1f}" y="{cy-12}" text-anchor="middle" class="val">{str(f["a"]).replace(".", ",")}</text>')
        out.append(f'<circle cx="{x(f["b"]):.1f}" cy="{cy}" r="7" fill="{t["navy"]}"><title>{e(c["b"])}: {f["b"]}</title></circle>'
                   f'<text x="{x(f["b"]):.1f}" y="{cy-12}" text-anchor="middle" class="val">{str(f["b"]).replace(".", ",")}</text>')
    out.append("</svg>")
    ley = f'<span><i style="background:{t["accent"]};border-radius:50%"></i>{e(c["a"])}</span><span><i style="background:{t["navy"]};border-radius:50%"></i>{e(c["b"])}</span><span class="muted">posición media · menor es mejor</span>'
    return "".join(out), ley


def grafico_ranking(c, t):
    """Barras horizontales (alternativa a la mancuerna cuando no hay dos páginas compitiendo). La fila con
    "destacar": true va en el color de acento; el resto en navy."""
    filas = c["filas"]
    W, fh, pad_l, pad_r = 460, 40, 196, 52
    H = 16 + fh * len(filas)
    mx = max(f["valor"] for f in filas) or 1
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{e(c["titulo"])}">']
    for i, f in enumerate(filas):
        cy = 12 + i * fh
        w = max(3, (W - pad_l - pad_r) * f["valor"] / mx)
        col = t["accent"] if f.get("destacar") else t["navy"]
        v = f"{f['valor']:,}".replace(",", ".")
        out.append(f'<text x="{pad_l-10}" y="{cy+15}" text-anchor="end" class="lbl">{e(f["etiqueta"])}</text>')
        if f.get("nota"):
            out.append(f'<text x="{pad_l-10}" y="{cy+29}" text-anchor="end" class="ax">{e(f["nota"])}</text>')
        out.append(f'<rect class="bar" x="{pad_l}" y="{cy+4}" width="{w:.1f}" height="16" rx="3" fill="{col}"><title>{e(f["etiqueta"])}: {v}</title></rect>'
                   f'<text x="{pad_l+w+6:.1f}" y="{cy+16}" class="val" text-anchor="start">{v}</text>')
    out.append("</svg>")
    ley = f'<span class="muted">{e(c.get("unidad", ""))}</span>'
    return "".join(out), ley


def cambio_html(c, slug, i, j):
    tope = c.get("max")
    cid = f"{slug}-{i}-{j}"
    hoy = f'<div class="hoy"><span class="k">Hoy</span><p>{e(c["hoy"])}</p></div>' if c.get("hoy") else ""
    accion = c.get("accion", "Cargar")
    cont = f'<span class="cnt" data-max="{tope}"></span>' if tope else '<span class="cnt"></span>'
    return (f'<div class="chg {"quitar" if accion.lower().startswith("quitar") else ""}"><div class="campo">{e(c["campo"])}</div>{hoy}'
            f'<div class="new"><span class="k">{e(accion)}</span><p id="{cid}" class="txt">{e(c["cargar"])}</p>'
            f'<div class="tools">{cont}<button class="copy" data-target="{cid}" type="button">Copiar</button></div></div></div>')


def paso_html(p, i, slug):
    cambios = "".join(cambio_html(c, slug, i, j) for j, c in enumerate(p.get("cambios", [])))
    porque = "".join(f"<li>{e(x)}</li>" for x in p["por_que"]) if isinstance(p["por_que"], list) else f"<li>{e(p['por_que'])}</li>"
    nota = f'<p class="nota">{e(p["nota"])}</p>' if p.get("nota") else ""
    cond = f'<span class="chip cond">{e(p["condicion"])}</span>' if p.get("condicion") else ""
    return f"""
<article class="step" data-tipo="{e(p['tipo'])}" data-id="{slug}-p{i}">
  <header class="step-h">
    <label class="done" title="Marcar como hecho"><input type="checkbox" class="chk" data-id="{slug}-p{i}"><span></span></label>
    <button class="step-tog" type="button" aria-expanded="{'true' if i == 1 else 'false'}">
      <span class="num">{i:02d}</span>
      <span class="st"><span class="tt">{e(p['titulo'])}</span><span class="dd">{e(p['donde'])}</span></span>
      <span class="chips"><span class="chip">{e(p['tipo'])}</span>{cond}</span>
      <span class="car" aria-hidden="true"></span>
    </button>
  </header>
  <div class="step-b"{'' if i == 1 else ' hidden'}>
    {nota}
    <div class="chgs">{cambios}</div>
    <div class="why"><span class="k">Por qué</span><ul>{porque}</ul></div>
  </div>
</article>"""


def render(d):
    cod = d["marca"]
    m = MARCAS[cod]
    t = m["tokens"]
    slug = d["slug"]
    logo = b64(os.path.join(MARCA_DIR, cod, "logos", m["logo"]))
    g1, l1 = grafico_barras(d["grafico_mes"], t)
    g2d = d.get("competencia") or d["ranking"]
    g2, l2 = grafico_posiciones(g2d, t) if d.get("competencia") else grafico_ranking(g2d, t)
    kpis = "".join(f'<div class="kpi"><div class="kv">{e(k["valor"])}</div><div class="kl">{e(k["etiqueta"])}</div><div class="kn">{e(k.get("nota", ""))}</div></div>' for k in d["kpis"])
    pasos = "".join(paso_html(p, i + 1, slug) for i, p in enumerate(d["pasos"]))
    medir = "".join(f'<div class="ms"><div class="mw">{e(x["cuando"])}</div><ul>{"".join(f"<li>{e(i)}</li>" for i in x["items"])}</ul></div>' for x in d["medir"])
    tipos = sorted({p["tipo"] for p in d["pasos"]})
    filtros = '<button class="f on" data-f="*" type="button">Todos</button>' + "".join(f'<button class="f" data-f="{e(x)}" type="button">{e(x)}</button>' for x in tipos)
    ps_extra = f"--yellow:{t.get('yellow', t['accent'])};" if cod == "ps" else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>document.documentElement.className+=" js";setTimeout(function(){{[].forEach.call(document.querySelectorAll(".reveal"),function(r){{r.classList.add("in")}})}},2500)</script>
<title>{e(d['nombre'])}</title>
<meta name="description" content="{e(d['url'])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={m['google']}&display=swap" rel="stylesheet">
<style>
{fuentes_css(m, cod)}
:root{{--accent:{t['accent']};--accent2:{t['accent2']};--navy:{t['navy']};--grey:{t['grey']};--ink:{t['ink']};--tint:{t['tint']};--tint2:{t['tint2']};--hair:{t['hair']};--page:{t['page']};{ps_extra}
--fh:'{m['fuente']}','Calibri',sans-serif;--fb:{m['cuerpo']};}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--page);color:var(--ink);font-family:var(--fb);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}}
h1,h2,h3{{font-family:var(--fh);color:var(--navy);font-weight:600;margin:0;letter-spacing:-.01em}}
.topbar{{height:8px;background:var(--accent)}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 24px}}
.brandhead{{display:flex;justify-content:space-between;align-items:center;padding:26px 0 22px;gap:16px}}
.brandhead img{{height:38px;width:auto;display:block}}
.doc{{font-family:var(--fh);font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--grey);text-align:right}}
.hero{{border-top:1px solid var(--hair);padding:36px 0 8px}}
.eyebrow{{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent2);font-weight:700;margin-bottom:14px}}
.hero h1{{font-size:clamp(30px,5vw,46px);line-height:1.06;max-width:820px}}
.url{{display:inline-block;margin-top:12px;font-size:15px;color:var(--grey);word-break:break-all;text-decoration:none;border-bottom:1px solid var(--hair)}}
.url:hover{{color:var(--navy);border-color:var(--accent)}}
.period{{font-size:13px;color:var(--grey);margin-top:8px}}
.ps2{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:30px 0 8px}}
.card{{padding:22px 24px;border-radius:4px;position:relative}}
.card .k{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;margin-bottom:8px;display:block}}
.card p{{margin:0;font-size:17px;line-height:1.45}}
.prob{{background:var(--tint2);border-left:4px solid var(--grey)}}
.prob .k{{color:var(--grey)}} .prob p{{color:var(--navy)}}
.sol{{background:var(--navy);color:#fff}}
.sol .k{{color:var(--accent)}} .sol p{{color:#fff}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin:34px 0 10px;border-top:3px solid var(--accent)}}
.kpi{{padding:18px 18px 4px 0}}
.kpi+.kpi{{padding-left:18px;border-left:1px solid var(--hair)}}
.kv{{font-family:var(--fh);font-size:clamp(24px,3.4vw,34px);font-weight:600;color:var(--navy);line-height:1;font-variant-numeric:tabular-nums;transition:.6s}}
.js .reveal:not(.in) .kv{{opacity:0;transform:translateY(8px)}}
.in .kv{{opacity:1;transform:none}}
.kl{{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--grey);margin-top:9px;font-weight:700}}
.kn{{font-size:13px;color:var(--ink);margin-top:4px}}
section{{padding:44px 0 6px}}
.sec{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px;border-bottom:2px solid var(--accent);padding-bottom:10px;flex-wrap:wrap}}
.sec h2{{font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--navy)}}
.sec .sub{{font-size:14px;color:var(--grey)}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.panel{{border:1px solid var(--hair);border-radius:4px;padding:18px 18px 12px}}
.panel h3{{font-size:16px;margin-bottom:2px}}
.panel .cap{{font-size:13px;color:var(--grey);margin-bottom:8px}}
.chart{{width:100%;height:auto;display:block}}
.chart .ax{{font-size:11px;fill:var(--grey);font-family:var(--fb)}}
.chart .val{{font-size:11.5px;fill:var(--navy);font-weight:700;font-family:var(--fb)}}
.chart .lbl{{font-size:12.5px;fill:var(--navy);font-family:var(--fb)}}
.chart .bar{{transform-origin:bottom;transform-box:fill-box;transition:transform .8s cubic-bezier(.2,.7,.2,1)}}
.js .reveal:not(.in) .chart .bar{{transform:scaleY(0)}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--ink);margin-top:6px}}
.legend i{{display:inline-block;width:11px;height:11px;margin-right:6px;vertical-align:-1px;border-radius:2px}}
.legend i.ln{{height:0;border-top:2.5px solid;width:16px;vertical-align:3px;border-radius:0}}
.muted{{color:var(--grey)}}
.alert{{margin:22px 0 0;padding:18px 22px;border:1px solid var(--navy);border-left:6px solid var(--navy);border-radius:4px;background:#fff}}
.alert .ak{{font-family:var(--fh);font-weight:600;color:var(--navy);font-size:17px;margin-bottom:4px}}
.alert p{{margin:0}}
.toolbar{{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:14px}}
.filters{{display:flex;gap:8px}}
.f{{font:inherit;font-size:13px;padding:6px 14px;border-radius:999px;border:1px solid var(--hair);background:#fff;color:var(--navy);cursor:pointer}}
.f.on{{background:var(--navy);color:#fff;border-color:var(--navy)}}
.prog{{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--grey);min-width:220px}}
.bar-o{{flex:1;height:8px;background:var(--tint2);border-radius:99px;overflow:hidden}}
.bar-i{{height:100%;width:0;background:var(--accent);transition:width .4s}}
.acts{{display:flex;gap:8px}}
.lnk{{font:inherit;font-size:13px;background:none;border:none;color:var(--accent2);cursor:pointer;padding:4px 2px;text-decoration:underline;text-underline-offset:3px}}
.step{{border:1px solid var(--hair);border-radius:4px;margin-bottom:12px;background:#fff;transition:box-shadow .2s,border-color .2s}}
.step:hover{{box-shadow:0 2px 14px rgba(27,30,66,.07)}}
.step.is-done{{border-color:var(--accent)}}
.step.is-done .tt{{text-decoration:line-through;text-decoration-color:var(--accent);color:var(--grey)}}
.step-h{{display:flex;align-items:stretch}}
.done{{display:flex;align-items:center;padding:0 0 0 18px;cursor:pointer}}
.done input{{position:absolute;opacity:0;pointer-events:none}}
.done span{{width:22px;height:22px;border:2px solid var(--hair);border-radius:4px;display:grid;place-items:center;transition:.2s}}
.done input:checked+span{{background:var(--accent);border-color:var(--accent)}}
.done input:checked+span:after{{content:"";width:6px;height:11px;border:solid #fff;border-width:0 2.5px 2.5px 0;transform:rotate(45deg) translate(-1px,-1px)}}
.done input:focus-visible+span{{outline:2px solid var(--navy);outline-offset:2px}}
.step-tog{{flex:1;display:flex;align-items:center;gap:16px;padding:16px 18px;background:none;border:none;font:inherit;color:inherit;text-align:left;cursor:pointer}}
.num{{font-family:var(--fh);font-size:26px;font-weight:600;color:var(--accent);line-height:1;min-width:34px}}
.st{{flex:1;display:flex;flex-direction:column;gap:3px;min-width:0}}
.tt{{font-family:var(--fh);font-size:18px;font-weight:600;color:var(--navy);line-height:1.25}}
.dd{{font-size:13px;color:var(--grey);word-break:break-word}}
.chips{{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}}
.chip{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;padding:3px 9px;border:1px solid var(--navy);color:var(--navy);border-radius:3px;white-space:nowrap}}
.chip.cond{{border-color:var(--grey);color:var(--grey)}}
.car{{width:10px;height:10px;border-right:2px solid var(--grey);border-bottom:2px solid var(--grey);transform:rotate(45deg);transition:.25s;margin:0 4px 4px}}
.step-tog[aria-expanded=true] .car{{transform:rotate(-135deg);margin-bottom:-4px}}
.step-b{{padding:0 22px 20px 74px}}
.nota{{margin:0 0 12px;font-size:14px;color:var(--navy);background:var(--tint);padding:10px 14px;border-radius:3px}}
.chg{{display:grid;grid-template-columns:150px 1fr;gap:4px 18px;padding:14px 0;border-top:1px solid var(--hair)}}
.chg:first-child{{border-top:none;padding-top:4px}}
.campo{{grid-row:span 2;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--grey);font-weight:700;padding-top:3px}}
.hoy,.new{{grid-column:2;min-width:0}}
.hoy p,.new p,.campo{{overflow-wrap:anywhere}}
.k{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:var(--grey)}}
.hoy p{{margin:2px 0 8px;color:var(--grey);font-size:14px;text-decoration:line-through;text-decoration-color:rgba(121,148,149,.5)}}
.new{{background:var(--tint);border-left:3px solid var(--accent);padding:10px 14px;border-radius:0 3px 3px 0}}
.chg.quitar .new{{background:var(--tint2);border-left-color:var(--grey)}}
.chg.quitar .txt{{color:var(--ink)}}
.new .k{{color:var(--accent2)}}
.txt{{margin:3px 0 8px;color:var(--navy);font-size:15px;font-weight:500;word-break:break-word}}
.tools{{display:flex;justify-content:flex-end;align-items:center;gap:12px}}
.cnt{{font-size:12px;color:var(--grey);font-variant-numeric:tabular-nums}}
.cnt.over{{color:#b3261e;font-weight:700}}
.copy{{font:inherit;font-size:12.5px;padding:5px 12px;border-radius:3px;border:1px solid var(--navy);background:#fff;color:var(--navy);cursor:pointer;transition:.15s}}
.copy:hover{{background:var(--navy);color:#fff}}
.copy.ok{{background:var(--accent);border-color:var(--accent);color:#fff}}
.why{{margin-top:12px}}
.why ul{{margin:6px 0 0;padding-left:18px}}
.why li{{margin-bottom:6px;font-size:14.5px}}
table{{width:100%;border-collapse:collapse;font-size:14.5px}}
th{{text-align:left;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--grey);border-bottom:2px solid var(--navy);padding:8px 10px 8px 0}}
td{{padding:10px 10px 10px 0;border-bottom:1px solid var(--hair);vertical-align:top}}
td:first-child{{font-weight:700;color:var(--navy);white-space:nowrap}}
td:last-child{{font-variant-numeric:tabular-nums;color:var(--navy)}}
.tblw{{overflow-x:auto}}
.medir{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}
.ms{{background:var(--tint2);padding:18px 20px;border-radius:4px;border-top:3px solid var(--accent)}}
.mw{{font-family:var(--fh);font-weight:600;color:var(--navy);font-size:17px;margin-bottom:6px}}
.ms ul{{margin:0;padding-left:18px}} .ms li{{margin-bottom:6px;font-size:14.5px}}
details{{border:1px solid var(--hair);border-radius:4px;padding:14px 18px}}
summary{{cursor:pointer;font-family:var(--fh);font-weight:600;color:var(--navy);font-size:16px}}
details ul{{margin:12px 0 0;padding-left:18px}} details li{{margin-bottom:8px;font-size:14.5px}}
footer{{margin-top:56px;position:relative;padding:22px 0 34px}}
.footbar{{height:10px;background:var(--navy);margin-left:calc((100% - min(1040px,100%))/2 + 24px)}}
.foot{{display:flex;justify-content:flex-end;align-items:flex-end;gap:16px;flex-wrap:wrap;padding-top:18px}}
.tag{{font-family:var(--fh);font-size:13px;letter-spacing:.22em;color:var(--navy);font-weight:600}}
.fmeta{{font-size:12.5px;color:var(--grey)}}
.toast{{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(20px);background:var(--navy);color:#fff;padding:10px 18px;border-radius:4px;font-size:14px;opacity:0;transition:.25s;pointer-events:none;z-index:5}}
.toast.on{{opacity:1;transform:translateX(-50%)}}
.reveal{{transition:opacity .6s,transform .6s}}
.js .reveal:not(.in){{opacity:0;transform:translateY(14px)}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}.reveal{{opacity:1;transform:none}}.kv{{opacity:1;transform:none}}.chart .bar{{transform:none}}}}
@media (max-width:760px){{
 .wrap{{padding:0 16px}} .ps2,.charts{{grid-template-columns:1fr}}
 .kpis{{grid-template-columns:1fr 1fr}} .kpi:nth-child(3){{padding-left:0;border-left:none}} .kpi{{border-top:1px solid var(--hair)}}
 .step-b{{padding:0 16px 18px}} .chg{{grid-template-columns:1fr}} .campo{{grid-row:auto}} .hoy,.new{{grid-column:1}}
 .chips{{display:none}} .brandhead img{{height:30px}} .doc{{font-size:10px}}
 .footbar{{margin-left:16px}}
}}
@media print{{
 .toolbar,.copy,.done,.toast{{display:none!important}} .step-b{{display:block!important}} .step{{break-inside:avoid}}
 .reveal,.kv,.chart .bar{{opacity:1!important;transform:none!important}} body{{font-size:12px}} section{{padding-top:24px}}
 .topbar,.sol,.footbar,.kpis{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
}}
</style></head>
<body>
<div class="topbar"></div>
<div class="wrap">
  <div class="brandhead"><img src="data:image/svg+xml;base64,{logo}" alt="{e(m['nombre'])}"></div>

  <div class="hero reveal">
    <h1>{e(d['nombre'])}</h1>
    <a class="url" href="{e(d['url'])}" target="_blank" rel="noopener">{e(d['url'])}</a>
    <div class="kpis">{kpis}</div>
  </div>

  <section class="reveal">
    <div class="sec"><h2>Diagnóstico</h2><span class="sub">{e(d['diag_sub'])}</span></div>
    <div class="charts">
      <div class="panel"><h3>{e(d['grafico_mes']['titulo'])}</h3><div class="cap">{e(d['grafico_mes']['cap'])}</div>{g1}<div class="legend">{l1}</div></div>
      <div class="panel"><h3>{e(g2d['titulo'])}</h3><div class="cap">{e(g2d['cap'])}</div>{g2}<div class="legend">{l2}</div></div>
    </div>
  </section>

  <section id="pasos">
    <div class="sec"><h2>Paso a paso</h2><span class="sub">El texto exacto a cargar, en orden</span></div>
    <div class="toolbar">
      <div class="filters">{filtros if len(tipos) > 1 else ""}</div>
      <div class="prog"><span id="pc">0 de {len(d['pasos'])}</span><div class="bar-o"><div class="bar-i" id="pb"></div></div></div>
      <div class="acts"><button class="lnk" id="openall" type="button">Desplegar todo</button><button class="lnk" onclick="window.print()" type="button">Imprimir</button></div>
    </div>
    {pasos}
  </section>

  <section class="reveal">
    <div class="sec"><h2>Qué medir y cuándo</h2><span class="sub">{e(d['medir_sub'])}</span></div>
    <div class="medir">{medir}</div>
  </section>
</div>
<footer>
  <div class="footbar"></div>
  <div class="wrap foot"><div class="tag">{e(m['tagline'])}</div></div>
</footer>
<div class="toast" id="toast">Copiado</div>
<script>
(function(){{
  var KEY='landing:{slug}';
  function load(){{try{{return JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{return {{}}}}}}
  function save(s){{try{{localStorage.setItem(KEY,JSON.stringify(s))}}catch(e){{}}}}
  var st=load(), chks=[].slice.call(document.querySelectorAll('.chk'));
  function prog(){{var n=chks.filter(function(c){{return c.checked}}).length;
    document.getElementById('pc').textContent=n+' de '+chks.length+' hechos';
    document.getElementById('pb').style.width=(100*n/chks.length)+'%';}}
  chks.forEach(function(c){{c.checked=!!st[c.dataset.id];c.closest('.step').classList.toggle('is-done',c.checked);
    c.addEventListener('change',function(){{st[c.dataset.id]=c.checked;save(st);c.closest('.step').classList.toggle('is-done',c.checked);prog();}});}});
  prog();
  document.querySelectorAll('.step-tog').forEach(function(b){{b.addEventListener('click',function(){{
    var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!o));b.closest('.step').querySelector('.step-b').hidden=o;}});}});
  var all=false;document.getElementById('openall').addEventListener('click',function(){{all=!all;
    document.querySelectorAll('.step-tog').forEach(function(b){{b.setAttribute('aria-expanded',String(all));b.closest('.step').querySelector('.step-b').hidden=!all;}});
    this.textContent=all?'Plegar todo':'Desplegar todo';}});
  document.querySelectorAll('.f').forEach(function(f){{f.addEventListener('click',function(){{
    document.querySelectorAll('.f').forEach(function(x){{x.classList.remove('on')}});f.classList.add('on');
    document.querySelectorAll('.step').forEach(function(s){{s.style.display=(f.dataset.f==='*'||s.dataset.tipo===f.dataset.f)?'':'none'}});}});}});
  document.querySelectorAll('.new').forEach(function(n){{var t=n.querySelector('.txt'),c=n.querySelector('.cnt');if(!c)return;
    var L=t.textContent.length,M=parseInt(c.dataset.max||'0',10);c.textContent=M?L+' / '+M+' caracteres':L+' caracteres';if(M&&L>M)c.classList.add('over');}});
  var toast=document.getElementById('toast');
  function flash(msg){{toast.textContent=msg;toast.classList.add('on');setTimeout(function(){{toast.classList.remove('on')}},1400);}}
  document.querySelectorAll('.copy').forEach(function(b){{b.addEventListener('click',function(){{
    var txt=document.getElementById(b.dataset.target).textContent;
    function ok(){{b.classList.add('ok');b.textContent='Copiado';flash('Texto copiado');setTimeout(function(){{b.classList.remove('ok');b.textContent='Copiar'}},1500);}}
    if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(txt).then(ok,function(){{fb(txt);ok();}});}}else{{fb(txt);ok();}}
    function fb(x){{var a=document.createElement('textarea');a.value=x;document.body.appendChild(a);a.select();try{{document.execCommand('copy')}}catch(e){{}}a.remove();}}
  }});}});
  var io='IntersectionObserver' in window?new IntersectionObserver(function(es){{es.forEach(function(x){{if(x.isIntersecting){{x.target.classList.add('in');io.unobserve(x.target);}}}})}},{{threshold:.12}}):null;
  document.querySelectorAll('.reveal').forEach(function(r){{io?io.observe(r):r.classList.add('in')}});
}})();
</script>
</body></html>"""


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ruta = sys.argv[1]
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    if d["marca"] not in MARCAS:
        raise SystemExit("marca debe ser «cu» o «ps»")
    salida = os.path.splitext(ruta)[0] + ".html"
    with open(salida, "w", encoding="utf-8") as f:
        f.write(render(d))
    print(salida, f"{os.path.getsize(salida)/1024:.0f} KB")


if __name__ == "__main__":
    main()
