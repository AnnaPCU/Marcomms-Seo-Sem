# -*- coding: utf-8 -*-
"""
generar_propuestas_anuncios.py — propuestas de cambio de anuncios por grupo, a partir de:
  · lo que dice el anuncio hoy (títulos y descripciones activos, fuerza del anuncio)
  · los términos de búsqueda que lo activaron y su relación con el anuncio (pago)
  · cómo busca la gente el mismo tema en orgánico (Search Console)
Los títulos propuestos respetan 30 caracteres y las descripciones 90; el script lo valida.
Sale a informe/propuestas-anuncios.html
"""
import json, os, sys
from informe_util import n, ars, e, hoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(ROOT, "informe")
A = {(s["campana"], s["grupo"]): s for s in json.load(open(os.path.join(INF, "datos_anuncios.json"), encoding="utf-8"))}
HOY = hoy()
H, D = 30, 90


def g(camp, grupo):
    return next((v for (c, gr), v in A.items() if c.startswith(camp) and gr == grupo), None)


# ================================================================== propuestas (copy escrito a mano, validado abajo)
P = []


def prop(marca, unidad, camp, grupo, diagnostico, titulos, descripciones, quitar=None, nota=None, cambio="Reescribir"):
    P.append(dict(marca=marca, unidad=unidad, camp=camp, grupo=grupo, diagnostico=diagnostico, titulos=titulos, descripciones=descripciones,
                  quitar=quitar or [], nota=nota, cambio=cambio, datos=g(camp, grupo)))


# ---------- CONTROL UNION · ESPAÑA
prop("Control Union", "España", "CU España - CAEs", "Certificados y Sistema CAE",
     "Siete títulos, fuerza «pobre». Ninguno dice «verificación de actuaciones» ni «sujeto obligado», que es lo que compra la campaña; el orgánico entra por «verificacion cae» y «verificador cae». La mitad del gasto viene de particulares que buscan el certificado de su vivienda: eso no se arregla con títulos sino con negativos.",
     ["Verificamos Actuaciones CAE", "Verificador CAE Acreditado", "Sistema CAE: Verificamos", "Sujetos Obligados y Delegados", "Certificados Ahorro Energético", "Verificación CAE para Empresas", "Control Union España", "Solicita Verificación CAE", "Auditoría Técnica de Ahorros", "Verificamos, No Gestionamos"],
     ["Organismo verificador acreditado por ENAC. Verificamos actuaciones de ahorro energético.", "Para sujetos obligados y delegados: verificación técnica de CAE con rigor y plazos claros.", "Convierte tus ahorros energéticos en certificados verificados. Cuéntanos tu actuación.", "No gestionamos ni tramitamos CAE de particulares: verificamos actuaciones de empresas."],
     quitar=["Rigor Técnico en Cada Proyecto"], nota="Aplicar antes los negativos de vivienda. La cuarta descripción cierra la puerta al particular de forma explícita.")

prop("Control Union", "España", "CU España - IFS", "Food Safety",
     "Los títulos hablan de «seguridad alimentaria» en genérico y ninguno nombra IFS, ISO 22000 ni FSSC, que es lo que la gente escribe (ifs food, iso 22000, brcgs). En orgánico entran por haccp, iso 22000 y «certificaciones de seguridad alimentaria». Sugerencia: partir en tres grupos, IFS, ISO 22000/FSSC y HACCP, cada uno con su anuncio.",
     ["Certificación IFS Food", "Auditoría IFS Food Versión 8", "Certificamos ISO 22000", "Certificación FSSC 22000", "Certificación HACCP", "Organismo Certificador", "Control Union España", "Certificamos Food Safety", "Auditores IFS en España", "Solicita Tu Auditoría IFS"],
     ["Certificamos IFS Food, ISO 22000 y FSSC 22000. Organismo de certificación acreditado.", "Auditoría IFS Food v8 con equipo auditor local. Cuéntanos tu planta y coordinamos fechas.", "Certificación de seguridad alimentaria reconocida por GFSI para fabricantes y envasadores.", "Más de 100 años certificando. Presencia en más de 80 países."],
     quitar=["Soporte técnico completo", "Auditorías para empresas", "Equipo técnico experto"], nota="BRCGS no va en títulos: no hay demanda ni contenido (33 búsquedas orgánicas en el histórico).")

prop("Control Union", "España", "CU España - Textile", "GOTS",
     "Fuerza «pobre». La descripción dice «Control Union acompaña marcas»: es vocabulario de Peterson; Control Union certifica. Lo que la gente escribe: certificado gots, sello gots, certified gots organic cotton; en orgánico, «gots en español» y «qué es gots». OEKO-TEX aparece por keyword, no por anuncio: va a negativo.",
     ["Certificación GOTS", "Certificado GOTS Para Tu Marca", "Sello GOTS: Algodón Orgánico", "GOTS: Qué Es y Cómo Certificar", "Auditoría GOTS en España", "GOTS Global Organic Textile", "Certificamos GOTS y OCS", "Organismo Certificador Textil", "Control Union España", "Solicita Tu Certificación GOTS"],
     ["Certificamos GOTS: textiles orgánicos con trazabilidad desde la fibra hasta la prenda.", "Organismo de certificación GOTS. Cuéntanos tu producto: alcance, pasos y plazos.", "Auditoría GOTS con equipo local en España y red en más de 80 países.", "También certificamos OCS y GRS: contenido orgánico y reciclado en una misma auditoría."],
     quitar=["Prepara Tu Auditoría", "Auditoría Independiente"], nota="«Prepara tu auditoría» sugiere preparación, que es servicio de Peterson. Control Union certifica y audita.")

