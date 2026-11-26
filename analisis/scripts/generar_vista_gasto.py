# -*- coding: utf-8 -*-
"""
generar_vista_gasto.py — vista interactiva del gasto de Google Ads: cliente → país → campaña → grupo,
con gasto mensual y diario, participación y clics. Un solo HTML autónomo con los datos embebidos,
identidad MarComms (agencia interna), sin servidor. Sale a informe/vista-gasto.html
"""
import base64, json, os, re
from informe_util import hoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
D = json.load(open(os.path.join(INF, "datos_gasto_actual.json"), encoding="utf-8"))
LOGO = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "Marcomms SEO-SEM", "public", "marca", "marcomms-horizontal-600.png")
logo_b64 = base64.b64encode(open(LOGO, "rb").read()).decode() if os.path.exists(LOGO) else ""


def unidad(nombre):
    """País de la campaña por palabra clave, en cualquier parte del nombre: los prefijos cambian seguido
    («PCU Argentina» → «PCU Tech» → «PCU - Argentina»). «Tech» es la unidad ISO 27001 de Argentina."""
    # naming estándar del equipo (skill paid-media-pcu): MARCA_PAÍS_TIPO_NORMA_IDIOMA, p. ej. CU_US_SEARCH_GPFS-2026_EN
    m = re.match(r"^(?:CUC|CU|PS|PCU)_([A-Z]{2})_", nombre)
    if m:
        return {"US": "CUC USA", "CA": "Canadá", "MX": "México", "AR": "Argentina", "ES": "España", "PT": "Portugal",
                "BR": "Brasil", "CL": "Chile", "PE": "Perú"}.get(m.group(1), "Sin asignar")
    for clave, u in [("España", "España"), ("Portugal", "Portugal"), ("Canada", "Canadá"), ("CUC USA", "CUC USA"), ("United States", "CUC USA"),
                     ("Argentina", "Argentina"), ("PCU Tech", "Argentina")]:
        if clave in nombre:
            return u
    return "Sin asignar"


filas = D["filas"]
for f in filas:
    f["unidad"] = unidad(f["campana"])
    f["campana_corta"] = re.sub(r"\s*-\s*search\s*$", "", f["campana"], flags=re.I)
import datetime as _dt
_d, _h = _dt.date.fromisoformat(D["desde"]), _dt.date.fromisoformat(D["hasta"])
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
etiqueta = (f"{_d.day} → {_h.day} {MESES[_h.month-1]} {_h.year}" if (_d.year, _d.month) == (_h.year, _h.month)
            else f"{_d.day} {MESES[_d.month-1]} → {_h.day} {MESES[_h.month-1]} {_h.year}")
mes_txt = f"{MESES[_h.month-1]} {_h.year}"
import calendar as _cal
dias_mes = _cal.monthrange(_h.year, _h.month)[1]
datos = dict(ventana=etiqueta, dias=D["dias"], dias_mes=dias_mes, filas=filas, generado=hoy(), mes=mes_txt)

html = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarComms · Gasto en Google Ads</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#1b1e42;--blue:#009ceb;--ink:#4f6566;--grey:#799495;--tint:#f3f6f9;--tint2:#e6edf3;--hair:#d7dee5;--bg:#f7f9fb}}
*{{box-sizing:border-box}}body{{margin:0;font-family:"DM Sans",system-ui,sans-serif;background:var(--bg);color:var(--ink);font-size:14px}}
.mono{{font-family:"JetBrains Mono",Consolas,monospace;font-variant-numeric:tabular-nums}}
header{{background:#fff;border-bottom:3px solid var(--blue);padding:16px 28px;display:flex;align-items:center;justify-content:space-between;gap:20px}}
header img{{height:34px}} header .t{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:600}}
header h1{{margin:2px 0 0;font-size:20px;color:var(--navy);font-weight:700}}
main{{max-width:1180px;margin:0 auto;padding:22px 28px 60px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}}
.kpi{{background:#fff;border:1px solid var(--hair);border-radius:12px;padding:14px 16px}}
.kpi .n{{font-size:24px;font-weight:700;color:var(--navy)}}.kpi .l{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--grey);margin-top:4px}}
.bar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px}}
select,input{{font:inherit;border:1px solid var(--hair);background:#fff;border-radius:8px;padding:7px 10px;color:var(--navy)}}
.seg{{display:inline-flex;border:1px solid var(--hair);border-radius:8px;overflow:hidden;background:#fff}}
.seg button{{font:inherit;border:0;background:transparent;padding:7px 12px;color:var(--ink);cursor:pointer}}.seg button.on{{background:var(--navy);color:#fff}}
.node{{background:#fff;border:1px solid var(--hair);border-radius:12px;margin-bottom:10px;overflow:hidden}}
.row{{display:grid;grid-template-columns:22px 1fr 120px 120px 90px 90px 70px 120px;gap:10px;align-items:center;padding:10px 14px;cursor:pointer;border-top:1px solid var(--tint2)}}
.row:first-child{{border-top:0}} .row:hover{{background:var(--tint)}}
.row .name{{font-weight:600;color:var(--navy)}} .row .sub{{font-size:11px;color:var(--grey);font-weight:400}}
.row .num{{text-align:right}} .lvl1>.row{{background:var(--tint)}} .lvl1>.row .name{{font-size:15px}}
.lvl2>.row{{padding-left:34px}} .lvl3>.row{{padding-left:54px}} .lvl4>.row{{padding-left:74px;cursor:default}} .lvl4>.row:hover{{background:#fff}}
.chev{{width:14px;height:14px;display:inline-block;transition:transform .15s;color:var(--grey)}} .open>.row .chev{{transform:rotate(90deg)}}
.kids{{display:none}} .open>.kids{{display:block}}
.track{{height:6px;background:var(--tint2);border-radius:3px;overflow:hidden}} .fill{{height:6px;background:var(--blue)}} .lvl1 .fill{{background:var(--navy)}}
.head{{display:grid;grid-template-columns:22px 1fr 120px 120px 90px 90px 70px 120px;gap:10px;padding:0 14px 6px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--grey)}}
.head .num{{text-align:right}} .conv{{color:var(--blue);font-weight:600}} .pres{{color:var(--grey)}} .semaforo{{display:inline-block;min-width:52px;padding:2px 8px;border-radius:999px;font-weight:600;text-align:center}} .s-rojo{{background:#fdecec;color:#b4232c}} .s-verde{{background:#e7f6ee;color:#1d7a46}} .s-gris{{background:var(--tint2);color:var(--grey)}} .leyenda{{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--grey);margin:0 0 12px}} .leyenda b{{font-weight:600}}
footer{{max-width:1180px;margin:0 auto;padding:0 28px 30px;font-size:11px;color:var(--grey)}}
@media(max-width:900px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.row,.head{{grid-template-columns:18px 1fr 110px 80px}}.row>:nth-child(n+6),.head>:nth-child(n+6){{display:none}}}}
</style></head><body>
<header><div><div class="t">MarComms · Paid media · Google Ads</div><h1>Gasto por cliente, país, campaña y grupo</h1></div>
{f'<img src="data:image/png;base64,{logo_b64}" alt="MarComms">' if logo_b64 else ''}</header>
<main>
 <div class="kpis" id="kpis"></div>
 <div class="bar">
  <div class="seg" id="modo"><button data-m="mes" class="on">Mes ({datos["mes"]})</button><button data-m="dia">Por día</button></div>
  <select id="cliente"><option value="">Todos los clientes</option></select>
  <select id="pais"><option value="">Todos los países</option></select>
  <input id="q" placeholder="Buscar campaña o grupo…" style="flex:1;min-width:200px">
  <button id="exp" style="font:inherit;border:1px solid var(--hair);background:#fff;border-radius:8px;padding:7px 12px;cursor:pointer;color:var(--navy)">Expandir todo</button>
 </div>
 <div class="leyenda"><span><b style="color:#1d7a46">● Verde</b> gasta dentro de su presupuesto diario</span><span><b style="color:#b4232c">● Rojo</b> gasta más de un 5% por encima, o no gasta nada</span><span><b>● Gris</b> campaña pausada o eliminada</span></div>
 <div class="head"><span></span><span>Nivel</span><span class="num" id="hp">Presupuesto</span><span class="num" id="hg">Gasto del mes</span><span class="num" id="hr">Consumido</span><span class="num">Clics</span><span class="num">Conv.</span><span></span></div>
 <div id="arbol"></div>
</main>
<footer>Mes en curso: {datos["ventana"]} ({datos["dias"]} días con datos), leído por API de Google Ads. «Mes» = suma de esos días; «día» = gasto ÷ {datos["dias"]}. «Presupuesto» = presupuesto diario configurado en Google Ads (snapshot {D.get("snapshot", "")}); en la vista mensual, × {datos["dias_mes"]} días del mes = presupuesto mensual, y «Consumido» = qué parte de ese presupuesto mensual ya se gastó hasta el {_h.day}. En la vista por día se compara gasto por día contra presupuesto por día. Semáforo por ritmo de gasto: rojo si la campaña gasta por día más de un 5% por encima de su presupuesto o no gasta nada; verde en el medio. Solo cuenta el presupuesto de campañas activas. La participación es sobre el nivel superior. Generado el {datos["generado"]}. Documento interno de MarComms.</footer>
<script>
const DATA = {json.dumps(datos, ensure_ascii=False)};
const DIAS = DATA.dias, DIAS_MES = DATA.dias_mes; let modo = 'mes';
const ars = v => 'ARS ' + Math.round(v).toLocaleString('es-AR');
const val = v => modo === 'mes' ? v : v / DIAS;
const pres = p => p == null ? null : (modo === 'mes' ? p * DIAS_MES : p);  // presupuesto diario de la cuenta; en la vista mensual, presupuesto del mes completo (× días del mes)
const ratio = n => !n.pres ? null : (modo === 'mes' ? n.coste / (n.pres * DIAS_MES) : n.coste / DIAS / n.pres);  // mes: consumido del presupuesto mensual; día: gasto/día vs presupuesto/día
// semáforo por ritmo de gasto (gasto por día contra presupuesto por día), igual en las dos vistas
const semaforo = n => !n.pres ? 's-gris' : (n.coste <= 0 || n.coste / DIAS > n.pres * 1.05) ? 's-rojo' : 's-verde';
function build(rows){{
  const tree = {{}};
  for (const r of rows){{
    const a = tree[r.marca] ??= {{coste:0,clics:0,conv:0,kids:{{}}}};
    const b = a.kids[r.unidad] ??= {{coste:0,clics:0,conv:0,kids:{{}}}};
    const c = b.kids[r.campana_corta] ??= {{coste:0,clics:0,conv:0,kids:{{}}}};
    const d = c.kids[r.grupo] ??= {{coste:0,clics:0,conv:0,pres:null}};
    for (const n of [a,b,c,d]){{ n.coste += r.coste; n.clics += r.clics; n.conv += r.conv; }}
    c.estado = r.campana_estado;
    if (r.presupuesto_dia != null && !c.presVisto){{ c.presVisto = true; c.pres = (c.pres||0) + r.presupuesto_dia; b.pres = (b.pres||0) + r.presupuesto_dia; a.pres = (a.pres||0) + r.presupuesto_dia; }}
  }}
  return tree;
}}
function node(name, n, parentCoste, lvl, sub){{
  const share = parentCoste ? n.coste/parentCoste*100 : 100;
  const kids = n.kids ? Object.entries(n.kids).sort((x,y)=>y[1].coste-x[1].coste) : [];
  const chev = kids.length ? '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 6l6 6-6 6"/></svg>' : '';
  return `<div class="node lvl${{lvl}}${{lvl===1?' open':''}}"><div class="row" onclick="this.parentNode.classList.toggle('open')">
    <span>${{chev}}</span><span class="name">${{name}}${{sub?` <span class="sub">${{sub}}</span>`:''}}</span>
    <span class="num mono pres">${{n.pres == null ? '' : ars(pres(n.pres))}}</span><span class="num mono">${{ars(val(n.coste))}}</span><span class="num mono">${{n.pres ? `<span class="semaforo ${{semaforo(n)}}">${{(ratio(n)*100).toFixed(0)}}%</span>` : (n.estado && n.estado !== 'ENABLED' ? '<span class="semaforo s-gris">'+(n.estado === 'REMOVED' ? 'eliminada' : 'pausada')+'</span>' : '')}}</span>
    <span class="num mono">${{n.clics.toLocaleString('es-AR')}}</span><span class="num mono ${{n.conv?'conv':''}}">${{Math.round(n.conv)}}</span>
    <span><div class="track"><div class="fill" style="width:${{share}}%"></div></div></span></div>
    ${{kids.length?`<div class="kids">${{kids.map(([k,v])=>node(k,v,n.coste,lvl+1, v.kids? (lvl===1?`${{Object.keys(v.kids).length}} campañas`:(lvl===2?`${{Object.keys(v.kids).length}} grupos`:'')):'')).join('')}}</div>`:''}}
  </div>`;
}}
function render(){{
  const cli = document.getElementById('cliente').value, pais = document.getElementById('pais').value, q = document.getElementById('q').value.toLowerCase();
  const rows = DATA.filas.filter(r => (!cli||r.marca===cli) && (!pais||r.unidad===pais) && (!q||r.campana_corta.toLowerCase().includes(q)||r.grupo.toLowerCase().includes(q)));
  const tree = build(rows); const tot = rows.reduce((s,r)=>s+r.coste,0), clics = rows.reduce((s,r)=>s+r.clics,0), conv = rows.reduce((s,r)=>s+r.conv,0);
  const presDia = Object.values(tree).reduce((s,n)=>s+(n.pres||0),0);
  document.getElementById('kpis').innerHTML = [[ars(tot),'gasto del mes · '+DATA.ventana],[ars(tot/DIAS),'gasto por día · presupuesto '+ars(presDia)+' ('+(presDia?(tot/DIAS/presDia*100).toFixed(0):'—')+'%)'],[clics.toLocaleString('es-AR'),'clics'],[Math.round(conv)+' · '+(conv?ars(tot/conv):'—'),'conversiones · coste por conv.']]
    .map(([n,l])=>`<div class="kpi"><div class="n mono">${{n}}</div><div class="l">${{l}}</div></div>`).join('');
  document.getElementById('hg').textContent = modo==='mes' ? 'Gasto del mes' : 'Gasto / día';
  document.getElementById('hp').textContent = modo==='mes' ? 'Presup. × '+DIAS_MES+' d' : 'Presup. / día';
  document.getElementById('hr').textContent = modo==='mes' ? 'Consumido' : 'Gasto / presup.';
  document.getElementById('arbol').innerHTML = Object.entries(tree).sort((x,y)=>y[1].coste-x[1].coste).map(([k,v])=>node(k,v,tot,1,`${{Object.keys(v.kids).length}} países`)).join('');
}}
const clientes = [...new Set(DATA.filas.map(r=>r.marca))], paises = [...new Set(DATA.filas.map(r=>r.unidad))].sort();
document.getElementById('cliente').innerHTML += clientes.map(c=>`<option>${{c}}</option>`).join('');
document.getElementById('pais').innerHTML += paises.map(c=>`<option>${{c}}</option>`).join('');
for (const el of ['cliente','pais','q']) document.getElementById(el).addEventListener('input', render);
document.querySelectorAll('#modo button').forEach(b=>b.addEventListener('click',()=>{{modo=b.dataset.m;document.querySelectorAll('#modo button').forEach(x=>x.classList.toggle('on',x===b));render();}}));
let allOpen=false; document.getElementById('exp').addEventListener('click',()=>{{allOpen=!allOpen;document.querySelectorAll('.node').forEach(n=>n.classList.toggle('open',allOpen||n.classList.contains('lvl1')));document.getElementById('exp').textContent=allOpen?'Contraer todo':'Expandir todo';}});
render();
</script></body></html>'''
open(os.path.join(INF, "vista-gasto.html"), "w", encoding="utf-8").write(html)
print("-> informe/vista-gasto.html")
