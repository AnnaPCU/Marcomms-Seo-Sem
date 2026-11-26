# -*- coding: utf-8 -*-
"""
ads_auth.py — autorización de Google Ads, Search Console y/o Google Analytics 4 (solo lectura en GSC y GA4).

Uso:
  python ads_auth.py --ads CUENTA     Google Ads  -> refresh token en google-ads.yaml
  python ads_auth.py --gsc CUENTA     Search Console -> token.json (por defecto tmisrahi@onepeterson.com)
  python ads_auth.py --ga4 CUENTA     Google Analytics 4 -> token_ga4.json (por defecto tmisrahi@onepeterson.com)
  python ads_auth.py                  las dos con tmisrahi@onepeterson.com (solo si esa cuenta tiene acceso a Ads)
Cada permiso se guarda solo si la cuenta que autorizó es la pedida.

Abre el navegador una sola vez (elegir tmisrahi@onepeterson.com). Usa el mismo client_secret.json
que Search Console. No imprime ninguna credencial.

Para que el token no venza a los 7 días, la pantalla de consentimiento del proyecto de Google Cloud tiene
que estar en «Interno» (usuarios de onepeterson.com). En «Externo / Prueba» Google lo vence cada 7 días.

Requisito previo: en Google Cloud, la Google Ads API habilitada y el scope
https://www.googleapis.com/auth/adwords agregado a la pantalla de consentimiento.
Para GA4: Google Analytics Data API y Admin API habilitadas, scope analytics.readonly agregado.
"""
import base64, json, os, re, sys
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(ROOT, "google-ads.yaml")
SEC = os.path.join(ROOT, "client_secret.json")
# openid + email: solo para comprobar con qué cuenta se autorizó antes de guardar nada
ID = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
ADS, GSC = "https://www.googleapis.com/auth/adwords", "https://www.googleapis.com/auth/webmasters.readonly"
GA4 = "https://www.googleapis.com/auth/analytics.readonly"
TOKEN_GSC = os.path.join(ROOT, "token.json")
TOKEN_GA4 = os.path.join(ROOT, "token_ga4.json")
args = sys.argv[1:]
if "--ads" in args:
    CUENTA, SCOPES, DESTINO = args[args.index("--ads") + 1], [ADS] + ID, "ads"
elif "--gsc" in args:
    CUENTA, SCOPES, DESTINO = (args[args.index("--gsc") + 1] if len(args) > args.index("--gsc") + 1 else "tmisrahi@onepeterson.com"), [GSC] + ID, "gsc"
elif "--ga4" in args:
    CUENTA, SCOPES, DESTINO = (args[args.index("--ga4") + 1] if len(args) > args.index("--ga4") + 1 else "tmisrahi@onepeterson.com"), [GA4] + ID, "ga4"
else:
    CUENTA, SCOPES, DESTINO = "tmisrahi@onepeterson.com", [ADS, GSC] + ID, "ambos"

if not os.path.exists(YAML) or not os.path.exists(SEC):
    sys.exit("Faltan google-ads.yaml o client_secret.json en la carpeta del proyecto.")
texto = open(YAML, encoding="utf-8").read()
if "PEGAR_AQUI" in texto:
    sys.exit("Primero pegá el developer token en google-ads.yaml (línea developer_token).")

print("=" * 66 + f"\n  Se abre el navegador. ELEGÍ LA CUENTA: {CUENTA}\n" + "=" * 66)
flow = InstalledAppFlow.from_client_secrets_file(SEC, SCOPES)
# sin abrir el navegador solo: el navegador predeterminado puede tener otra cuenta (p. ej. Gmail) y responder primero
dominio = CUENTA.split("@")[1]
extra = {} if dominio == "gmail.com" else {"hd": dominio}  # «hd» solo sirve para dominios de Workspace
creds = flow.run_local_server(port=0, open_browser=False, prompt="select_account consent", login_hint=CUENTA,
                              access_type="offline", timeout_seconds=1800, **extra)
if creds is None:
    sys.exit("Se venció el tiempo de espera sin autorización. Volvé a correr el script.")
pago = creds.id_token.split(".")[1] if creds.id_token else ""
email = json.loads(base64.urlsafe_b64decode(pago + "=" * (-len(pago) % 4))).get("email", "") if pago else ""
if email.lower() != CUENTA.lower():
    sys.exit(f"Se autorizó con {email or 'una cuenta desconocida'} y no con {CUENTA}. No se guardó nada: volvé a correr y elegí {CUENTA}.")
if not creds.refresh_token:
    sys.exit("Google no devolvió refresh token. Revocá el acceso de la app en la cuenta y volvé a correr.")
if DESTINO in ("ads", "ambos"):
    texto = re.sub(r'refresh_token: ".*"', f'refresh_token: "{creds.refresh_token}"', texto)
    open(YAML, "w", encoding="utf-8").write(texto)
    print(f"Google Ads: refresh token de {email} guardado en google-ads.yaml. Probá con:  python scripts/ads_export.py --test")
if DESTINO in ("gsc", "ambos"):
    open(TOKEN_GSC, "w", encoding="utf-8").write(creds.to_json())
    print(f"Search Console: token de {email} guardado en token.json.")
if DESTINO == "ga4":
    open(TOKEN_GA4, "w", encoding="utf-8").write(creds.to_json())
    print(f"Google Analytics 4: token de {email} guardado en token_ga4.json.")