prop("Control Union", "España", "CU España - Textile", "GRS",
     "Anuncio correcto en tema; la gente escribe «global recycled standard» y «grs textile exchange», y en orgánico «grs» a secas domina (7.658 búsquedas, posición 9). Falta nombrar a Textile Exchange, que es como muchos identifican la norma.",
     ["Certificación GRS", "GRS de Textile Exchange", "Global Recycled Standard", "Certificado GRS Reciclado", "Auditoría GRS en España", "Certificamos GRS y RCS", "Reciclado Certificado GRS", "Organismo Certificador Textil", "Control Union España", "Solicita Tu Certificación GRS"],
     ["Certificamos GRS y RCS, los estándares de contenido reciclado de Textile Exchange.", "Auditoría GRS con equipo local. Trazabilidad del reciclado en toda la cadena textil.", "Cuéntanos tu producto y te confirmamos alcance, requisitos y plazos de certificación.", "Más de 100 años certificando. Red propia en más de 80 países."],
     quitar=["grs textile certification", "Prepara Tu Auditoría"], cambio="Ajustar")

prop("Control Union", "España", "CU España - Forestal", "PEFC",
     "Fuerza «pobre». Los términos son «pefc españa», «certificado madera pefc» y una porción creciente de «sostenibilidad» a secas por la keyword «pefc certification» en frase. FSC entra al grupo PEFC y ve un anuncio de PEFC: por eso el plan pide un grupo FSC propio, con este anuncio.",
     ["Certificación PEFC", "Cadena de Custodia PEFC", "Certificado PEFC de Madera", "PEFC España: Certificamos", "Auditoría PEFC Forestal", "Certificación Forestal PEFC", "Certificadora Forestal", "Control Union España", "Solicita Tu Certificación PEFC", "Certificación PEFC y FSC"],
     ["Certificamos PEFC: cadena de custodia para madera, papel y productos forestales.", "Auditoría PEFC con equipo local en España. Cuéntanos tu producto y coordinamos fechas.", "Organismo de certificación forestal: PEFC y FSC en una misma auditoría.", "Más de 100 años certificando. Presencia en más de 80 países."],
     nota="Grupo FSC nuevo con: «Certificación FSC», «Cadena de Custodia FSC», «Certificado FSC de Madera», «FSC España: Certificamos», landing en la página FSC.")

prop("Control Union", "España", "CU España - Smeta", "Social",
     "El anuncio está bien y el 80% del gasto reciente son nombres de competidores. No es un problema de anuncio: la keyword «smeta auditoria» en frase abrió la puerta. Cambio mínimo en el anuncio y negativos.",
     ["Auditoría SMETA", "Auditoría SMETA 4 Pilares", "SMETA 2 y 4 Pilares", "Auditoría Social Sedex", "SMETA España: Auditamos", "Auditores SMETA Locales", "Auditoría Ética y Laboral", "Control Union España", "Solicita Tu Auditoría SMETA", "Certificación SMETA"],
     ["Auditoría SMETA 2 y 4 pilares para proveedores y cadenas de suministro. Equipo local.", "Auditamos prácticas laborales, salud y seguridad, medio ambiente y ética de negocio.", "Cuéntanos tu planta y tu cliente y coordinamos la auditoría SMETA en fecha.", "Más de 100 años auditando. Red propia en más de 80 países."],
     quitar=["Prepara Tu Auditoría"], cambio="Ajustar", nota="Negativos: intertek, tüv, dnv, veolia, sgs, bureau veritas, aenor, kiwa. «smeta auditoria» a exacta.")

prop("Control Union", "España", "CU España - Bioenergia", "ISCC",
     "Fuerza «pobre» con relación fuerte: la gente escribe «iscc», «iscc plus», «certificado iscc» y el anuncio lo dice. El problema es que la query «iscc» casi desapareció del orgánico (605 → 11 impresiones desde España): el anuncio hoy sostiene solo el tema. Faltan títulos de ISCC EU y de la directiva RED.",
     ["Certificación ISCC", "ISCC EU e ISCC PLUS", "Certificado ISCC Biomasa", "Auditoría ISCC en España", "Certificamos ISCC EU", "Biocombustibles Certificados", "Cumplimiento RED III", "Organismo Certificador ISCC", "Control Union España", "Solicita Tu Certificación ISCC"],
     ["Certificamos ISCC EU e ISCC PLUS: biomasa, biocombustibles y materias primas sostenibles.", "Auditoría ISCC con equipo local. Balance de masas y trazabilidad para RED III.", "Cuéntanos tu materia prima y tu mercado y te confirmamos alcance y plazos.", "Más de 100 años certificando. Presencia en más de 80 países."],
     quitar=["Solicita Información"], cambio="Ajustar")

