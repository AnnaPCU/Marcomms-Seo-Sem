# Decisiones

Registro corto de por qué las cosas son como son. Se agrega arriba.

## 2026-09-28 / 29 — Arranque

- **Identidad MarComms, no la de los clientes.** El tablero es de la agencia interna. Control Union y
  Peterson aparecen como chips de texto en la paleta MarComms; nunca con sus colores ni logos, porque el
  manual del grupo no admite piezas que mezclen las dos marcas.
- **Esquema `seo_sem` dentro del proyecto MarComms Hub, no proyecto propio.** Se quería un proyecto nuevo,
  pero el plan gratuito de Supabase permite 2 proyectos activos por usuario sumando todas sus organizaciones
  y la cuenta ya los tenía (uno en marcomms-hub y otro en otra organización). Un esquema aparte da el mismo
  aislamiento de datos y RLS, comparte el login y no cuesta nada. Regla: nunca tocar `public` ni `auth.users`.
- **Restricción de dominio en las políticas RLS**, no con un trigger sobre `auth.users`, para no afectar al
  Hub. Una cuenta ajena puede iniciar sesión pero no lee ni escribe nada de `seo_sem`.
- **Contraseña compartida en vez de login por correo.** Felipe no quiere que cada persona entre con su mail:
  una sola cuenta interna de Auth y una contraseña de equipo. El nombre que escribe cada uno al entrar se guarda
  en el navegador y es lo que se registra en el historial de movimientos. Costo: si alguien filtra la
  contraseña, se cambia desde el dashboard de Supabase y listo.
- **Carga de datos por SQL generado** (`publicar.py --sql`) en lugar de la API con service role key: no
  requiere secretos en ninguna máquina y el archivo queda versionado en `supabase/seed/`.
- **Clave estable por recomendación** (`marca:tipo:campaña|sitio:slug`). Es lo que permite renovar cada mes
  sin duplicar tarjetas ni pisar el estado que alguien ya movió.
- **Las recomendaciones no se escriben en la web.** Salen de los informes del proyecto de análisis y se
  cargan por script. La web es para decidir y seguir, no para redactar.
- **Métricas por mes calendario**, del 1 al último día con datos. Felipe pidió que la vista mensual sea el mes
  real y no una ventana móvil; el gasto por día sale de dividir por los días con datos.
- **RLS abierto para autenticados.** Equipo de pocas personas, todas del grupo; no hay roles por ahora.
- **Una rama, sin staging.** `npm run verificar` antes de cada push reemplaza al entorno de prueba.
