# Brief: optimización de las campañas de Google Ads de Peterson Solutions Argentina

> Copiá todo este archivo en el proyecto de Paid Media. Los datos salen de Google Ads, GA4 y Search Console
> (solo lectura) del **1 de agosto al 25 de noviembre de 2026**, extraídos el 26 de noviembre de 2026.

---

## 0. Qué te pido

Sos el especialista de paid media que arma y ajusta las campañas de **Peterson Solutions** (PS). Te paso el
diagnóstico de las 8 campañas de búsqueda de PS en Argentina, lo que se acordó con Peterson en una reunión y
las mejoras que salen de los datos. Necesito tres cosas:

1. **Plan de cambios por campaña**, en una tabla con estas columnas: prioridad (alta / media / baja), campaña,
   grupo o anuncio (id), acción, qué cargar (texto literal, con concordancia), motivo (el dato) y estado. El
   estado puede ser «listo» o «espera la validación #N» (son las preguntas de la sección 6).
2. **Archivo para Google Ads Editor** solo con los cambios «listo»: CSV en UTF-16 con tabulaciones y
   «Ad type» = «Responsive search ad» declarado en cada anuncio. Los pendientes van en un archivo aparte, sin importar.
3. **Anuncios nuevos completos** para cada grupo que cambia: 15 títulos de hasta 30 caracteres, 4
   descripciones de hasta 90, y el motivo de cada uno. Marcá cuáles conviene fijar o priorizar.

No armes campañas nuevas. La estructura general está bien: se ajusta y se prueban cosas nuevas. No borres
nada: pausá. Usá los nombres reales de campaña y grupo tal como figuran abajo. Si algo no está en este brief,
preguntá antes de inventarlo.

## 1. Reglas de marca (no negociables)

- **Peterson Solutions es una consultora.** Dice: *acompañamos, co-desarrollamos, preparamos para certificar*.
  **Nunca dice «certificamos»** ni sugiere que emite certificados: nada de «Certificación biomasa» ni
  «Auditorías de certificación» como servicio propio.
- Control Union es otra marca del grupo (organismo certificador) y **no se mezcla**: ni sus cifras, ni su tono, ni su nombre.
- Cifras de PS: **desde 1920, empresa familiar, +1.000 personas, +35 países.** Nunca «+100 años» ni «+80 países»
  (son de Control Union).
- Tono: personal, empático, positivo, activo; «nosotros», voz activa, el protagonista es el cliente.
- Español con tildes y eñes (hoy muchos textos dicen «Gestion», «Hidrica», «Evalue», «Acompanamos»).
- Trato: **pendiente de la validación #1**. Los borradores de este brief van en «usted», como el sitio y 34 de
  los 39 anuncios; si eligen «vos», adaptá todo.

## 2. Diagnóstico (1 ago – 25 nov 2026)

Cuenta de Google Ads 1606422184. Las 8 campañas arrancaron el 22 jul 2026, todas con «Maximizar conversiones»,
**ARS 2.268 por día cada una**, solo Red de Búsqueda, idioma español y ubicación Argentina con «Presencia o
interés». La campaña «PS Argentina - Evento TecnoManí - Search» termina el 27/11 y queda fuera de este trabajo.