prop("Control Union", "España", "CU España - Plasticos", "RecyClass",
     "Relación fuerte: «recyclass» es el 98% del gasto. El orgánico muestra tres intenciones que el anuncio no nombra: reciclabilidad, contenido reciclado y reutilización de plásticos (830 búsquedas, posición 36).",
     ["Certificación RecyClass", "RecyClass: Reciclabilidad", "Reciclado Certificado", "Auditoría RecyClass en España", "Certificamos RecyClass", "Plástico Reciclado Certificado", "Trazabilidad del Reciclado", "Organismo Certificador", "Control Union España", "Solicita Tu Certificación"],
     ["Certificamos RecyClass: reciclabilidad y contenido reciclado en envases plásticos.", "Auditoría RecyClass con equipo local. Demuestra tu contenido reciclado sin greenwashing.", "Cuéntanos tu producto y te confirmamos el esquema, el alcance y los plazos.", "Más de 100 años certificando. Red propia en más de 80 países."],
     quitar=["Prepara Tu Auditoría", "Equipo Auditor Local"], cambio="Ajustar")

# ---------- CONTROL UNION · PORTUGAL
prop("Control Union", "Portugal", "CU Portugal - Textile", "GOTS",
     "La gente escribe «gots 8.0», «gots database», «gots symbol», «norma gots». El anuncio no nombra la versión ni el símbolo. La descripción «Apoio a marcas» es vocabulario de consultoría; Control Union certifica.",
     ["Certificação GOTS", "Certificação GOTS 8.0", "Norma GOTS: Certificamos", "Símbolo GOTS Para a Sua Marca", "Auditoria GOTS em Portugal", "GOTS Global Organic Textile", "Certificamos GOTS e OCS", "Organismo de Certificação", "Control Union Portugal", "Peça a Sua Certificação GOTS"],
     ["Certificamos GOTS 8.0: têxteis orgânicos com rastreabilidade da fibra ao produto final.", "Auditoria GOTS com equipa local em Portugal e rede em mais de 80 países.", "Diga-nos o seu produto e confirmamos âmbito, requisitos e prazos de certificação.", "Também certificamos OCS e GRS: conteúdo orgânico e reciclado numa só auditoria."],
     quitar=["Peça Informação"], cambio="Ajustar")

prop("Control Union", "Portugal", "CU Portugal - Forestal", "PEFC",
     "Relación fuerte, con «pefc o que é» entre los términos más caros: intención informativa. En orgánico, «pefc search» y «pefc certificate search»: la gente busca verificar certificados. Un título que responda «o que é» captura esa intención sin pagar por curiosidad pura.",
     ["Certificação PEFC", "PEFC: O Que É e Como Obter", "Cadeia de Custódia PEFC", "Certificado PEFC de Madeira", "Auditoria PEFC em Portugal", "Certificação Florestal", "Certificamos PEFC e FSC", "Organismo de Certificação", "Control Union Portugal", "Peça a Sua Certificação PEFC"],
     ["Certificamos PEFC: cadeia de custódia para madeira, papel e produtos florestais.", "Auditoria PEFC com equipa local em Portugal. Diga-nos o seu produto e marcamos datas.", "Organismo de certificação florestal: PEFC e FSC numa só auditoria.", "Mais de 100 anos a certificar. Presença em mais de 80 países."],
     cambio="Ajustar", nota="Grupo FSC próprio: «Certificação FSC», «Cadeia de Custódia FSC», «Madeira Certificada FSC», landing na página FSC.")

prop("Control Union", "Portugal", "CU Portugal - Plasticos", "UNE 15343",
     "Los términos dicen «une en 15343 2008»: la gente cita la norma con año. Bien el anuncio, salvo «bso consulting» y «como reduzir a produção de resíduos», que son negativos, no títulos.",
     ["Certificação UNE-EN 15343:2008", "Plástico Reciclado Certificado", "Auditoria EN 15343", "Rastreabilidade do Reciclado", "Certificamos EN 15343", "Organismo de Certificação", "Control Union Portugal", "Peça a Sua Certificação"],
     ["Certificamos UNE-EN 15343:2008: rastreabilidade e conteúdo reciclado em plásticos.", "Auditoria com equipa local em Portugal. Diga-nos o seu processo e confirmamos o âmbito.", "Mais de 100 anos a certificar. Rede própria em mais de 80 países."],
     quitar=["Cumprir EN 15343", "Peça Informação"], cambio="Ajustar")

