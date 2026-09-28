# Decisiones

Registro corto de por qué las cosas son como son. Se agrega arriba.

## 2026-09-28 — Arranque

- **Identidad MarComms, no la de los clientes.** El tablero es de la agencia interna. Control Union y
  Peterson aparecen como chips de texto en la paleta MarComms; nunca con sus colores ni logos, porque el
  manual del grupo no admite piezas que mezclen las dos marcas.
- **Proyecto nuevo de Supabase** («Marcomms SEO-SEM»), separado de MarComms Hub. Se borra «MarComms Hub
  Reports», que estaba inactivo y sin uso, para liberar el cupo del plan gratuito.
- **Login con Google restringido por dominio en la base**, con enlace por correo como alternativa. El
  trigger sobre `auth.users` es la única barrera real; lo del cliente es cortesía.
- **Clave estable por recomendación** (`marca:tipo:campaña|sitio:slug`). Es lo que permite renovar cada mes
  sin duplicar tarjetas ni pisar el estado que alguien ya movió.
- **Las recomendaciones no se escriben en la web.** Salen de los informes del proyecto de análisis y se
  cargan por script. La web es para decidir y seguir, no para redactar.
- **Métricas por mes calendario**, del 1 al último día con datos. Felipe pidió que la vista mensual sea el mes
  real y no una ventana móvil; el gasto por día sale de dividir por los días con datos.
- **RLS abierto para autenticados.** Equipo de pocas personas, todas del grupo; no hay roles por ahora.
- **Una rama, sin staging.** `npm run verificar` antes de cada push reemplaza al entorno de prueba.