| Campaña | Gasto ARS | Clics | Impr. | Conv. | Keyword que se lleva el gasto |
|---|---:|---:|---:|---:|---|
| PS Argentina - SuSo - Agricultura regenerativa- Search | 282.334 | 727 | 27.586 | 0 | 3 keywords = 99% (2 de concordancia amplia) |
| PS Argentina - SuSe - Huella de carbono / GEI - Search | 271.044 | 283 | 15.563 | 0 | 3 amplias = 90% |
| PS Argentina - SuSe - ESG / Reportes - Search | 246.508 | 159 | 4.594 | 0 | «reporte GRI» [f]+[e] = 77% |
| PS Argentina - Bioenergia / Biocombustibles - Search | 230.195 | 161 | 8.842 | 0 | «bioenergia sostenible» [f] = 100% |
| PS Argentina - SuSe - Huella de agua - Search | 181.175 | 62 | 1.408 | 0 | «gestion del agua industrial» [f] = 96% |
| PS Argentina - CeSu - Preparacion para certificaciones - Search | 94.280 | 26 | 967 | 0 | «auditoria interna certificaciones» [f] = 91% |
| PS Argentina - SuSo - Trazabilidad / EUDR - Search | 56.546 | 21 | 649 | 0 | «trazabilidad de proveedores» [f] = 49% |
| PS Argentina - SuSo - Abastecimiento sostenible - Search | 45.871 | 23 | 945 | 0 | 3 keywords = 87% |
| **Total** | **1.407.954** | **1.462** | **60.554** | **0** | top 10 keywords = 83% del gasto |

Gasto por mes: agosto ARS 350.122 · septiembre 358.223 · octubre 445.687 · noviembre (1–25) 253.922.

**Lo que dicen los datos**

