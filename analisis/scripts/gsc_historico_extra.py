# -*- coding: utf-8 -*-
"""
gsc_historico_extra.py — cortes complementarios sobre la misma ventana (2025-04-01 → hoy):

  queries_agg   query + country          (sin date: sin anonimización diaria, comparable al baseline)
  device_total  device                   (reparto móvil/escritorio exacto por propiedad)
  device_date   date + device            (evolución del reparto por día)

Mismas carpetas, mismo log y mismos parámetros que gsc_historico.py.
"""
import sys
import gsc_historico as g

g.CORTES = [("queries_agg", ["query", "country"], False),
            ("device_total", ["device"], False),
            ("device_date", ["date", "device"], False)]

if __name__ == "__main__":
    g.main()
