/**
 * Fichas del detalle de una tarjeta, con la misma información que los informes PDF:
 *  - FichaAnuncio: qué dice hoy el anuncio, qué buscó la gente que lo activó, cómo lo buscan en orgánico,
 *    diagnóstico, qué quitar y los títulos/descripciones propuestos con su largo.
 *  - FichaPlan: pain point → mejora y, si tiene campaña, cómo buscan su tema en orgánico.
 * Los datos vienen en `evidencia` (los arma exportar_recomendaciones.py en el proyecto de análisis).
 */
import type { ReactNode } from 'react';
import { Info } from 'lucide-react';
import { ars, entero } from '@/utils/formato';

export interface TerminoFicha {
  termino: string;
  relacion: string;
  coste: number;
  clics?: number;
}
export interface OrganicoFicha {
  query: string;
  impr: number;
  pos: number;
}
export interface DatosAnuncio {
  ficha: 'anuncio';
  unidad?: string;
  cambio?: string;
  gasto_ars?: number;
  fuerza?: string[];
  url?: string;
  titulos_hoy?: string[];
  terminos?: TerminoFicha[];
  organico?: OrganicoFicha[];
  diagnostico?: string;
  titulos_propuestos?: string[];
  descripciones_propuestas?: string[];
  quitar?: string[];
  nota?: string | null;
  ventanas?: string;
  organico_hasta?: string;
  /** País desde el que se midieron las búsquedas orgánicas (el de la campaña). */
  organico_desde?: string | null;
}
export interface DatosPlan {
  ficha: 'plan';
  unidad?: string;
  estado_en_plan?: string;
  pain?: string;
  pain_txt?: string;
  mejora?: string;
  mejora_txt?: string;
  organico?: OrganicoFicha[];
  organico_hasta?: string;
  /** País desde el que se midieron las búsquedas orgánicas (el de la campaña). */
  organico_desde?: string | null;
}

function Rotulo({ children }: { children: ReactNode }) {
  return <h4 className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-mc-grey">{children}</h4>;
}

function Ayuda({ children }: { children: ReactNode }) {
  return (
    <div className="mt-2 flex gap-2 rounded-lg bg-sky-50 px-3 py-2 text-[11.5px] leading-relaxed text-mc-ink ring-1 ring-sky-100">
      <Info size={14} className="mt-0.5 shrink-0 text-mc-blue" />
      <div>{children}</div>
    </div>
  );
}

const RELACION: Record<string, { clase: string; texto: string }> = {
  fuerte: {
    clase: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    texto: 'fuerte',
  },
  parcial: {
    clase: 'bg-amber-50 text-amber-800 ring-amber-200',
    texto: 'parcial',
  },
  nula: { clase: 'bg-red-50 text-red-700 ring-red-200', texto: 'nula' },
  'sin anuncio': {
    clase: 'bg-mc-tint2 text-mc-grey ring-mc-hair',
    texto: 'sin anuncio',
  },
};

function ChipRelacion({ relacion }: { relacion: string }) {
  const r = RELACION[relacion] ?? {
    clase: 'bg-mc-tint2 text-mc-grey ring-mc-hair',
    texto: relacion,
  };
  return <span className={`inline-flex rounded-full px-2 py-0.5 text-[10.5px] font-semibold ring-1 ${r.clase}`}>{r.texto}</span>;
}

