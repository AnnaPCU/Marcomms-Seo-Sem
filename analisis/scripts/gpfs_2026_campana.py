# -*- coding: utf-8 -*-
"""
gpfs_2026_campana.py — campaña Search de Control Union para The Global Produce & Floral Show 2026 (IFPA)
(Orlando, 14 a 16 de octubre; expo abierta 15 y 16, de 10 a 17 h; stand #851).

Versión 3 (6 oct 2026), con las correcciones de Felipe:
  · una sola campaña, «CU United States - Evento IFPA - Search», EE.UU. + México + Canadá sin ajustes por país
  · ARS 10.000 por día, sin fecha de fin, Maximizar clics (sin CPC máximo), solo inglés, sin plantilla de seguimiento
  · sin grupo de marca y sin tocar las campañas que ya existen
  · copy: siempre «Control Union» (ningún país), más directo a la necesidad de quien va al show, invita a la landing
  · recursos: sitelinks por programa a la landing, textos destacados y fragmento; sin formulario, llamada ni imágenes
Valida largos, marca y negativas, escribe el plan JSON y genera los CSV con build_editor_csv.py de la skill paid-media-pcu:
  campanas/gpfs-2026/final/   campanas.csv, ubicaciones.csv, grupos.csv, keywords.csv, negativas.csv, anuncios.csv,
                              sitelinks.csv y todo-junto.csv (importación en un solo archivo)
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "campanas", "gpfs-2026", "final")
LANDING = "https://northamerica.controlunion.com/fresh-produce-certification-expertise/"  # URL final de todo, salvo el grupo del check
# Link público del Typeform «Certification Check». Mientras esté vacío, el grupo GPFS_CHECK y su sitelink no entran al CSV.
TYPEFORM_URL = "https://form.typeform.com/to/VisEEU2n"
SKILL = os.path.join(os.environ.get("APPDATA", ""), "Claude", "local-agent-mode-sessions", "skills-plugin")

CAMPANA = "CU United States - IFPA event - Search"
PRESUPUESTO_DIA = 10000
ESTRATEGIA = "Maximize clicks"
IDIOMAS = ["en"]
UBICACIONES = ["United States", "Mexico", "Canada"]
GEO_ID = {"United States": "2840", "Mexico": "2484", "Canada": "2124"}  # IDs de Google: «Mexico» solo podría confundirse con el Estado de México

# ------------------------------------------------------------------ grupos y keywords (texto, concordancia)
GRUPOS = {
    "GPFS_EVENTO": dict(
        intencion="Busca el show por su nombre: va a ir o está decidiendo.",
        kw=[
            ("global produce and floral show 2026", "Exact"),
            ("global produce and floral show", "Exact"),
            ("global produce and floral show", "Phrase"),
            ("the global produce and floral show", "Exact"),
            ("ifpa global produce and floral show", "Phrase"),
            ("gpfs 2026", "Exact"),
            ("ifpa 2026", "Exact"),
            ("ifpa global show", "Phrase"),
            ("ifpa global produce show", "Phrase"),
            ("ifpa show 2026", "Phrase"),
            ("global produce show 2026", "Phrase"),
            ("fresh summit 2026", "Exact"),
        ],
    ),
    "GPFS_ORLANDO": dict(
        intencion="Busca la feria por ciudad o por rubro, sin saber el nombre exacto.",
        kw=[
            ("ifpa orlando 2026", "Exact"),
            ("ifpa orlando", "Phrase"),
            ("ifpa 2026 orlando", "Phrase"),
            ("produce show orlando", "Phrase"),
            ("produce expo orlando", "Phrase"),
            ("produce trade show orlando", "Phrase"),
            ("floral trade show orlando", "Phrase"),
            ("produce trade show 2026", "Phrase"),
            ("fresh produce show october 2026", "Phrase"),
        ],
    ),
    "GPFS_EXPOSITORES": dict(
        intencion="Arma su recorrido por la expo: lista de expositores y plano.",
        kw=[
            ("global produce and floral show exhibitors", "Phrase"),
            ("global produce and floral show 2026 exhibitor list", "Phrase"),
            ("gpfs 2026 exhibitors", "Phrase"),
            ("gpfs exhibitor list", "Phrase"),
            ("ifpa exhibitor list", "Phrase"),
            ("ifpa 2026 exhibitors", "Phrase"),
            ("global show exhibitor list", "Phrase"),
            ("ifpa expo floor plan", "Phrase"),
        ],
    ),
}

# ------------------------------------------------------------------ anuncios (RSA). Sin «IFPA» ni el nombre del show en el texto
# (marca de un tercero). Siempre «Control Union», sin país. Los tres primeros títulos de cada anuncio se fijan en posición 1.
H_EVENTO = ["Control Union at Booth #851", "Going to the Show? Booth #851", "Booth #851, Expo Oct 15-16"]
# banco 1: la necesidad de quien va al show
H_NECESIDAD = [
    "Buyer Requires Certification?", "Too Many Audits Every Year?", "One Body for All Your Audits", "Exporting Fresh Produce?",
    "Retailer Audit Coming Up?", "PrimusGFS or GLOBALG.A.P.?", "Explore Our Produce Programs", "See What We Certify",
    "Plan Your Visit to Booth #851", "Fresh Produce Certification", "200+ Certification Programs", "100+ Years of Certification",
]
# banco 2: los programas que la landing dice que Control Union certifica
H_PROGRAMAS = [
    "Food Safety Audits for Growers", "PrimusGFS Certification", "GLOBALG.A.P. Certification", "USDA NOP Organic Certification",
    "SMETA and GRASP Audits", "BRCGS Certification", "Florverde Sustainable Flowers", "Fair Trade USA Certification",
    "Expo Floor Open Oct 15-16", "Meet Control Union in Orlando", "Present in 80+ Countries", "Control Union Certifications",
]
D_A = [
    "Going to the produce show in Orlando? See our certification programs before you visit.",
    "We certify and audit fresh produce: PrimusGFS, GLOBALG.A.P., USDA NOP, IFS, BRCGS.",
    "Buyers asking for new audits? Explore the programs we certify for growers and packers.",
    "Certification body with 100+ years of experience and a presence in 80+ countries.",
]
D_B = [
    "Food safety, social compliance, organic, packaging and flower certification programs.",
    "Find Control Union at Booth #851. Expo floor open Thursday 15 and Friday 16 in Orlando.",
    "One certification body for several audits: fewer visits and one audit calendar.",
    "Exporting to new markets? See the certifications retailers and importers ask for.",
]
ANUNCIOS = {
    "GPFS_EVENTO": [
        dict(h=H_EVENTO + H_NECESIDAD, d=D_A, p=("Produce-Show", "Booth-851")),
        dict(h=H_EVENTO + H_PROGRAMAS, d=D_B, p=("Certification", "Orlando")),
    ],
    "GPFS_ORLANDO": [
        dict(h=["At the Produce Show in Orlando", "In Orlando This October?", "Booth #851, Expo Oct 15-16"] + H_NECESIDAD, d=D_A, p=("Produce-Show", "Orlando")),
        dict(h=["Produce Expo in Orlando", "Control Union at Booth #851", "Booth #851, Expo Oct 15-16"] + H_PROGRAMAS, d=D_B, p=("Certification", "Orlando")),
    ],
    "GPFS_EXPOSITORES": [
        dict(h=["Add Booth #851 to Your Plan", "Save Booth #851 in the App", "Exhibitor: Control Union"] + H_NECESIDAD,
             d=["Planning your expo floor visits? Add Control Union, Booth #851, to your list."] + D_A[1:], p=("Booth-851", "Orlando")),
        dict(h=["Find Us on the Expo Floor", "Control Union at Booth #851", "Booth #851, Expo Oct 15-16"] + H_PROGRAMAS,
             d=["Building your show agenda? See what Control Union certifies before you visit #851."] + D_B[1:], p=("Certification", "Booth-851")),
    ],
}

# ------------------------------------------------------------------ grupo del Typeform «Certification Check» (va al Typeform, no a la landing)
# Necesidad de certificación de quien produce, empaca o exporta. Evita las keywords de la campaña PrimusGFS de EE.UU.
GRUPO_CHECK = dict(
    intencion="Necesita saber qué certificación le piden: se lo invita a un check de 2 minutos.",
    kw=[
        ("fresh produce certifications", "Phrase"),
        ("produce certification requirements", "Phrase"),
        ("certifications for exporting produce", "Phrase"),
        ("certification needed to export produce", "Phrase"),
        ("certifications for produce growers", "Phrase"),
        ("buyer certification requirements produce", "Phrase"),
        ("produce supplier certification", "Phrase"),
        ("fresh produce audit requirements", "Phrase"),
        ("retailer requirements fresh produce", "Phrase"),
        ("flower farm certification", "Phrase"),
    ],
)
H_CHECK = ["2-Minute Certification Check", "Which Certification Do I Need?", "Take the Certification Check"]
H_CHECK_A = [
    "Buyer Requires Certification?", "Too Many Audits Every Year?", "Exporting Fresh Produce?", "Retailer Audit Coming Up?",
    "Answer 10 Quick Questions", "See Programs That Fit You", "PrimusGFS or GLOBALG.A.P.?", "Organic, Social, Food Safety?",
    "Going to the Produce Show?", "Control Union at Booth #851", "200+ Certification Programs", "100+ Years of Certification",
]
D_C = [
    "Answer a few questions and see which certification programs match your operation.",
    "For growers, packers and exporters: food safety, organic, social and flower programs.",
    "Buyers asking for new audits? Take the 2-minute check before the produce show.",
    "Certification body with 100+ years of experience and a presence in 80+ countries.",
]
ANUNCIOS_CHECK = [
    dict(h=H_CHECK + H_CHECK_A, d=D_C, p=("Certification", "Check")),
    dict(h=H_CHECK + H_PROGRAMAS, d=D_C[:2] + D_B[2:], p=("Produce", "Check")),
]
SITELINK_CHECK = ("Certification Check", "Answer 10 quick questions", "See programs that fit you")
if TYPEFORM_URL:
    GRUPOS["GPFS_CHECK"] = GRUPO_CHECK
    ANUNCIOS["GPFS_CHECK"] = ANUNCIOS_CHECK

CALLOUTS = ["Booth #851", "Expo Floor Oct 15-16", "200+ Programs", "100+ Years Certifying", "Present in 80+ Countries", "One Body, Several Audits"]
# todos a la landing: es la única página que reúne estos programas (SMETA, BRCGS, Florverde y Fair Trade USA no tienen página propia en el sitio)
SITELINKS = [
    ("PrimusGFS Certification", "Food safety for fresh produce", "Audits for growers and packers"),
    ("GLOBALG.A.P. Program", "Good agricultural practices", "Certification for farms"),
    ("USDA NOP Organic", "Organic certification", "For growers and handlers"),
    ("SMETA Audits", "Social compliance audits", "Ethical trade for suppliers"),
    ("BRCGS Certification", "Food safety and packaging", "Recognized by retailers"),
    ("Florverde Flowers", "Sustainable flower certification", "For flower growers"),
    ("Fair Trade USA", "Fair Trade certification", "For produce and flowers"),
]
SNIPPET = ("Service catalog", ["PrimusGFS", "GLOBALG.A.P.", "USDA NOP", "SMETA", "GRASP", "BRCGS", "Florverde", "Fair Trade USA"])

# ------------------------------------------------------------------ negativas de campaña (concordancia amplia: el Editor solo acepta
# «Campaign Negative»; una negativa de varias palabras bloquea las búsquedas que contienen todas esas palabras)
NEG_ORIGINAL = ["jobs", "job", "careers", "hiring", "employment", "volunteer", "internship", "free", "2025", "2024", "anaheim", "atlanta",
                "hotel", "hotels", "parking", "airport", "flights", "shuttle", "booth cost", "booth price", "exhibit cost", "sponsorship",
                "become an exhibitor", "ifpa membership", "ifpa login", "wholesale", "buy", "consulting", "consultant", "advisory", "training", "course"]
NEG_NUEVAS = {
    "Entrada y logística del asistente": ["registration", "register", "tickets", "ticket", "badge", "pass", "app", "download", "login", "agenda",
                                         "speakers", "keynote", "awards", "education", "restaurants", "weather", "address", "2027"],
    "Logística del expositor y proveedores de stands": ["exhibitor manual", "exhibitor kit", "exhibitor services", "move in", "freight",
                                                        "booth design", "booth rental", "booth builder", "exhibit design", "displays"],
    "Vendedores de bases de datos": ["email list", "attendee list", "mailing list", "contact list", "leads"],
    "Otras ferias del rubro": ["new york produce show", "fruit logistica", "fruit attraction", "viva fresh", "southern exposure",
                               "cpma", "fpfc", "west coast produce expo", "world of perishables"],
    "Informativas y ruido": ["what is", "meaning", "membership", "salary"],
}
# Lista compartida de la skill para todas las campañas de Control Union (intención de consultoría, que es de Peterson)
NEG_CRUZADA_PETERSON = ["consultoría", "consultoria", "consultor", "consultora", "asesoría", "asesoria", "asesor", "asesoramiento",
                        "implementar", "implementación", "cómo implementar", "prepararse", "preparación", "cómo prepararse",
                        "gap analysis", "diagnóstico previo", "pre auditoría gratuita", "capacitación", "entrenamiento", "taller", "curso",
                        "estrategia", "hoja de ruta", "roadmap", "huella de carbono cálculo", "inventario de gei consultoría",
                        "consulting", "advisory", "training"]

PAIS = re.compile(r"\b(usa|u\.s\.|united states|mexico|méxico|canada|north america|american)\b", re.I)


def negs():
    return NEG_ORIGINAL + [n for v in NEG_NUEVAS.values() for n in v]


# ================================================================== validación propia (además de la del builder de la skill)
def validar():
    errores = []
    for g, ads in list(ANUNCIOS.items()) + [("GPFS_CHECK", ANUNCIOS_CHECK)]:
        for i, a in enumerate(ads, 1):
            if len(a["h"]) != 15:
                errores.append(f"{g} RSA{i}: {len(a['h'])} títulos")
            if len(set(a["h"])) != len(a["h"]):
                errores.append(f"{g} RSA{i}: títulos repetidos")
            errores += [f"{g} RSA{i} título >30: {t} ({len(t)})" for t in a["h"] if len(t) > 30]
            errores += [f"{g} RSA{i} descripción >90: {t} ({len(t)})" for t in a["d"] if len(t) > 90]
            errores += [f"{g} RSA{i} ruta >15: {p}" for p in a["p"] if len(p) > 15]
            for t in a["h"] + a["d"]:
                if re.search(r"advis|consult|prepar|strategy", t, re.I):
                    errores.append(f"{g}: vocabulario de consultora en «{t}»")
                if re.search(r"\bifpa\b|global produce (&|and) floral", t, re.I):
                    errores.append(f"{g}: marca de tercero en el texto «{t}»")
                if "14-16" in t:
                    errores.append(f"{g}: «14-16» junto al stand; la expo abre el 15 y el 16 («{t}»)")
                # siempre «Control Union», sin país; «Fair Trade USA» es el nombre del programa
                if PAIS.search(t.replace("Fair Trade USA", "")):
                    errores.append(f"{g}: nombra un país en «{t}»")
                if re.search(r"schedule|book a meeting|book time", t, re.I):
                    errores.append(f"{g}: invita a agendar en vez de a la landing («{t}»)")
    errores += [f"callout >25: {c}" for c in CALLOUTS if len(c) > 25]
    errores += [f"callout con país: {c}" for c in CALLOUTS if PAIS.search(c)]
    for s in SITELINKS + [SITELINK_CHECK]:
        if len(s[0]) > 25 or len(s[1]) > 35 or len(s[2]) > 35:
            errores.append(f"sitelink largo: {s}")
    errores += [f"snippet >25: {v}" for v in SNIPPET[1] if len(v) > 25]
    for g, d in list(GRUPOS.items()) + [("GPFS_CHECK", GRUPO_CHECK)]:
        for k, _ in d["kw"]:
            for ng in negs() + NEG_CRUZADA_PETERSON:
                if all(w in k.split() for w in ng.split()):
                    errores.append(f"la negativa «{ng}» bloquea la keyword «{k}» ({g})")
    return errores


# ================================================================== plan JSON para build_editor_csv.py (skill paid-media-pcu)
def plan():
    return {
        "_comentario": "Generado por scripts/gpfs_2026_campana.py. Control Union, The Global Produce & Floral Show 2026 (IFPA).",
        "marca": "control-union", "pais": "US", "moneda": "ARS",
        "utm": {"activar": False},  # sin plantilla de seguimiento, a pedido de Felipe
        "campanas": [dict(
            nombre=CAMPANA, tipo="Search", estado="Paused", presupuesto_diario=PRESUPUESTO_DIA, estrategia_puja=ESTRATEGIA,
            redes="Google Search", idiomas=IDIOMAS, ubicaciones=UBICACIONES, ubicaciones_excluidas=[], fecha_inicio="", fecha_fin="",
            etiquetas=["Evento IFPA 2026"], negativas_campana=negs(),
            sitelinks=[dict(texto=t, desc1=d1, desc2=d2, url=LANDING) for t, d1, d2 in SITELINKS]
            + ([dict(texto=SITELINK_CHECK[0], desc1=SITELINK_CHECK[1], desc2=SITELINK_CHECK[2], url=TYPEFORM_URL)] if TYPEFORM_URL else []),
            grupos=[dict(nombre=g, estado="Paused", url_final=TYPEFORM_URL if g == "GPFS_CHECK" else LANDING,
                         keywords=[dict(texto=k, concordancia=t) for k, t in GRUPOS[g]["kw"]],
                         anuncios=[dict(nombre=f"{g}_RSA{i}", titulares=a["h"], descripciones=a["d"], path1=a["p"][0], path2=a["p"][1])
                                   for i, a in enumerate(ANUNCIOS[g], 1)])
                    for g in GRUPOS],
        )],
    }


def para_editor():
    """Convierte la salida del builder (UTF-8, comas) en el archivo que importa Google Ads Editor en Windows en español:
    UTF-16 con BOM y separado por tabulaciones («Unicode Text», el formato que recomienda Google). Además:
    solo la campaña en pausa (grupos, keywords y anuncios activos) y ubicaciones con su ID de Google."""
    import csv
    ruta = os.path.join(OUT, "todo-junto.csv")
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    cols = list(filas[0].keys())
    if "Location ID" not in cols:
        cols.insert(cols.index("Location") + 1, "Location ID")
    if "Ad type" not in cols:  # sin esto Editor marca las filas de anuncios como «tipo de fila ambiguo» y no los importa
        cols.insert(cols.index("Ad Name") + 1, "Ad type")
    for f in filas:
        if f.get("Campaign Type"):
            f["Campaign Status"] = "Paused"
        if f.get("Ad Group Status"):
            f["Ad Group Status"] = "Enabled"
        if f.get("Status"):
            f["Status"] = "Enabled"
        f["Location ID"] = GEO_ID.get(f.get("Location", ""), "")
        f["Ad type"] = "Responsive search ad" if f.get("Ad Name") else ""
    for nombre in os.listdir(OUT):  # un solo archivo de importación, para no confundir
        if nombre.endswith(".csv"):
            os.remove(os.path.join(OUT, nombre))
    with open(ruta, "w", encoding="utf-16", newline="") as fh:  # «utf-16» escribe el BOM
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="	", extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    # control: se vuelve a leer como lo haría Editor
    leidas = list(csv.DictReader(open(ruta, encoding="utf-16"), delimiter="	"))
    cuenta = dict(campana=sum(1 for f in leidas if f["Campaign Type"]), ubicaciones=sum(1 for f in leidas if f["Location"]),
                  grupos=sum(1 for f in leidas if f["Ad Group Status"]), keywords=sum(1 for f in leidas if f["Criterion Type"] in ("Exact", "Phrase")),
                  negativas=sum(1 for f in leidas if f["Criterion Type"] == "Campaign Negative"), anuncios=sum(1 for f in leidas if f["Ad type"] == "Responsive search ad"),
                  sitelinks=sum(1 for f in leidas if f["Sitelink Text"]))
    nombres = {f["Campaign"] for f in leidas}
    assert nombres == {CAMPANA}, nombres
    return f"Editor: {os.path.basename(ruta)} (UTF-16, tabulaciones) · {cuenta}"


def builder():
    for raiz, _, archivos in os.walk(SKILL):
        if "build_editor_csv.py" in archivos and "paid-media-pcu" in raiz:
            return os.path.join(raiz, "build_editor_csv.py")
    raise SystemExit("No encuentro build_editor_csv.py de la skill paid-media-pcu")


if __name__ == "__main__":
    err = validar()
    if err:
        raise SystemExit("Errores:\n  " + "\n  ".join(err))
    if not TYPEFORM_URL:
        print("Aviso: TYPEFORM_URL vacío. El grupo GPFS_CHECK y su sitelink quedan afuera del CSV hasta cargar el link.")
    if os.path.isdir(OUT):  # la versión anterior tenía otra campaña: se regeneran todos los archivos
        for f in os.listdir(OUT):
            os.remove(os.path.join(OUT, f))
    os.makedirs(OUT, exist_ok=True)
    ruta_plan = os.path.join(OUT, "plan.json")
    json.dump(plan(), open(ruta_plan, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, builder(), ruta_plan, "--outdir", OUT, "--merge"], capture_output=True, text=True,
                       encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print(r.stdout[-3000:], r.stderr[-1500:])
    if r.returncode:
        raise SystemExit("build_editor_csv.py rechazó el plan")
    print(para_editor())