prop("Control Union", "Portugal", "CU Portugal - Biomasa", "SURE",
     "Un solo término, «certificado sur», con relación fuerte. En orgánico, «sure madeira» (60 búsquedas) y «sure sustainable resources». El anuncio no nombra madera ni RED III.",
     ["Certificação SURE", "SURE Para Biomassa de Madeira", "Certificado SURE: RED III", "Auditoria SURE em Portugal", "Certificamos SURE", "Biomassa Sustentável: SURE", "Organismo de Certificação", "Control Union Portugal", "Peça a Sua Certificação SURE"],
     ["Certificamos SURE: biomassa sólida e madeira com conformidade RED III e rastreabilidade.", "Auditoria SURE com equipa local em Portugal. Diga-nos a sua cadeia e confirmamos âmbito.", "Mais de 100 anos a certificar. Presença em mais de 80 países."],
     quitar=["Peritos Em Bioenergia", "Peça Informação"], cambio="Ajustar")

# ---------- CONTROL UNION · CANADÁ Y EE.UU.
prop("Control Union", "Canadá", "CU Canada - Forestry", "FSC",
     "El grupo FSC usa el mismo anuncio genérico de «Forestry Certification». La gente escribe «fsc canada», «fsc chain of custody», «how to get fsc certification» y también en francés («normes fsc», ARS 8.498). Un anuncio FSC propio, y uno en francés si se mantiene la campaña. Vale solo si se decide no pausar Forestry.",
     ["FSC Certification Canada", "FSC Chain of Custody Audit", "How to Get FSC Certified", "FSC Certified: We Certify", "FSC Forest Management", "Accredited Certification Body", "FSC Auditors in Canada", "Control Union Canada", "Request FSC Certification", "FSC and PEFC Certification"],
     ["We certify FSC chain of custody and forest management. Accredited certification body.", "Tell us your products and markets and we confirm scope, requirements and timelines.", "FSC audits with local auditors in Canada and a network in more than 80 countries.", "Over 100 years of certification. 274+ offices and labs worldwide."],
     nota="Versión en francés: «Certification FSC Canada», «Chaîne de Contrôle FSC», «Organisme Certificateur FSC». Negativos de credencial personal siguen pendientes.")

prop("Control Union", "Canadá", "CU Canada - Canada Gap", "CanadaGAP cert",
     "Relación fuerte en los términos correctos («canada gap», «canadagap certification», «canadagap 2026»). La descripción dice «CanadianGAP», nombre incorrecto del programa. Cargill, supply chain management e indocert son negativos, no anuncio.",
     ["CanadaGAP Certification", "CanadaGAP Audit 2026", "Certified CanadaGAP Body", "Fresh Produce Food Safety", "CanadaGAP for Packers", "CanadaGAP for Growers", "Accredited Certification Body", "Control Union Canada", "Request CanadaGAP Audit", "Greenhouse and Field Produce"],
     ["We certify CanadaGAP for growers, packers and repackers. Accredited certification body.", "Book your CanadaGAP audit with local auditors. Tell us your operation and crop.", "Food safety certification recognized by Canadian retailers and GFSI.", "Over 100 years of certification. Presence in more than 80 countries."],
     quitar=["Don't Risk It, Get Certified", "Packing House Support", "Transparent and consistent"], cambio="Ajustar")

prop("Control Union", "Estados Unidos", "CU United States - Organic - USDA NOP", "Switch & Get Certified",
     "Los términos más caros son definiciones («what does certified organic mean», «what is certified organic»): van a negativo, no a título. Lo que sí compra bien: «how to get certified organic», «organic certification», «national organic program». Falta nombrar el NOP y el ámbito (crop, livestock, handling).",
     ["USDA Organic Certification", "Get USDA Organic Certified", "NOP-Accredited Certifier", "Organic Certification: Farms", "Organic Handler Certification", "Switch Your Organic Certifier", "No Lapse When You Switch", "Control Union USA", "Request an Organic Quote", "How to Get Certified Organic"],
     ["USDA NOP-accredited organic certifier for crops, handling and processing in the U.S.", "Switch certifiers with no lapse in status. We manage the transfer for you.", "Tell us your operation and we confirm scope, fees and timeline to certification.", "Over 100 years of certification. Presence in more than 80 countries."],
     quitar=["Named Contact, Every Time", "CUC USA: 80+ Countries"], cambio="Ajustar", nota="«organic chicken certification» (ARS 11.056): solo si el alcance incluye livestock; si no, negativo. Es un supuesto a confirmar con la unidad.")

prop("Control Union", "Canadá", "CU Canada - GLOBALG.A.P.", "GLOBALG.A.P cert",
     "«global gap» sin punto es la forma en que la gente lo escribe (ARS 15.523) y ningún título lo dice así; «food safety consultant» es negativo. Títulos con «partner» y «support» suenan a consultoría.",
     ["GLOBALG.A.P. Certification", "Global GAP Certification", "GLOBALG.A.P. IFA Audit", "GGAP Chain of Custody", "Accredited Certification Body", "GLOBALG.A.P. for Greenhouses", "Control Union Canada", "Request GLOBALG.A.P. Audit", "Farm Certification Canada"],
     ["We certify GLOBALG.A.P. IFA and chain of custody. Accredited certification body.", "Tell us your farm and crops and we confirm scope, requirements and audit dates.", "Over 100 years of certification. Presence in more than 80 countries."],
     quitar=["Farm Assurance Support", "Don't Risk It, Get Certified", "Market Access Support", "Improve Farm Compliance"], cambio="Ajustar")