/** Posición en Google: 1–3 arriba de todo, 4–10 primera página, 11+ segunda página o más. */
function ChipPosicion({ pos }: { pos: number }) {
  const clase =
    pos <= 3.5
      ? 'bg-emerald-50 text-emerald-700 ring-emerald-200'
      : pos <= 10.5
        ? 'bg-sky-50 text-mc-blue2 ring-sky-200'
        : 'bg-mc-tint2 text-mc-grey ring-mc-hair';
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 font-mono text-[10.5px] font-semibold ring-1 ${clase}`}>
      pos. {pos.toLocaleString('es-AR', { maximumFractionDigits: 1 })}
    </span>
  );
}

function ListaConLargo({ items, limite }: { items: string[]; limite: number }) {
  return (
    <ul>
      {items.map((t) => (
        <li key={t} className="flex items-start justify-between gap-4 border-b border-mc-hair/70 py-2 text-[13.5px] text-mc-navy last:border-b-0">
          <span>{t}</span>
          <span className={`shrink-0 font-mono text-[11px] ${t.length > limite ? 'font-bold text-red-700' : 'text-mc-grey'}`}>
            {t.length}/{limite}
          </span>
        </li>
      ))}
    </ul>
  );
}

/** Búsquedas orgánicas del tema, con la explicación de impresiones y posición. */
function BloqueOrganico({ organico, desde, hasta }: { organico?: OrganicoFicha[]; desde?: string; hasta?: string }) {
  return (
    <section>
      <Rotulo>Cómo lo buscan en orgánico</Rotulo>
      {organico?.length ? (
        <ul className="divide-y divide-mc-tint2 text-[13px]">
          {organico.map((o) => (
            <li key={o.query} className="flex items-center gap-2 py-1.5">
              <span className="min-w-0 flex-1 truncate text-mc-navy" title={o.query}>
                {o.query}
              </span>
              <span className="w-24 text-right font-mono text-[12px] text-mc-ink">{entero(o.impr)} impr.</span>
              <ChipPosicion pos={o.pos} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-[13px] text-mc-grey">
          El sitio no apareció en Google para búsquedas de este tema hechas desde {desde ?? 'el país de la campaña'}. No es un error de carga: es un hueco de
          contenido.
        </p>
      )}
      <Ayuda>
        <b>Impresiones</b>: cuántas veces apareció el sitio en Google (resultados orgánicos, no pagos) para esa búsqueda, hecha desde{' '}
        {desde ?? 'el país de la campaña'}, en todo el histórico de Search Console hasta el {hasta ?? '—'}. <b>Posición</b>: lugar promedio en los resultados,
        ponderado por impresiones: <b className="text-emerald-700">1–3</b> arriba de todo, <b className="text-mc-blue2">4–10</b> primera página, <b>11 o más</b>{' '}
        segunda página en adelante.
      </Ayuda>
    </section>
  );
}

export function FichaAnuncio({ d }: { d: DatosAnuncio }) {
  const fuerza = d.fuerza?.length ? [...new Set(d.fuerza)].join(', ') : '—';
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 rounded-lg bg-mc-tint px-3 py-2 text-[13px] text-mc-ink">
        <b className="font-mono text-mc-navy">{ars(d.gasto_ars ?? 0)}</b> gasto en las dos ventanas ({d.ventanas ?? '—'})<span className="text-mc-hair">·</span>{' '}
        fuerza del anuncio según Google <b className="text-mc-navy">{fuerza}</b>
        <span className="text-mc-hair">·</span> {entero(d.titulos_hoy?.length ?? 0)} títulos hoy
        {d.cambio && <span className="ml-auto rounded bg-mc-navy px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em] text-white">{d.cambio}</span>}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* izquierda: situación actual */}
        <div className="space-y-4">
          <section>
            <Rotulo>Qué dice hoy</Rotulo>
            <p className="text-[13.5px] leading-relaxed text-mc-ink">{d.titulos_hoy?.length ? d.titulos_hoy.join(' | ') : '—'}</p>
            <Ayuda>
              Cada búsqueda que activó el anuncio se compara con estos títulos: <b className="text-emerald-700">fuerte</b> = todas las palabras de tema de la
              búsqueda aparecen en algún título; <b className="text-amber-800">parcial</b> = aparecen algunas, en títulos o descripciones;{' '}
              <b className="text-red-700">nula</b> = no aparece ninguna, el anuncio no responde a lo que se buscó; <b className="text-mc-grey">sin anuncio</b> =
              el grupo no tenía un anuncio activo cuando se hizo la búsqueda. Las palabras genéricas («certificación», «auditoría») no cuentan.
            </Ayuda>
          </section>

          <section>
            <Rotulo>Qué buscó la gente que lo activó</Rotulo>
            {d.terminos?.length ? (
              <ul className="divide-y divide-mc-tint2 text-[13px]">
                {d.terminos.map((t) => (
                  <li key={t.termino} className="flex items-center gap-2 py-1.5">
                    <span className="min-w-0 flex-1 truncate text-mc-navy" title={t.termino}>
                      {t.termino}
                    </span>
                    <ChipRelacion relacion={t.relacion} />
                    <span className="w-24 text-right font-mono text-[12px] text-mc-ink">{ars(t.coste)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-[13px] text-mc-grey">Sin términos con gasto en el período.</p>
            )}
            <p className="mt-1 text-[11px] text-mc-grey">Monto: lo que costó cada búsqueda en las dos ventanas.</p>
          </section>

          <BloqueOrganico organico={d.organico} desde={d.organico_desde ?? d.unidad} hasta={d.organico_hasta} />

          {d.diagnostico && (
            <section>
              <Rotulo>Diagnóstico</Rotulo>
              <p className="text-[14px] leading-relaxed text-mc-navy">{d.diagnostico}</p>
            </section>
          )}

          {d.quitar && d.quitar.length > 0 && (
            <section>
              <Rotulo>Quitar</Rotulo>
              <div className="flex flex-wrap gap-1.5">
                {d.quitar.map((q) => (
                  <span key={q} className="rounded-md bg-red-50 px-2 py-0.5 text-[12px] text-red-800 line-through decoration-red-300 ring-1 ring-red-100">
                    {q}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* derecha: propuesta */}
        <div className="space-y-4 rounded-card bg-mc-tint px-4 py-3">
          <section>
            <Rotulo>Títulos propuestos</Rotulo>
            <ListaConLargo items={d.titulos_propuestos ?? []} limite={30} />
          </section>
          <section>
            <Rotulo>Descripciones propuestas</Rotulo>
            <ListaConLargo items={d.descripciones_propuestas ?? []} limite={90} />
          </section>
          {d.nota && <p className="border-t border-mc-hair/70 pt-2 text-[12.5px] leading-relaxed text-mc-grey">{d.nota}</p>}
        </div>
      </div>
    </div>
  );
}

export function FichaPlan({ d, conCampana }: { d: DatosPlan; conCampana: boolean }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-card border border-l-4 border-mc-hair/70 border-l-mc-red bg-white px-4 py-3">
          <Rotulo>Pain point</Rotulo>
          <p className="text-[14px] font-semibold text-mc-navy">{d.pain}</p>
          <p className="mt-1 text-[13px] leading-relaxed text-mc-ink">{d.pain_txt}</p>
        </div>
        <div className="rounded-card border border-l-4 border-mc-hair/70 border-l-mc-green bg-white px-4 py-3">
          <Rotulo>Mejora</Rotulo>
          <p className="text-[14px] font-semibold text-mc-navy">{d.mejora}</p>
          <p className="mt-1 text-[13px] leading-relaxed text-mc-ink">{d.mejora_txt}</p>
        </div>
      </div>
      {conCampana && <BloqueOrganico organico={d.organico} desde={d.organico_desde ?? d.unidad} hasta={d.organico_hasta} />}
    </div>
  );
}
