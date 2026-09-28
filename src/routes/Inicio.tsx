/** Portada: frescura de los datos, estado del tablero por cliente y gasto del último mes por campaña. */
import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { ESTADOS, MARCAS } from '@/constants/estados';
import { useCatalogo, useExtracciones, useMetricas, useRecomendaciones } from '@/hooks/useDatos';
import { Cargando, ErrorBox, Kpi, Tarjeta, Vacio } from '@/components/shared/Ui';
import { ars, campanaCorta, diasDesde, entero, fecha, fechaHora, mesCorto, pct } from '@/utils/formato';

export default function Inicio() {
  const recs = useRecomendaciones();
  const ext = useExtracciones();
  const met = useMetricas();
  const cat = useCatalogo();

  const gsc = ext.datos.search_console;
  const ads = ext.datos.google_ads;
  const diasGsc = diasDesde(gsc?.corridaEn);
  const diasAds = diasDesde(ads?.corridaEn);

  const ultimoMes = met.datos[0]?.mes ?? null;
  const gastoMes = useMemo(() => {
    if (!ultimoMes) return [];
    const filas = met.datos.filter((m) => m.mes === ultimoMes);
    const total = filas.reduce((s, m) => s + m.coste, 0);
    return filas
      .map((m) => ({ ...m, campana: cat.campana(m.campanaId), total }))
      .sort((a, b) => b.coste - a.coste);
  }, [met.datos, ultimoMes, cat]);
  const totalMes = gastoMes[0]?.total ?? 0;
  const porMarca = useMemo(() => {
    const acc = new Map<string, number>();
    for (const g of gastoMes) acc.set(g.campana?.marca ?? '?', (acc.get(g.campana?.marca ?? '?') ?? 0) + g.coste);
    return acc;
  }, [gastoMes]);

  if (recs.error) return <ErrorBox mensaje={recs.error} />;

  return (
    <div className="space-y-6 animate-fade-in">
      <header>
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-blue">MarComms · Inicio</div>
        <h1 className="text-xl">Qué está pendiente y qué tan frescos son los datos</h1>
      </header>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Kpi
          valor={gsc ? fecha(gsc.hasta) : '—'}
          etiqueta="Search Console · datos hasta"
          nota={gsc ? `Extraído ${fechaHora(gsc.corridaEn)}${diasGsc !== null && diasGsc > 35 ? ' · hace más de un mes' : ''}` : 'Sin extracciones cargadas'}
        />
        <Kpi
          valor={ads ? fecha(ads.hasta) : '—'}
          etiqueta="Google Ads · datos hasta"
          nota={ads ? `Extraído ${fechaHora(ads.corridaEn)}${diasAds !== null && diasAds > 35 ? ' · hace más de un mes' : ''}` : 'Sin extracciones cargadas'}
        />
        <Kpi valor={entero(recs.datos.filter((r) => r.estado === 'propuesta').length)} etiqueta="Propuestas sin tomar" nota={`${entero(recs.datos.filter((r) => r.estado === 'en_proceso').length)} en proceso`} />
        <Kpi
          valor={entero(recs.datos.filter((r) => r.estado === 'hecha').length)}
          etiqueta="Hechas"
          nota={`${entero(recs.datos.filter((r) => r.verificadaApi).length)} verificadas por API · ${entero(recs.datos.filter((r) => r.estado === 'descartada').length)} descartadas`}
        />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Tarjeta className="p-4">
          <h2 className="text-sm">Tablero por cliente</h2>
          {recs.cargando ? (
            <Cargando />
          ) : (
            <table className="mt-2 w-full text-[13px]">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-[0.1em] text-mc-grey">
                  <th className="py-1 font-semibold">Cliente</th>
                  {ESTADOS.map((e) => (
                    <th key={e.id} className="py-1 text-right font-semibold">
                      {e.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MARCAS.map((m) => (
                  <tr key={m.id} className="border-t border-mc-tint2">
                    <td className="py-1.5 text-mc-navy">
                      <Link to={`/sem?marca=${m.id}`} className="hover:text-mc-blue">
                        {m.label}
                      </Link>
                    </td>
                    {ESTADOS.map((e) => (
                      <td key={e.id} className="py-1.5 text-right font-mono">
                        {recs.datos.filter((r) => r.marca === m.id && r.estado === e.id).length}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="mt-3 flex gap-3 text-sm">
            <Link to="/sem" className="font-semibold text-mc-blue hover:underline">
              Ir al tablero SEM
            </Link>
            <Link to="/seo" className="font-semibold text-mc-blue hover:underline">
              Ir al tablero SEO
            </Link>
          </div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <div className="flex items-baseline justify-between">
            <h2 className="text-sm">Gasto por campaña</h2>
            <span className="text-xs text-mc-grey">{ultimoMes ? `ventana de 31 días cerrada en ${mesCorto(ultimoMes)}` : ''}</span>
          </div>
          {met.cargando || cat.cargando ? (
            <Cargando />
          ) : gastoMes.length === 0 ? (
            <Vacio>Todavía no hay métricas cargadas. Corré scripts/publicar.py después de una extracción.</Vacio>
          ) : (
            <>
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[13px]">
                <span className="font-mono font-semibold text-mc-navy">{ars(totalMes)}</span>
                {MARCAS.map((m) => (
                  <span key={m.id} className="text-mc-grey">
                    {m.corto} <span className="font-mono text-mc-navy">{ars(porMarca.get(m.id) ?? 0)}</span>
                  </span>
                ))}
              </div>
              <ul className="mt-3 max-h-80 space-y-1.5 overflow-y-auto pr-1">
                {gastoMes.map((g) => (
                  <li key={g.campanaId} className="text-[13px]">
                    <div className="flex justify-between gap-2">
                      <span className="truncate text-mc-navy">{g.campana ? campanaCorta(g.campana.nombre) : g.campanaId}</span>
                      <span className="shrink-0 font-mono">{ars(g.coste)}</span>
                      <span className="w-10 shrink-0 text-right font-mono text-mc-grey">{pct(g.coste, totalMes)}</span>
                    </div>
                    <div className="mt-0.5 h-1 rounded bg-mc-tint2">
                      <div className="h-1 rounded bg-mc-blue" style={{ width: `${(g.coste / totalMes) * 100}%` }} />
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Tarjeta>
      </section>
    </div>
  );
}