# ---------- CONTROL UNION · ARGENTINA (campañas nuevas)
prop("Control Union", "Argentina", "CU Argentina - Agroexportación", "EUDR proceso",
     "Campaña nueva y bien armada: relación fuerte, landing propia. «eudr que significa» (ARS 5.493, un clic) es definición: negativo. Falta un título que diga qué hace Control Union en EUDR con su verbo: verificar, no asesorar.",
     ["Verificación EUDR Argentina", "Cumplimiento EUDR Verificado", "Debida Diligencia EUDR", "EUDR Soja, Carne y Madera", "Libre de Deforestación", "Auditores EUDR en Argentina", "Organismo de Certificación", "Control Union Argentina", "Pedí Tu Verificación EUDR", "EUDR: Aplica en Diciembre 2026"],
     ["Verificamos el cumplimiento EUDR: trazabilidad y debida diligencia para exportar a la UE.", "Organismo de certificación con auditores en Argentina y red en más de 80 países.", "Contanos tu producto y tu mercado y te confirmamos alcance, requisitos y plazos.", "Más de 100 años certificando. Presencia en más de 80 países."],
     cambio="Ajustar", nota="«eudr que significa», «que es», «resumen» a negativo antes de cambiar el anuncio.")

prop("Control Union", "Argentina", "CU Argentina - Biocombustible", "ISCC",
     "Las keywords dicen ISCC y el anuncio dice 2BSvs, «alternativa a ISCC EU». Cuando publique, cobrará clics de quien busca ISCC y ve otro esquema. Un grupo por esquema, cada uno con su anuncio y su landing.",
     ["Certificación ISCC Argentina", "ISCC EU e ISCC PLUS", "Certificamos ISCC EU", "Biocombustibles a la UE", "Auditoría ISCC en Argentina", "Balance de Masas ISCC", "Organismo Certificador ISCC", "Control Union Argentina", "Pedí Tu Certificación ISCC", "Certificación ISCC y 2BSvs"],
     ["Certificamos ISCC EU e ISCC PLUS: biocombustibles, aceite y materias primas para la UE.", "Auditoría ISCC con equipo local en Argentina. Balance de masas y trazabilidad RED III.", "Contanos tu materia prima y tu mercado y te confirmamos alcance y plazos.", "También certificamos 2BSvs. Te decimos cuál conviene según tu comprador."],
     cambio="Grupo nuevo", nota="El anuncio 2BSvs actual queda en su propio grupo con keywords 2BSvs. Antes: definir el corte con Peterson, que compra Bioenergía con las mismas keywords.")

# ---------- ISO 27001 (PCU)
prop("ISO 27001 (PCU)", "España", "PCU España - ISO 27001", "Compra",
     "El anuncio ya usa las cifras y el verbo de Control Union («certificamos», «más de 100 años», «80 países», «274 oficinas»): es un anuncio de Control Union con nombre PCU. Relación fuerte. Faltan la versión 2022 y «ISO/IEC», que la gente escribe; «que dice», «dominios», «iso 27» son negativos.",
     ["Certificación ISO 27001", "ISO/IEC 27001:2022", "Certificamos ISO 27001", "Auditoría ISO 27001 en España", "Certifica Tu SGSI", "Certificadora ISO 27001", "Auditores ISO 27001 en España", "Control Union España", "Solicita Tu Presupuesto", "Más de 100 Años Certificando"],
     ["Auditamos y certificamos ISO/IEC 27001:2022 con alcance acreditado. Solicita presupuesto.", "Cuéntanos el alcance de tu SGSI y coordinamos la auditoría con el equipo local.", "Entidad de certificación con más de 100 años y presencia en más de 80 países.", "Certificación de seguridad de la información para empresas de cualquier tamaño."],
     cambio="Ajustar", nota="Renombrar campaña y anuncios como Control Union. Verificar el alcance acreditado para ISO 27001 antes de usar «acreditado» en títulos: es un supuesto.")

prop("ISO 27001 (PCU)", "Argentina", "PCU Argentina - ISO 27001", "Compra",
     "Mismo caso. En Argentina la gente escribe «iso iec 27001», «iso 27001 2022», «norma iso 27001» y «ciberseguridad»; el anuncio no nombra la versión ni ISO/IEC. Google califica la relevancia «media» en 14 de 15 keywords: hay margen.",
     ["Certificación ISO 27001", "Norma ISO/IEC 27001:2022", "Certificamos ISO 27001", "Auditoría ISO 27001 Argentina", "Certificá Tu SGSI", "Certificadora ISO 27001", "Seguridad de la Información", "Control Union Argentina", "Pedí Tu Cotización", "Más de 100 Años Certificando"],
     ["Auditamos y certificamos ISO/IEC 27001:2022 con alcance acreditado. Pedí tu cotización.", "Contanos el alcance de tu SGSI y coordinamos la auditoría con el equipo local.", "Organismo de certificación con más de 100 años y presencia en más de 80 países.", "Certificación de seguridad de la información: el certificado que piden tus clientes."],
     cambio="Ajustar")

