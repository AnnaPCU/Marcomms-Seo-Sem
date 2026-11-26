# Cómo arrancar

## 1. Instalar Claude Code

En una terminal (PowerShell):

    npm install -g @anthropic-ai/claude-code

Si no tenés Node.js, bajalo de nodejs.org primero.

## 2. Abrir el proyecto

    cd "C:\Users\tmisrahi\OneDrive - Peterson and Control Union\Documentos\gsc-extraccion\proyecto"
    claude

La primera vez pide iniciar sesión con tu cuenta de Claude.

## 3. El primer pedido

Copiá y pegá esto tal cual:

---
Leé CLAUDE.md completo antes de hacer nada.

Quiero reconstruir el histórico máximo de Search Console (16 meses, el tope que guarda
Google) para las 10 propiedades, sumando las dimensiones date y device que faltaron en la
extracción anterior, y rehacer el análisis completo sobre esa base.

Empezá por:
1. Verificar que la autenticación funciona y listar las propiedades.
2. Detectar cuál es la fecha más vieja con datos disponibles, probando hacia atrás.
3. Mostrarme el plan de extracción con el volumen estimado antes de bajarlo todo.

En datos/gsc/ está la extracción de 12 meses que ya se hizo, para que compares y valides
continuidad. En datos/ads/ están los dos informes de Google Ads. En referencia/ están los
dos PDF ya entregados y los archivos que los generaron.
---

## 4. Qué esperar

Claude Code va a escribir sus propios scripts en `scripts/`. No hace falta que los revises,
pero quedan ahí.

La extracción de 16 meses con 4 cortes por propiedad es bastante más grande que la anterior
(121.412 filas). Calculá varios minutos y un archivo histórico de unos 50–80 MB.

---

## Estructura de la carpeta

    CLAUDE.md          el brief maestro — Claude Code lo lee solo al arrancar
    README.md          este archivo
    datos/ads/         los dos informes de Google Ads (keywords y términos)
    datos/gsc/         la extracción de 12 meses ya hecha, como baseline
    referencia/        los dos PDF entregados + style.css + render.py
    scripts/           vacío, lo llena Claude Code

    client_secret.json  <- copiar acá desde la carpeta de arriba
    token.json          <- copiar acá desde la carpeta de arriba

## Antes de la primera corrida

Copiá `client_secret.json` y `token.json` desde `gsc-extraccion\` a esta carpeta.
Sin esos dos archivos no hay autenticación.

Si el token venció (pasan 7 días), Claude Code te va a pedir reautorizar: se abre el
navegador, elegís `tmisrahi@onepeterson.com`, y listo.
