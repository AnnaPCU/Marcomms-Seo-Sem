# -*- coding: utf-8 -*-
"""
meta_mcp_headers.py — encabezado de autorización para el servidor MCP oficial de Meta (https://mcp.facebook.com/ads).

Lo ejecuta Claude Code al conectarse (headersHelper en .mcp.json): imprime {"Authorization": "Bearer <token>"} con el
token de usuario del sistema guardado en analisis/meta-ads.json. Así el token no queda copiado en la configuración y,
si se regenera, alcanza con cambiarlo en meta-ads.json.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token = os.environ.get("META_ACCESS_TOKEN") or json.load(open(os.path.join(ROOT, "meta-ads.json"), encoding="utf-8"))["access_token"]
print(json.dumps({"Authorization": f"Bearer {token}"}))
