# Meta Ads: lectura y subida de campañas

Dos caminos que se complementan:

| | Para qué | Cómo |
|---|---|---|
| **Extracción** (`scripts/meta_export.py`) | Foto completa de la cuenta y métricas día a día, igual que Google Ads, para el análisis y el tablero | Marketing API con token de usuario del sistema |
| **Órdenes desde acá** | Crear, editar, pausar campañas conversando con Claude | Servidor MCP oficial de Meta (`https://mcp.facebook.com/ads`) |
| **Subida de campañas armadas** (`scripts/meta_subir.py`) | Subir una campaña preparada en un JSON versionado (como el CSV de Editor en Google) | Marketing API, todo se crea en PAUSA |

Nada se activa solo: lo que se crea queda **en pausa** y activar (empezar a gastar) es siempre una orden aparte y
explícita.

## 1. Lo que tiene que hacer alguien con control total del portfolio comercial

Claude no puede crear cuentas, apps ni tokens, ni recibirlos por chat.

1. **Confirmar qué cuentas publicitarias** se usan y de qué marca es cada una (CU / PS / PCU). Las campañas tienen que
   empezar con el prefijo de la marca («CU Argentina - …»), igual que en Google Ads: así se separan los datos.
2. **Crear una app de Meta** en https://developers.facebook.com/apps (tipo empresa, asociada al portfolio).
   Agregarle los casos de uso **«Create & manage ads with ads MCP server»** y **Marketing API**. El nivel de acceso
   «Limited» (antes «Standard») se otorga solo y alcanza para cuentas propias; «Full» solo hace falta para
   administrar cuentas de terceros.
3. **Crear un usuario del sistema** en Configuración del negocio › Usuarios › Usuarios del sistema, con rol
   **Empleado** (el MCP de Meta rechaza los tokens de rol Administrador). Asignarle:
   - las cuentas publicitarias: «Ver rendimiento» alcanza para leer; «Administrar campañas» para subir;
   - la página de Facebook (y la cuenta de Instagram) con las que se publican los anuncios.
4. **Generar el token** de ese usuario del sistema para la app, con permisos `ads_read`, `ads_management`,
   `ads_mcp_management`, `business_management`, `pages_show_list`, `pages_read_engagement`.
5. **Guardarlo uno mismo** en `proyecto/meta-ads.json` (no pegarlo en el chat ni subirlo a ningún lado):
   ```json
   {"access_token": "EAAG...", "version": "v26.0", "cuentas": {"act_1234567890": "CU Argentina"}}
   ```
   Si se omite `cuentas`, se extraen todas las que ve el token.
6. Opcional pero recomendado: en el portfolio, **reglas del servidor MCP de anuncios** para limitar lo que pueden
   hacer los agentes de IA (por ejemplo, cambios de presupuesto).

## 2. Extracción

```bash
python scripts/meta_export.py --probar
```
```bash
python scripts/meta_export.py --desde 2026-09-01 --hasta 2026-10-30
```

Trae cuentas, campañas (objetivo, **estrategia de puja**, presupuesto, estado efectivo, problemas), conjuntos
(optimización, evento de cobro, puja y tope, **segmentación completa**, píxel/evento, atribución, fase de
aprendizaje), anuncios (motivo de rechazo y creativo completo), audiencias, píxeles, historial de cambios, métricas
por anuncio y por día con cada acción y su costo, y desgloses por edad y sexo, plataforma y ubicación, país y
dispositivo. A diferencia de Google Ads, en Meta la estrategia de puja, el tope y el evento de optimización sí vienen
por API.

Salida separada por marca en `datos/meta/api/<marca>/`.

## 3. Órdenes desde Claude (MCP oficial)

Configurado el 10 nov 2026 en `Optimizaciónes SEO-SEM/.mcp.json` (servidor «meta-ads»). No usa el inicio de sesión de
Facebook: `scripts/meta_mcp_headers.py` le pasa el token del usuario del sistema que está en `meta-ads.json`, así que al
regenerar el token alcanza con cambiarlo ahí. Se carga al abrir una sesión nueva de Claude en esa carpeta (la primera
vez pide aprobar el servidor del proyecto). App de Meta: 3772720962878154 (portfolio «Marcomms - Cuentas de META»).

Alternativa con inicio de sesión de Facebook, si algún día hace falta (requiere cargar la URL de retorno de Claude Code
en «Facebook Login for Business» de la app):
```bash
claude mcp add --transport http --client-id 3772720962878154 meta-ads https://mcp.facebook.com/ads
```
Herramientas principales (99 al 10 nov 2026):
`ads_get_ad_entities` (informes), `ads_create_campaign` / `ads_create_ad_set` / `ads_create_ad` (crean en pausa),
`ads_create_creative`, `ads_update_entity`, `ads_activate_entity` (activa y empieza a gastar), audiencias, vista
previa de anuncios, biblioteca de anuncios, pruebas A/B e historial de cambios. Está en beta abierta desde abril de
2026, sin costo por ahora.

Regla de trabajo: Claude no crea, edita ni activa nada sin un «sí» explícito en el chat para esa acción.

## 4. Subida de una campaña armada

```bash
python scripts/meta_subir.py campanas/<carpeta>/meta.json
```
```bash
python scripts/meta_subir.py campanas/<carpeta>/meta.json --validar
```
```bash
python scripts/meta_subir.py campanas/<carpeta>/meta.json --subir
```

Sin opción revisa en local: prefijo de marca, dominio del enlace (CU → controlunion.com, PS →
peterson-solutions.com), vocabulario prohibido por marca y largos de texto. `--validar` le pide a Meta que revise
la campaña y los creativos con `validate_only`, sin crear nada; los conjuntos y anuncios solo se pueden validar
creándolos, así que quedan para `--subir`. `--subir` crea todo en pausa y deja el registro con los id en la carpeta
de la campaña. El formato del JSON está al principio de `scripts/meta_subir.py`.