# ---------- PETERSON SOLUTIONS
prop("Peterson Solutions", "Argentina", "PS Argentina - SuSo - Agricultura regenerativa", "Regenerativa",
     "El anuncio está bien escrito; el gasto se va en tecnología agrícola, marcas del agro y pools de siembra, que ningún título puede responder: es la amplia. El tono puede ser más de Peterson: «nosotros», acompañar, co-desarrollar.",
     ["Agricultura Regenerativa", "Transición Regenerativa", "Programas Regenerativos Agro", "Carbono en Suelo: Medimos", "Te Acompañamos en Campo", "Regenagri y Certificaciones", "Consultoría Peterson", "Diagnóstico y Monitoreo", "Hablemos de Tu Campo", "Impacto Medido en Campo"],
     ["Acompañamos a productores y empresas en la transición regenerativa, de punta a punta.", "Co-desarrollamos programas regenerativos con datos de suelo, carbono e impacto.", "Preparamos tu cadena para Regenagri y otras certificaciones. Hablemos de tu campo.", "Para el mundo, para nosotros, para nuestras familias."],
     quitar=["Monitoreo En Campo", "Cadena Agricola", "Impacto Agricola"], cambio="Ajustar", nota="Sacar la amplia primero: ningún título compensa 219 clics de marcas del agro.")

prop("Peterson Solutions", "Argentina", "PS Argentina - SuSe - Huella de carbono / GEI", "Huella carbono",
     "Dos grupos con el mismo anuncio. La gente escribe «inventario gei argentina» (fuerte), «consultoria ambiental» y «como medir la huella de carbono de una empresa» (parcial): hay demanda de consultoría que es exactamente lo que Peterson vende y el anuncio no dice «consultora ambiental». Bonos, verra, carbono neutral son negativos.",
     ["Huella de Carbono Empresas", "Consultora Ambiental", "Inventario GEI Argentina", "Medimos Tu Huella de Carbono", "ISO 14064 e ISO 14067", "Alcances 1, 2 y 3", "Huella de Producto", "Consultoría Peterson", "Te Acompañamos a Medir", "Hablemos de Tus Emisiones"],
     ["Medimos y gestionamos con vos la huella de carbono de tu empresa, tu producto y tu cadena.", "Inventario GEI bajo ISO 14064 y GHG Protocol: alcances 1, 2 y 3 con datos sólidos.", "Consultora ambiental con equipo en Argentina y presencia en más de 35 países.", "Te preparamos para verificar tu inventario. Hablemos de tus emisiones."],
     quitar=["AFOLU Agro", "Carbono Corporativo", "Reporte De Emisiones"], cambio="Ajustar", nota="Aplica a los dos grupos, Huella carbono y Huella producto.")

prop("Peterson Solutions", "Argentina", "PS Argentina - SuSe - ESG / Reportes", "Reportes ESG",
     "La campaña más sana. La gente escribe «indicadores gri», «estándares gri en español», «gri sectoriales», «csrd»: el anuncio dice «Reporte GRI» pero no «indicadores», «estándares» ni «sectoriales». En Materialidad: «matriz de materialidad», «doble materialidad».",
     ["Reportes de Sostenibilidad", "Estándares GRI en Español", "Indicadores GRI: Te Guiamos", "GRI Sectoriales", "CSRD y Doble Materialidad", "Matriz de Materialidad", "Consultoría ESG", "Consultoría Peterson", "Hablemos de Tu Reporte", "Datos ESG Que Se Sostienen"],
     ["Co-desarrollamos tu reporte de sostenibilidad: estándares GRI, indicadores y materialidad.", "Doble materialidad y CSRD con una hoja de ruta clara. Acompañamos todo el proceso.", "Consultora ESG con equipo en Argentina y presencia en más de 35 países.", "Hablemos de tu reporte: te decimos qué indicadores aplican y por dónde empezar."],
     quitar=["Datos ESG", "Impacto ESG", "Plan ESG Empresa"], cambio="Ajustar", nota="gri + número, «qué es» y «qué significa» siguen a negativo: son lectores del indicador, no clientes.")

prop("Peterson Solutions", "Argentina", "PS Argentina - SuSe - Huella de agua", "Gestion agua",
     "El 100% del gasto reciente es tratamiento de efluentes: no hay título que lo arregle. Si la campaña sigue, el anuncio tiene que decir qué es la huella hídrica corporativa y nombrar ISO 14046.",
     ["Huella Hídrica Corporativa", "Huella de Agua ISO 14046", "Medimos Tu Huella Hídrica", "Riesgo Hídrico en Tu Cadena", "Consultora Ambiental", "Consultoría Peterson", "Te Acompañamos a Medir", "Hablemos de Tu Consumo"],
     ["Medimos con vos la huella hídrica de tu empresa y tu producto bajo ISO 14046.", "Evaluamos riesgo hídrico en operaciones y cadena de valor. No tratamos efluentes: medimos.", "Consultora ambiental con equipo en Argentina y presencia en más de 35 países."],
     quitar=["Gestion Del Agua", "Agua En Industria", "Consumo De Agua", "Agua Agroindustrial"], cambio="Reescribir", nota="Antes: eliminar «gestion del agua industrial» y negativos tratamiento, efluentes, planta, calculadora.")

