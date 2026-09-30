/** Portada: presupuesto vs. gasto de Google Ads, frescura de los datos y estado del tablero por cliente. */
import { Link } from 'react-router-dom';
import { ESTADOS, MARCAS } from '@/constants/estados';
import { useExtracciones, useRecomendaciones } from '@/hooks/useDatos';
import { Cargando, Tarjeta } from '@/components/shared/Ui';
import VistaPresupuesto from '@/components/presupuesto/VistaPresupuesto';
import { diasDesde, fecha, fechaHora } from '@/utils/formato';

function Frescura({ titulo, hasta, corrida }: { titulo: string; hasta: string | null | undefined; corrida: string | null | undefined }) {
  const d = diasDesde(corrida);
  return (
    <div className="text-[13px]">
      <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">{titulo}</div>
      <div className="font-mono font-semibold text-mc-navy">{hasta ? `hasta ${fecha(hasta)}` : 'sin datos'}</div>
      <div className={`text-xs ${d !== null && d > 35 ? 'text-red-700' : 'text-mc-grey'}`}>{corrida ? `extraído ${fechaHora(corrida)}` : ''}</div>
    </div>
  );
}

export default function Inicio() {
  const recs = useRecomendaciones();
  const ext = useExtracciones();
  const gsc = ext.datos.search_console;
  const ads = ext.datos.google_ads;

  return (
    <div className="space-y-8 animate-fade-in">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-blue">MarComms · Inicio</div>
          <h1 className="text-xl">Presupuesto y gasto de Google Ads</h1>
        </div>
        <div className="flex gap-8">
          <Frescura titulo="Google Ads" hasta={ads?.hasta} corrida={ads?.corridaEn} />
          <Frescura titulo="Search Console" hasta={gsc?.hasta} corrida={gsc?.corridaEn} />
        </div>
      </header>

      <VistaPresupuesto />

      <section>
        <h2 className="mb-3 text-base">Tablero de recomendaciones por cliente</h2>
        <Tarjeta className="p-4">
          {recs.cargando ? (
            <Cargando />
          ) : (
            <table className="w-full text-[13px]">
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
          <div className="mt-3 flex gap-4 text-sm">
            <Link to="/sem" className="font-semibold text-mc-blue hover:underline">
              Ir al tablero SEM
            </Link>
            <Link to="/seo" className="font-semibold text-mc-blue hover:underline">
              Ir al tablero SEO
            </Link>
          </div>
        </Tarjeta>
      </section>
    </div>
  );
}