1. **No hay medición de conversiones.** Google Ads registra 0 conversiones en cuatro meses (una sola
   «conversión total», un «Clic saliente» en ESG). En GA4, de 834 sesiones de Paid Search hubo **1 visita
   real a /gracias/**, 3 clics en email y 1 clic para llamar. «Maximizar conversiones» está optimizando a ciegas.
   La acción «Vista de página» figura como conversión principal de la cuenta: si llega a medir, va a contar
   cualquier vista como conversión. *Supuesto sin verificar:* el porqué del 0 (etiqueta que no dispara en
   americas.peterson-solutions.com o acciones atadas a los sitios de Control Union).
2. **Pocas palabras se llevan la plata porque son las únicas con volumen, no porque sean las mejores.** De 253
   keywords activas, **186 no tuvieron ni una impresión** en cuatro meses (son de cola larga y casi nadie las
   busca). El gasto cae en las pocas amplias o de frase, que abren la puerta a búsquedas de otra intención:
   - «bioenergia sostenible» → biogás, «energía biomasa», nombres de empresas (Fenix Bioenergy, Dosbio, Enerfree).
   - «gestion del agua industrial» → tratamiento de efluentes y plantas de tratamiento (no es el servicio).
   - «reporte GRI» → «estándares GRI», «GRI 306», «GRI 404-1»: gente que busca el texto de la norma.
   - «agricultura regenerativa (en) argentina» [amplia] → «tecnología agrícola», Argenbio, Corteva, Rizobacter,
     camelina, «agricultura» (1.538 impr.).
   - «inventario gases de efecto invernadero» / «huella de carbono producto» [amplias] → «ISO 14001» (841
     impr.), «bonos de carbono», Verra, «consultora ambiental».
   - «auditoria interna certificaciones» → «auditor interno ISO 9001», cursos, diplomados, SENA, CIA, COSO.
   - Google esconde el 58% del gasto en «otros términos» (solo vemos ARS 590.946 de 1.407.954). Las
     conclusiones salen de la parte visible: sirven para decidir dirección, no para cifras exactas.
3. **Un solo anuncio copiado en todos los grupos.** Cada campaña repite el mismo RSA en sus 4 o 5 grupos, así
   que el anuncio no acompaña las keywords del grupo. Muchos niveles de calidad dan 1 a 3.
4. **Errores en los anuncios publicados:**
   - Las extensiones de texto destacado de las 8 campañas dicen «+100 años de experiencia», «Presencia en +80
     países», «Respaldo internacional», «Alcance mundial»: cifras de Control Union.
   - Huella de agua publica textos internos: «Testee demanda en sectores con alto consumo de agua y presion
     ESG.» y «…definir alcance y viabilidad del servicio.»
   - Bioenergía y Preparación dicen «Biomasa Certificacion», «Certificacion Biomasa», «Certificacion Sostenible» y
     «Auditorias De Certificacion»: chocan con la regla de marca.
   - Solo 2 sitelinks por campaña («Contáctanos» e «Industrias»).
5. **Landings desalineadas.** Huella de agua lleva a «GEI y servicios medioambientales», una página de huella de
   carbono. ESG / Reportes lleva a la página general de Estrategia y no a la de Reporte.
6. **Ubicación.** El 8% del gasto (ARS 119.399, 109 clics) va a personas fuera de Argentina «interesadas» en Argentina.
7. **Presupuesto.** ESG / Reportes perdió el 67% de las impresiones por presupuesto en octubre (el 21% en
   noviembre); Bioenergía, el 48% en octubre. Con CPC de ARS 1.000 a 3.500, ARS 2.268 por día alcanza para 1 a
   2 clics diarios por campaña.
8. **Superposición con Control Union en la misma cuenta.** CU Argentina tiene campañas de ISCC EU/PLUS, 2BSvs,
   EUDR («eudr due diligence» [f]), GlobalG.A.P. («buenas practicas agricolas certificacion» [f]), FSA,
   Regenagri y verificación GEI. En una misma cuenta, Google muestra un solo anuncio por búsqueda: si PS suma
   ISCC, 2BSvs o BPA sin cortar por intención, compite contra CU. Regla propuesta: **PS = consultoría,
   preparación, implementación, «cómo cumplir»; CU = certificación, auditoría, verificación, certificadora.**
   El corte final lo decide Felipe (sección 6, decisiones internas).

**Search Console: cómo llega lo orgánico** (americas.peterson-solutions.com, datos desde el 22 mar 2026, que es
lo más viejo disponible para esta propiedad, hasta el 24 nov 2026)

- Total del sitio: 1.149 clics y 74.303 impresiones; casi todo viene de páginas en inglés (RED III) y en portugués.
- **Argentina: 2.311 impresiones y 34 clics en 8 meses, casi todo por la marca («peterson»).** No hay ni una
  búsqueda orgánica argentina sobre huella hídrica, huella de carbono, ESG, agricultura regenerativa ni certificaciones.
- Las páginas de servicio en español suman 1.710 impresiones temáticas y 3 clics en total. La mejor posicionada
  es «Regulación Europea contra la deforestación (EUDR)»: 707 impresiones por «eudr», posición media 19,5
  (zona 8–20, donde lo pago complementa bien).
- **Conclusión:** no hay canibalización. Para estos servicios, lo pago es hoy la única fuente de tráfico
  calificado, así que cada peso tiene que caer en la intención correcta. El SEO se trabaja aparte.

**GA4 (Paid Search, mismo período):** 834 sesiones (Ads contó 1.503 clics; la diferencia se explica sobre todo
por el banner de cookies), 57% con interacción y 85 segundos de promedio. Landings: Agricultura regenerativa 327
sesiones, GEI 215, Estrategia 104, Bioenergía 80.

## 3. Cambios para toda la cuenta de PS

| Prio. | Acción | Qué cargar | Motivo | Estado |
|---|---|---|---|---|
| Alta | Medición de conversiones | Conversión principal = vista a /gracias/ y /gracias-por-contactarnos/ en americas.peterson-solutions.com + clic en email. «Vista de página» y «Clic saliente» pasan a secundarias. | 0 conversiones en 4 meses con «Maximizar conversiones» | Decisión interna A |
| Alta | Estrategia de puja | Mientras no haya 15 conversiones o más en 30 días: «Maximizar clics» con CPC máximo de ARS 2.500. Cuando la medición funcione, volver a «Maximizar conversiones». | Sin conversiones, el algoritmo no tiene señal | Decisión interna B |
| Alta | Textos destacados (8 campañas) | Quitar «+100 años de experiencia», «Presencia en +80 países», «Respaldo internacional», «Alcance mundial». Cargar «Desde 1920», «Empresa familiar», «+1.000 personas», «Presentes en +35 países», «Acompañamiento a medida». | Cifras de Control Union en anuncios de PS | Espera #4 |
| Alta | Ubicación (8 campañas) | Opción de ubicación: «Presencia» (personas que están en Argentina) | 8% del gasto fuera del país | Listo |
| Media | Un RSA por grupo | Cada grupo, su anuncio, con las keywords del grupo en los títulos 1 a 3 | Hoy es un anuncio copiado en todos los grupos | Listo (en cada campaña) |
| Media | Sitelinks | Sumar 2 por campaña a páginas de servicio: «Reporte de sostenibilidad», «Huella de carbono», «Huella hídrica», «Preparación certificación», «Agricultura regenerativa», «EUDR y trazabilidad», «Webinar EUDR», «Bioenergía» (hasta 25 caracteres, con 2 descripciones de hasta 35) | Hay solo 2 sitelinks | Listo |
| Media | Corte CU / PS | Negativas en las campañas de PS: certificadora, certificadoras, «organismo certificador», «quien certifica», verificacion, verificador. Negativas espejo en las de CU: consultoria, consultora, preparacion, implementacion. | Las dos marcas compiten en la misma cuenta | Decisión interna C |
| Baja | Ortografía | Todos los textos nuevos con tildes | Calidad y marca | Listo |

## 4. Cambios por campaña

### PS Argentina - SuSe - Huella de agua - Search *(acordado en la reunión)*

- **Pausar el grupo «Gestion agua»** (id 198500852333): ARS 173.517 de 181.175 (96%) con búsquedas de
  tratamiento de efluentes. Estado: listo.
- **Grupo «Agua agroindustria»** (id 198500852133) → renombrar «Huella hídrica empresas» y abrirlo a cualquier
  empresa: sin agroindustria y sin industria alimentaria.
  - Pausar: uso de agua agroindustria [e][f], huella hidrica agroindustria [e][f], gestion hidrica alimentos
    [e][f], consumo de agua industria alimentaria [e][f].
  - Sumar [f]: «huella hídrica de mi empresa», «huella hídrica empresa», «huella hídrica de una empresa»,
    «huella hídrica corporativa», «medir huella hídrica», «reducir huella hídrica», «impacto hídrico empresa».
  - Estado: listo; «huella hídrica de producto» espera la #12.
- **Grupo «Huella hidrica»** (id 198500852293): se mantiene. Negativa de grupo: «calculadora». Hay 7 búsquedas
  de calculadoras gratuitas. Espera la #13.
- **Grupo «Riesgo hidrico»** (id 198500852373), keyword «riesgo climatico» [e][f]: sumar negativas de grupo
  seguro, seguros, pronostico, pronóstico, clima, noticias, inundaciones, mapa, ipcc, onu, tesis, monografia,
  curso. Espera la #10 (si el servicio va en ESG) y la #11 (lista final).
- **Negativas de campaña** (hoy no tiene ninguna): efluentes, «tratamiento de aguas», «tratamiento de
  efluentes», «planta de tratamiento», potabilizadora, «agua potable», plomero, curso, pdf, gratis, tesis,
  monografia, «que es», definicion, ejemplo, ejemplos. Estado: listo.
- **Anuncios** (ids 817970221136, 817970221139, 817970221145; el de «Gestion agua» queda pausado con su grupo):
  el foco es el **impacto** que la empresa quiere reducir, no la medición de consumo.
  - Sacar: «Consumo De Agua», «Medicion De Consumo», «Agua Agroindustrial», «Agua En Industria»,
    «Evalue huella de agua, consumo y riesgos hidricos en operaciones.», «Testee demanda en sectores con alto
    consumo de agua y presion ESG.», «Hable con Peterson para definir alcance y viabilidad del servicio.»
  - Títulos propuestos: Huella hídrica de su empresa · Mida su impacto en el agua · Evaluación de huella hídrica ·
    Huella hídrica corporativa · Reduzca su impacto hídrico · Impacto hídrico de su empresa · Riesgo hídrico en
    su cadena · Del diagnóstico a la acción · Agua y cadena de valor · Hablemos de su huella hídrica · Peterson
    Solutions · Desde 1920 · +35 países · Agende una reunión (+ «ISO 14046» si lo confirma la #8).
  - Descripciones propuestas: «Medimos el impacto de su empresa sobre el agua, no solo cuánto consume.» ·
    «Lo acompañamos a evaluar su huella hídrica y a priorizar acciones para reducirla.» · «Identifique los
    riesgos hídricos de sus operaciones y de su cadena de valor.» · «Hablemos de su empresa: armamos juntos el
    plan para reducir su impacto hídrico.»
- **Landing**: pasar de «GEI y servicios medioambientales» a /service/estrategia-y-gestion-de-sostenibilidad/gestion-eficiente-del-agua/
  o a una página nueva de huella hídrica. Espera la #9.

### PS Argentina - SuSe - ESG / Reportes - Search *(acordado en la reunión)*

- **Presupuesto**: de ARS 2.268 a ARS 3.400 por día (+50%), financiado con lo que deja de gastar «Gestion
  agua». Espera la #14 y la decisión de Felipe.
- **Sumar «reporte»** en el grupo «Reportes ESG» (id 198500855173), [f]: «reporte de sostenibilidad», «reporte
  ESG», «informe de sostenibilidad», «elaboración de reporte de sostenibilidad», «consultora reporte de
  sostenibilidad», «reporte de sostenibilidad empresas», «memoria de sostenibilidad». Estado: listo.
- **Materialidad dentro de Reportes**: recrear en «Reportes ESG» las keywords doble materialidad [f][e],
  analisis de materialidad ESG [f][e], matriz de materialidad consultoria [f][e] y evaluacion de impacto ESG
  [f][e], y pausar el grupo «Materialidad» (id 198500854973). Estado: listo.
- **«reporte GRI» [f]** (ARS 162.275): negativas de campaña estandares, estándares, estandar, estándar,
  standard, standards, ejemplos. Espera la #17.
- **Consultoría ESG** (grupo id 198500854933): sumar [f] «consultora ESG», «consultoría ESG», «consultora de
  sostenibilidad», «consultoría en sostenibilidad empresas». Espera la #16.
- **Landing** de «Reportes ESG»: /service/estrategia-y-gestion-de-sostenibilidad/estrategia-de-sostenibilidad-y-reporte/
  (tiene la sección «Análisis de materialidad y diagnóstico ESG»). Estado: listo.
- **Anuncio de Reportes ESG** (nuevo RSA): títulos con «Reporte de sostenibilidad», «Reporte ESG para su
  empresa», «Análisis de doble materialidad». Descripciones: «Elaboramos su reporte de sostenibilidad con GRI y
  análisis de doble materialidad.» · «Defina temas materiales, indicadores y metas: un reporte claro y con respaldo.»

### PS Argentina - Bioenergia / Biocombustibles - Search *(acordado en la reunión)*

- **Sacar RED**: pausar RED II biocombustibles [e][f] y quitar el título «RED II Support» de los 4 anuncios
  (ids 817970221391, 817970221382, 817970221388, 817970221385). Renombrar el grupo «ISCC RED» (id
  198500855693) a «ISCC EU y PLUS». Espera la #18 (si también sale REDcert).
- **ISCC EU y PLUS** en ese grupo, con intención de consultoría [f]: «consultoria ISCC», «consultora ISCC»,
  «preparacion ISCC», «implementacion ISCC», «ISCC PLUS consultoria», «preparacion auditoria ISCC».
- **Grupo nuevo «2BSvs»**, parecido a ISCC [f]: «consultoria 2BSvs», «preparacion 2BSvs», «implementacion
  2BSvs», «2BSvs biocombustibles consultoria».
- ISCC y 2BSvs esperan la #19, la #21 y la decisión interna C (corte con CU Argentina - Biocombustible).
- **«bioenergia sostenible» [f]** (100% del gasto): pasarla a [e] y sumar negativas biogas, biogás, «energia
  biomasa», «energía biomasa», fenix, dosbio, biodes, enerfree, bioenergy. Espera la #20.
- **Títulos que se van** por la regla de marca: «Biomasa Certificacion», «Certificacion Biomasa», «Biofuels
  Compliance». Entran: «Preparación ISCC EU y PLUS» · «Preparación para 2BSvs» · «Balance de masa ISCC» ·
  «Consultoría en bioenergía» · «Prepárese para certificar».
- **Descripción** «Soporte en ISCC, 2BSvs, biomasa, trazabilidad y mass balance.» → «Lo acompañamos a
  prepararse para ISCC EU, ISCC PLUS y 2BSvs, de punta a punta.» Landing /industry/bioenergia/ (ya nombra ISCC
  EU, ISCC PLUS y 2BSvs).

### PS Argentina - SuSe - Huella de carbono / GEI - Search *(acordado en la reunión)*

- **«Scope» → «alcance»** en los 4 anuncios (ids 817970221190, 817970221184, 817970221193, 817970221187):
  «Prepare inventarios GEI, Scope 1, 2 y 3 con soporte experto.» → «Prepare inventarios GEI de alcance 1, 2 y
  3 con soporte experto.» Renombrar el grupo «Scope 1 2 3» a «Alcance 1 2 3». La keyword «scope 3» [f][e]
  espera la #25. Estado del texto: listo.
- **Descarbonización y cadena de valor en las descripciones**: «Conecte huella de carbono con decisiones ESG y
  comerciales.» → «Mida su huella de carbono y defina un plan de descarbonización con metas claras.» La
  descripción 1 ya nombra la cadena de valor. Alternativa para la 4: «Sume a proveedores y clientes: alcance 3 y
  descarbonización en su cadena de valor.» Ajustar las palabras con la #24.
- **Concordancia**: pausar las amplias «inventario gases de efecto invernadero», «huella de carbono producto» e
  «iso 14067 huella de carbono» (90% del gasto). Las versiones [f][e] ya existen; sumar «huella de carbono
  producto» [f] e «iso 14067» [f]. Estado: listo.
- **Negativas de campaña** (hoy no tiene): «iso 14001», 14001, verra, curso, cursos, pdf, gratis, empleo,
  tesis, monografia, «que es», definicion, ejemplo, ejemplos, plantilla. «bonos de carbono» espera la #23.
  ISO 14001 se negativiza acá, pero puede abrir grupo en Preparación (#27).
- **Huella de producto** (grupo id 198500853733): 53% del gasto y 159 clics, con su propio anuncio. Espera la #22.

### PS Argentina - CeSu - Preparacion para certificaciones - Search *(acordado en la reunión)*

- **Grupo nuevo «Buenas prácticas agrícolas»** [f]: «implementacion buenas practicas agricolas», «consultoria
  buenas practicas agricolas», «preparacion BPA», «implementacion BPA». Anuncio: «Buenas prácticas agrícolas» ·
  «Implementación de BPA» · «Lo preparamos para implementar buenas prácticas agrícolas y llegar a la auditoría.»
  Espera la #26 (esquema y landing) y la decisión interna C (CU tiene «buenas practicas agricolas certificacion»).
- **«auditoria interna certificaciones» [f]** (91% del gasto): pausarla (queda la [e]) y sumar negativas
  «auditor interno», «iso 9001», 9001, diplomado, sena, coso, cia, irca, «bureau veritas», curso, cursos. Espera la #28.
- **Títulos**: «Certificacion Sostenible» → «Preparación para certificar»; «Auditorias De Certificacion» →
  «Auditoría interna previa» (los 5 anuncios). Estado: listo.
- Pausar los grupos «ISCC» y «2BSvs» de esta campaña (0 impresiones en 4 meses) si la #21 confirma que todo va en Bioenergía.

### PS Argentina - SuSo - Agricultura regenerativa- Search *(propuesta de los datos)*

- **Concordancia**: pausar las amplias «agricultura regenerativa argentina» (ARS 152.151) y «agricultura
  regenerativa en argentina» (ARS 99.457; son la misma keyword repetida). Sumar [f] «agricultura regenerativa
  argentina», «agricultura regenerativa empresas», «implementar agricultura regenerativa».
- **Negativas de campaña**: tecnologia, tecnología, agtech, argenbio, corteva, rizobacter, stoller, camelina,
  «pools de siembra», «agricultura de precision», «productos organicos», fragaria, agribio.
- Es la campaña con más clics (727 de 1.462) y 0 contactos. Espera la #32 (productor o empresa de la cadena).

### PS Argentina - SuSo - Trazabilidad / EUDR - Search

- **Geolocalización** (grupo id 198500851613): no tocar hasta tener la información de Samo (#29). «mapeo de
  parcelas» [f] ya está pausada (9 clics, ARS 23.839).
- **Prueba de landing** del grupo «EUDR» (id 198500851653): /regulacion-europea-contra-la-deforestacion-eudr/
  (3.100 palabras, posición orgánica 19,5 para «eudr»). Espera la #31.
- **Fecha**: la aplicación para grandes empresas que manejamos es el 30 dic 2026 (a confirmar). La #30
  pregunta si se refuerza el presupuesto en diciembre.
- Superposición con CU («eudr due diligence» [f] de CU vs «due diligence EUDR» [f] de PS): decisión interna C.

### PS Argentina - SuSo - Abastecimiento sostenible - Search *(baja)*

- Pausar las keywords en inglés: supplier performance, supplier risk management, supply chain sustainability
  consulting, responsible sourcing argentina, sustainable sourcing latam (todas [f][e]). Traen Coupa, Ariba, DHL,
  y la campaña segmenta en español.

## 5. Cosas nuevas para probar (una por vez, 4 semanas cada una)

1. **Oferta de entrada** en una campaña (si la #5 la habilita): una variante de anuncio con «Reunión de 30
   minutos sin costo» o «Diagnóstico inicial» contra el «Agende una reunión» actual.
2. **Landing con más contenido**: EUDR en la página de la regulación contra la de servicio (#31).
3. **Horario comercial** (#7): anuncios de lunes a viernes en horario de oficina contra 24/7, en ESG o Carbono.
4. **Presupuesto concentrado**: ESG a ARS 3.400 por día durante 4 semanas, medir impresiones perdidas por
   presupuesto y contactos.
5. **Frase contra amplia** en Agricultura regenerativa: comparar CPC, búsquedas y tiempo en la página antes y después.

Qué medir en todas: contactos reales (gracias + email), CTR, CPC, % de búsquedas relevantes entre las visibles y
% de impresiones perdidas por presupuesto.

## 6. Validaciones pendientes

**Con Peterson (documento compartido, 32 preguntas):** https://claude.ai/artifact/BN2i8JryxkaX1MRuFJDrav
Las más importantes: #1 tono, #2 qué es un contacto válido, #4 cifras de marca, #9 landing de agua, #14
presupuesto ESG, #18 RED, #26 esquema de BPA, #29 geolocalización (Samo).

**Decisiones internas (Felipe):**
- **A. Medición**: cómo se configura la conversión principal de PS y por qué hoy da 0.
- **B. Puja**: «Maximizar clics» con tope hasta tener conversiones, o seguir con «Maximizar conversiones».
- **C. Corte CU / PS** en ISCC, 2BSvs, EUDR, BPA y huella de carbono: negativas cruzadas en las dos marcas.

## 7. Límites de los datos

- Google Ads esconde el 58% del gasto en «otros términos»: no se puede atribuir todo a búsquedas concretas.
- Con 0 conversiones no hay base para optimizar por CPA. Todo se decide por relevancia de la intención.
- GA4 pierde visitas por el banner de cookies (834 sesiones contra 1.503 clics).
- La posición media de Search Console es un promedio: tomala como banda, no como número fino.
- Search Console y Google Ads no se suman entre sí.