# ================================================================== validación de longitudes
errores = []
for p in P:
    for t in p["titulos"]:
        if len(t) > H:
            errores.append((p["camp"], p["grupo"], "título", t, len(t)))
    for d in p["descripciones"]:
        if len(d) > D:
            errores.append((p["camp"], p["grupo"], "descripción", d, len(d)))
for x in errores:
    print("!! supera el límite:", x)
if errores:
    sys.exit("Corregir longitudes antes de generar.")

# ================================================================== HTML
def lista(items, lim):
    return "".join(f'<li><span>{e(t)}</span><em>{len(t)}/{lim}</em></li>' for t in items)


bloques = {"Control Union": [], "ISO 27001 (PCU)": [], "Peterson Solutions": []}
for p in P:
    d = p["datos"] or {}
    terms = "; ".join(f"{e(x['termino'])} <em>({x['relacion_anuncio']}, {ars(x['coste'])})</em>" for x in d.get("terminos", [])[:6]) if d else "—"
    org = "; ".join(f"{e(x['query'])} <em>({n(x['impr'])}, pos. {n(x['pos'],0)})</em>" for x in d.get("organico", [])[:6]) if d else ""
    fuerza = {"POOR": "pobre", "AVERAGE": "media", "GOOD": "buena", "EXCELLENT": "excelente"}
    fz = ", ".join(fuerza.get(f, f.lower()) for f in d.get("fuerza", [])) if d else "—"
    actual = " | ".join(d.get("titulos", [])[:10]) if d else "—"
    bloques[p["marca"]].append(f'''<div class="ad">
 <div class="ad-head"><div><div class="brand">{e(p["marca"])} · {e(p["unidad"])}</div><h3>{e(p["camp"].replace(" - Search","").replace(" - SEARCH",""))} › {e(p["grupo"])}</h3></div>
  <div class="meta"><b>{ars(d.get("coste", 0))}</b> gasto en las dos ventanas · fuerza <b>{e(fz)}</b> · {n(len(d.get("titulos", [])))} títulos hoy · <span class="chip">{e(p["cambio"])}</span></div></div>
 <div class="cols">
  <div>
   <div class="lab">Qué dice hoy</div><p class="now">{e(actual)}</p>
   <div class="lab">Qué buscó la gente que lo activó</div><p class="now">{terms}</p>
   {f'<div class="lab">Cómo lo buscan en orgánico</div><p class="now">{org}</p>' if org else ''}
   <div class="lab">Diagnóstico</div><p>{e(p["diagnostico"])}</p>
   {f'<div class="lab">Quitar</div><p class="now">{e(" · ".join(p["quitar"]))}</p>' if p["quitar"] else ''}
  </div>
  <div class="prop">
   <div class="lab">Títulos propuestos</div><ul class="h">{lista(p["titulos"], H)}</ul>
   <div class="lab">Descripciones propuestas</div><ul class="d">{lista(p["descripciones"], D)}</ul>
   {f'<p class="nota">{e(p["nota"])}</p>' if p["nota"] else ''}
  </div>
 </div>
</div>''')

CSS = '''
.ad{ break-inside:avoid; margin:0 0 6mm; border-top:2.2pt solid var(--navy); padding-top:2.5mm; }
.ad-head{ display:grid; grid-template-columns:1fr auto; gap:5mm; align-items:end; margin-bottom:2.5mm; }
.ad-head .brand{ font-size:6.4pt; letter-spacing:.18em; text-transform:uppercase; color:var(--grey); }
.ad-head h3{ font-size:12pt; margin:0; color:var(--navy); }
.ad-head .meta{ font-size:7.6pt; color:var(--grey); text-align:right; } .ad-head .meta b{ color:var(--navy); }
.chip{ display:inline-block; font-size:6.2pt; letter-spacing:.12em; text-transform:uppercase; font-weight:700; color:#fff; background:var(--navy); padding:.6mm 1.8mm; margin-left:1.5mm; vertical-align:middle; }
.cols{ display:grid; grid-template-columns:1fr 1fr; gap:6mm; }
.lab{ font-size:6.3pt; letter-spacing:.16em; text-transform:uppercase; color:var(--grey); font-weight:700; margin:2mm 0 .8mm; }
.cols p{ font-size:8pt; line-height:1.4; margin:0; }
.cols p.now{ color:var(--ink); font-size:7.6pt; } .cols p.now em, .cols p em{ font-style:normal; color:var(--grey); }
.prop{ background:var(--tint); padding:2.5mm 3.5mm 3mm; }
.prop ul{ list-style:none; margin:0; padding:0; }
.prop li{ display:flex; justify-content:space-between; gap:3mm; font-size:8.2pt; line-height:1.35; padding:.7mm 0; border-bottom:.4pt solid #dde3e5; color:var(--navy); }
.prop ul.d li{ font-size:7.8pt; color:var(--ink); }
.prop li em{ font-style:normal; color:var(--grey); font-size:6.6pt; white-space:nowrap; font-variant-numeric:tabular-nums; }
.prop .nota{ font-size:7.4pt; color:var(--grey); margin-top:2mm; line-height:1.4; }
.rules{ display:grid; grid-template-columns:1fr 1fr; gap:6mm; }
.rules h4{ font-size:10pt; color:var(--navy); margin:0 0 1.5mm; } .rules p, .rules li{ font-size:8.4pt; line-height:1.45; }
.rules ul{ margin:0; padding-left:3.5mm; }
'''

