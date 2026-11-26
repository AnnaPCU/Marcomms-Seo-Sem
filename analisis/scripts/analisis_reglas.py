# -*- coding: utf-8 -*-
"""Reglas compartidas: reconstrucción del Anexo A de la auditoría de Ads como lista de tokens.
Es la misma tabla que usa analisis.py (copiada acá para poder importarla sin ejecutar el análisis)."""
import re

ANEXO_A = {
    ("España", "CAEs"): "vivienda particular particulares gratis barato precio cuanto cuesta ce3x ce3 certicalia online sin visita descargar euskadi cantabria aragon unifamiliar cuando te caes db he1 cypetherm emovili repsol iberdrola endesa coche electrico aislamiento",
    ("Américas", "Agricultura regenerativa"): "rizobacter syngenta corteva bayer nutrien yara koppert adecoagro bioceres agrofy inta aapresid conabia inase upl adama sipcam daymsa spraytec nufarm stoller verdesian novonesis dekalb puna bio ovis 21 ruuts caligenia sembra evolucion argenbio|tecnologia agricola|tecnologia para la agricultura|agricultura innovadora|agtech|smart farming|agricultura de precision|nuevas tecnologias|sensores|monitores|fieldview|ndvi|sintropica|agroforesteria|permacultura|polyfarming|huerto|granja|olivar|libros|ernst gotsch",
    ("CU", "*"): "consultant|consultor|consultoria|advisor|asesoramiento",
    ("Américas", "Bioenergia / Biocombustibles"): "biogas|bio gas|biometano|planta de|produccion de|que es|como generar|residuos organicos|dosbio|biodes|fenix|doble l|ceamse|helios",
    ("Américas", "Huella de carbono / GEI"): "bonos de carbono|bono de carbono|mercado de carbono|mercados de carbono|creditos de carbono|credito de carbono|verra|cercarbono|carbono neutral|carbon neutral|carbono neutro|carbon trading|cuotas de carbono|iso 14001|persefoni|carboncloud|carbon cloud|puma|ndc|renami",
    ("Norteamérica", "Forestry"): "registered professional forester|rpf|forester license|forestry certificate online|courses|enform|falling ticket|tree felling|bc forest safety|accreditation board|how to become|job|training",
    ("España", "Textile"): "oeko tex|oeko-tex|oeko|organic cotton standard",
    ("Norteamérica", "Canada Gap"): "supply chain management|indocert|cargill|organic certification|forms|corrective action report",
    ("Norteamérica", "USDA NOP"): "organic chicken|chicken certification|organic land certification|omri",
    ("Américas", "Huella de agua"): "tratamiento|efluentes|aguas residuales|calculadora|aquae|planta de tratamiento",
    ("España", "IFS"): "servsafe|certifood|manipulacion de alimentos|food handler|food handling|curso|cursos|salsa accreditation",
    ("España", "Forestal"): "rainforest alliance|medio ambiente",
    ("Américas", "ESG / Reportes"): "gri \\d+|que es|que significa|que son|eqsc|verdantix",
    ("Portugal", "Textile"): "wordly|database",
    ("Portugal", "Forestal"): "ecocert",
    ("Argentina", "ISO 27001"): "nist",
}


def _rx(spec):
    partes = [p.strip() for p in spec.split("|") if p.strip()] if "|" in spec else spec.split()
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(p) if "\\d" not in p else p for p in partes) + r")(?![a-z0-9])")


def es_desperdicio_factory():
    RX = {k: _rx(v) for k, v in ANEXO_A.items()}

    def f(df):
        out = []
        for _, row in df.iterrows():
            t = row["termino_n"]; hit = False
            for (prop, camp), rx in RX.items():
                if prop == "CU":
                    if row["marca"] == "CU" and rx.search(t):
                        hit = True; break
                elif row["propiedad"] == prop and row["camp_corta"] == camp and rx.search(t):
                    hit = True; break
            out.append(hit)
        return out
    return f
