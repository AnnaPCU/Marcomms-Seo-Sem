/** Panel lateral con el detalle de una recomendación: qué hacer, la evidencia y su historial. */
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import type { Estado } from '@/lib/database.types';
import { ESTADOS, ESTADO_BY_ID, MARCA_BY_ID } from '@/constants/estados';
import { listarEventos, type Evento, type Recomendacion } from '@/services/recomendaciones';
import { Boton, ChipMarca, ChipPrioridad } from '@/components/shared/Ui';
import { campanaCorta, fechaHora, mesCorto } from '@/utils/formato';
import type { Contexto } from './TarjetaRec';
import { FichaAnuncio, FichaPlan, type DatosAnuncio, type DatosPlan } from './Fichas';

function valorEvidencia(v: unknown): string {
  if (typeof v === 'number') return v.toLocaleString('es-AR');
  if (typeof v === 'string') return v;
  if (v === null || v === undefined) return '—';
  return JSON.stringify(v);
}

export default function DetalleRec({ rec, ctx, onCerrar, onMover }: { rec: Recomendacion; ctx: Contexto; onCerrar: () => void; onMover: (a: Estado) => void }) {
  const [eventos, setEventos] = useState<Evento[]>([]);
  useEffect(() => {
    let vivo = true;
    listarEventos(rec.id, 50).then((e) => vivo && setEventos(e)).catch(() => undefined);
    return () => {
      vivo = false;
    };
  }, [rec.id, rec.estado]);

  useEffect(() => {
    const esc = (e: KeyboardEvent) => e.key === 'Escape' && onCerrar();
    window.addEventListener('keydown', esc);
    return () => window.removeEventListener('keydown', esc);
  }, [onCerrar]);

  const ficha = rec.evidencia.ficha;
  // la ficha ya muestra todo; la tabla genérica queda para las tarjetas sin ficha (SEO)
  const evidencia = ficha ? [] : Object.entries(rec.evidencia);
  return createPortal(
    <div className="fixed inset-0 z-40 flex justify-end bg-mc-navy/30" onClick={onCerrar}>
      <aside className={`h-full w-full overflow-y-auto bg-white shadow-elevada animate-fade-in ${ficha === 'anuncio' ? 'max-w-5xl' : ficha === 'plan' ? 'max-w-3xl' : 'max-w-lg'}`} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="sticky top-0 flex items-start justify-between gap-3 border-b border-mc-hair bg-white px-5 py-4">
          <div>
            <div className="mb-1.5 flex items-center gap-1.5">
              <ChipMarca marca={rec.marca} />
              <ChipPrioridad prioridad={rec.prioridad} />
              <span className="text-[11px] text-mc-grey">{rec.tipo}</span>
            </div>
            <h2 className="text-base leading-snug">{rec.titulo}</h2>
          </div>
          <button type="button" onClick={onCerrar} aria-label="Cerrar" className="rounded-md p-1 text-mc-grey hover:bg-mc-tint hover:text-mc-navy">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-5 px-5 py-4 text-sm">
          <dl className="grid grid-cols-[110px_1fr] gap-x-3 gap-y-1 text-[13px] md:grid-cols-[110px_1fr_110px_1fr]">
            <dt className="text-mc-grey">Cliente</dt>
            <dd className="text-mc-navy">{MARCA_BY_ID[rec.marca]?.label ?? rec.marca}</dd>
            {rec.tipo === 'SEM' ? (
              <>
                <dt className="text-mc-grey">Campaña</dt>
                <dd className="text-mc-navy">{ctx.campana ? campanaCorta(ctx.campana) : '—'}</dd>
                <dt className="text-mc-grey">Grupo</dt>
                <dd className="text-mc-navy">{ctx.grupo ?? 'toda la campaña'}</dd>
              </>
            ) : (
              <>
                <dt className="text-mc-grey">Sitio</dt>
                <dd className="text-mc-navy">{rec.sitio ?? '—'}</dd>
                <dt className="text-mc-grey">Página</dt>
                <dd className="break-all text-mc-navy">{rec.pagina ?? '—'}</dd>
              </>
            )}
            <dt className="text-mc-grey">Estado</dt>
            <dd className="text-mc-navy">{ESTADO_BY_ID[rec.estado]?.label}</dd>
            <dt className="text-mc-grey">Propuesta en</dt>
            <dd className="text-mc-navy">{mesCorto(rec.mesAlta)}{rec.origen ? ` · ${rec.origen}` : ''}</dd>
            {rec.mesCierre && (
              <>
                <dt className="text-mc-grey">Cerrada en</dt>
                <dd className="text-mc-navy">{mesCorto(rec.mesCierre)}</dd>
              </>
            )}
            {rec.verificadaApi && (
              <>
                <dt className="text-mc-grey">Verificada</dt>
                <dd className="text-mc-blue">Confirmada por API el {fechaHora(rec.verificadaEn)}</dd>
              </>
            )}
          </dl>

          {ficha === 'anuncio' ? (
            <FichaAnuncio d={rec.evidencia as unknown as DatosAnuncio} />
          ) : ficha === 'plan' ? (
            <FichaPlan d={rec.evidencia as unknown as DatosPlan} />
          ) : (
            <section>
              <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Qué hacer</h3>
              <p className="whitespace-pre-line leading-relaxed">{rec.detalle}</p>
            </section>
          )}

          {evidencia.length > 0 && (
            <section>
              <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Evidencia</h3>
              <table className="w-full text-[13px]">
                <tbody>
                  {evidencia.map(([k, v]) => (
                    <tr key={k} className="border-t border-mc-tint2">
                      <td className="py-1 pr-3 text-mc-grey">{k.replaceAll('_', ' ')}</td>
                      <td className="py-1 text-right font-mono text-mc-navy">{valorEvidencia(v)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {rec.motivoDescarte && (
            <section>
              <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Motivo del descarte</h3>
              <p className="italic">{rec.motivoDescarte}</p>
            </section>
          )}

          <section>
            <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Mover a</h3>
            <div className="flex flex-wrap gap-2">
              {ESTADOS.filter((e) => e.id !== rec.estado).map((e) => (
                <Boton key={e.id} tipo={e.id === 'descartada' ? 'peligro' : e.id === 'hecha' ? 'primario' : 'secundario'} onClick={() => onMover(e.id)}>
                  {e.label}
                </Boton>
              ))}
            </div>
          </section>

          <section>
            <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Historial</h3>
            {eventos.length === 0 ? (
              <p className="text-mc-grey">Sin movimientos todavía.</p>
            ) : (
              <ul className="space-y-1 text-[13px]">
                {eventos.map((ev) => (
                  <li key={ev.id} className="flex flex-wrap gap-x-2 border-t border-mc-tint2 py-1">
                    <span className="font-mono text-mc-grey">{fechaHora(ev.creadoEn)}</span>
                    <span>
                      {ev.deEstado ? ESTADO_BY_ID[ev.deEstado as Estado]?.label ?? ev.deEstado : '—'} → {ESTADO_BY_ID[ev.aEstado as Estado]?.label ?? ev.aEstado}
                    </span>
                    {ev.usuario && <span className="text-mc-grey">{ev.usuario}</span>}
                    {ev.motivo && <span className="w-full italic text-mc-grey">{ev.motivo}</span>}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </aside>
    </div>,
    document.body,
  );
}