portada = f'''<div class="cover">
 <div class="hero">
  <div class="eyebrow">Propuestas de anuncios · campañas de búsqueda · Control Union → ISO 27001 → Peterson Solutions</div>
  <h1>Qué dice cada anuncio, qué buscó la gente, y qué debería decir</h1>
  <p class="sub">{len(P)} grupos de anuncios que concentran el gasto, leídos por API: títulos y descripciones activos, los términos de búsqueda que los activaron con su relación con el anuncio, y cómo busca el mismo tema la gente en orgánico. Para cada uno, títulos y descripciones nuevos dentro de los límites de Google (30 y 90 caracteres), qué quitar y qué no se arregla con el anuncio.</p>
  <div class="hero-nums">
   <div><div class="n">{len(P)}</div><div class="l">grupos con propuesta</div></div>
   <div><div class="n">{sum(len(p["titulos"]) for p in P)}</div><div class="l">títulos propuestos, validados</div></div>
   <div><div class="n">{sum(1 for p in P if p["cambio"] == "Reescribir")}</div><div class="l">anuncios a reescribir de cero</div></div>
   <div><div class="n">{sum(1 for p in P if (p["datos"] or {}).get("fuerza") == ["POOR"])}</div><div class="l">anuncios con fuerza «pobre» hoy</div></div>
  </div>
 </div>
 <div class="top5"><h2>Lo que se repite en casi todos</h2>
  <div class="rules">
   <div><h4>Vocabulario de la otra marca</h4><p>Anuncios de Control Union que dicen «acompaña», «apoio», «support», «partner», «prepara tu auditoría». Control Union certifica, audita, inspecciona y verifica. Los de Peterson están mejor, pero pueden ser más Peterson: «nosotros», acompañamos, co-desarrollamos.</p></div>
   <div><h4>La norma como la escribe la gente</h4><p>«global gap» sin puntos, «iso iec 27001 2022», «gots 8.0», «une en 15343 2008», «canadagap 2026». Un título con la forma exacta que la gente escribe sube la relación y baja el CPC.</p></div>
   <div><h4>Lo informativo no se responde con títulos</h4><p>«qué es», «que significa», «what does … mean», «dominios», «pdf»: van a negativos. Excepción: «pefc o que é» y «que es gots», donde un título que responde captura al que va a certificar.</p></div>
   <div><h4>Cifras que ya están en los anuncios</h4><p>«Más de 100 años certificando», «80 países», «274 oficinas» aparecen en los anuncios PCU de ISO 27001: son las cifras de Control Union. Confirma de qué marca es esa campaña. Peterson usa las suyas: desde 1920, más de 35 países.</p></div>
  </div>
 </div>
 <p class="foot">Documento interno sin identidad de marca: cubre anuncios de Control Union y de Peterson Solutions; cada propuesta se carga dentro de su marca. Fuente: Google Ads por API (anuncios y estructura al 25 sep; términos 1 ago – 24 sep 2026) y Search Console (histórico completo). Supuestos a confirmar con cada unidad antes de publicar: alcances acreditados (ENAC para ISO 27001, livestock en NOP). Generado el {HOY}.</p>
</div>'''

cuerpo = ""
for marca, titulo in (("Control Union", "Control Union"), ("ISO 27001 (PCU)", "ISO 27001 · campañas «PCU»"), ("Peterson Solutions", "Peterson Solutions")):
    cuerpo += f'<div class="page"><h2 class="sec-title">{e(titulo)}</h2><p class="sec-sub">{len(bloques[marca])} grupos. Cada ficha: lo que dice hoy, lo que buscó la gente, el diagnóstico y el anuncio propuesto.</p>' + "".join(bloques[marca]) + '</div>'

doc = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Propuestas de anuncios · campañas de búsqueda</title>
<link rel="stylesheet" href="estilo-mejoras.css"><style>{CSS}</style></head><body>{portada}{cuerpo}</body></html>'''
open(os.path.join(INF, "propuestas-anuncios.html"), "w", encoding="utf-8").write(doc)
print(f"-> informe/propuestas-anuncios.html · {len(P)} grupos · {sum(len(p['titulos']) for p in P)} títulos · sin errores de longitud")
