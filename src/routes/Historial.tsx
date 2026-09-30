/** Historial: quién movió qué y cuándo, en toda la base. */
import { useEffect, useMemo, useState } from 'react';
import type { Estado } from '@/lib/database.types';
import { ESTADO_BY_ID } from '@/constants/estados';
import { listarEventos, type Evento } from '@/services/recomendaciones';
import { useRecomendaciones } from '@/hooks/useDatos';
import { Cargando, ChipMarca, ErrorBox, SeccionTitulo, Tarjeta, Vacio } from '@/components/shared/Ui';
import { fechaHora } from '@/utils/formato';

export default function Historial() {
  const recs = useRecomendaciones();
  const [eventos, setEventos] = useState<Evento[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let vivo = true;
    listarEventos(undefined, 300)
      .then((e) => vivo && setEventos(e))
      .catch((e: unknown) => vivo && setError(e instanceof Error ? e.message : String(e)));
    return () => {
      vivo = false;
    };
  }, [recs.datos]);

  const porId = useMemo(() => new Map(recs.datos.map((r) => [r.id, r])), [recs.datos]);

  if (error) return <ErrorBox mensaje={error} />;
  return (
    <div className="animate-fade-in">
      <SeccionTitulo meta="últimos 300 movimientos">Movimientos del tablero</SeccionTitulo>
      {!eventos ? (
        <Cargando />
      ) : eventos.length === 0 ? (
        <Vacio>Todavía nadie movió una tarjeta.</Vacio>
      ) : (
        <Tarjeta>
          <table className="w-full text-[13px]">
            <thead>
              <tr className="bg-noche-mc text-left text-[11px] uppercase tracking-[0.1em] text-white">
                <th className="px-4 py-2 font-semibold">Cuándo</th>
                <th className="px-2 py-2 font-semibold">Recomendación</th>
                <th className="px-2 py-2 font-semibold">Cambio</th>
                <th className="px-2 py-2 font-semibold">Quién</th>
              </tr>
            </thead>
            <tbody>
              {eventos.map((ev) => {
                const rec = porId.get(ev.recomendacionId);
                return (
                  <tr key={ev.id} className="border-t border-mc-tint2 align-top">
                    <td className="whitespace-nowrap px-4 py-2 font-mono text-mc-grey">{fechaHora(ev.creadoEn)}</td>
                    <td className="px-2 py-2">
                      {rec ? (
                        <span className="flex items-center gap-1.5">
                          <ChipMarca marca={rec.marca} />
                          <span className="text-mc-navy">{rec.titulo}</span>
                        </span>
                      ) : (
                        <span className="text-mc-grey">(recomendación eliminada)</span>
                      )}
                      {ev.motivo && <div className="mt-0.5 text-xs italic text-mc-grey">{ev.motivo}</div>}
                    </td>
                    <td className="whitespace-nowrap px-2 py-2">
                      {ev.deEstado ? ESTADO_BY_ID[ev.deEstado as Estado]?.label ?? ev.deEstado : '—'} → <b>{ESTADO_BY_ID[ev.aEstado as Estado]?.label ?? ev.aEstado}</b>
                    </td>
                    <td className="px-2 py-2 text-mc-grey">{ev.usuario ?? '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Tarjeta>
      )}
    </div>
  );
}
