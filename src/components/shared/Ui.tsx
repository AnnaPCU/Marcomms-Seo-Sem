/** Piezas chicas de interfaz reutilizadas en todas las vistas (estilo MarComms Reports). */
import type { ReactNode } from 'react';
import type { Marca, Prioridad } from '@/lib/database.types';
import { MARCA_BY_ID, PRIORIDAD_BY_ID } from '@/constants/estados';

export { Cargando } from './Loader';

export function Chip({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-semibold leading-4 ${className}`}>{children}</span>;
}

/** Marca del cliente. Siempre en la paleta MarComms: nunca se usan los colores de Control Union ni de Peterson. */
export function ChipMarca({ marca }: { marca: Marca }) {
  return <Chip className="bg-mc-navy text-white">{MARCA_BY_ID[marca]?.corto ?? marca}</Chip>;
}

export function ChipPrioridad({ prioridad }: { prioridad: Prioridad }) {
  const p = PRIORIDAD_BY_ID[prioridad];
  return (
    <Chip className={p?.clase ?? ''}>
      <span className={`mr-1 inline-block h-1.5 w-1.5 rounded-full ${p?.punto ?? ''}`} />
      {p?.label ?? prioridad}
    </Chip>
  );
}

/** Píldora de estado (verde, rojo, gris, azul), como las de los indicadores de Reports. */
export function Pildora({ children, tono = 'gris' }: { children: ReactNode; tono?: 'verde' | 'rojo' | 'gris' | 'azul' | 'dorado' | 'claro' }) {
  const t = {
    verde: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    rojo: 'bg-red-50 text-red-700 ring-red-200',
    gris: 'bg-mc-tint2 text-mc-ink ring-mc-hair',
    azul: 'bg-sky-50 text-mc-blue2 ring-sky-200',
    dorado: 'bg-amber-50 text-amber-800 ring-amber-200',
    claro: 'bg-white/15 text-white ring-white/25',
  }[tono];
  return <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ${t}`}>{children}</span>;
}

export function ErrorBox({ mensaje }: { mensaje: string }) {
  return <div className="rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{mensaje}</div>;
}

export function Vacio({ children }: { children: ReactNode }) {
  return <div className="rounded-card border border-dashed border-mc-hair bg-white px-4 py-8 text-center text-sm text-mc-grey">{children}</div>;
}

export function Tarjeta({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-card border border-mc-hair/70 bg-white shadow-card ${className}`}>{children}</div>;
}

/** Título de sección: texto azul en mayúsculas, línea hasta el borde y un dato a la derecha. */
export function SeccionTitulo({ children, meta }: { children: ReactNode; meta?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center gap-3">
      <span className="text-[11px] font-bold uppercase tracking-[0.16em] text-mc-blue">{children}</span>
      <span className="h-px flex-1 bg-mc-hair" />
      {meta && <span className="text-[11px] italic text-mc-grey">{meta}</span>}
    </div>
  );
}

/** Introducción de una vista: callout blanco con borde azul a la izquierda y cifras al costado. */
export function Intro({ children, cifras }: { children: ReactNode; cifras?: { valor: ReactNode; etiqueta: string; tono?: string }[] }) {
  return (
    <div className="mb-5 flex flex-wrap items-center gap-4 rounded-card border border-l-4 border-mc-hair/70 border-l-mc-blue bg-white px-4 py-3 shadow-card">
      <p className="min-w-[240px] flex-1 text-[13px] leading-relaxed text-mc-ink">{children}</p>
      {cifras && (
        <div className="flex gap-5">
          {cifras.map((c) => (
            <div key={c.etiqueta} className="text-center">
              <div className={`font-mono text-lg font-semibold ${c.tono ?? 'text-mc-navy'}`}>{c.valor}</div>
              <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-mc-grey">{c.etiqueta}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/** Panel con franja azul noche arriba (bloques de acción, como «Próximos pasos» en Reports). */
export function PanelOscuro({ titulo, icono, meta, children }: { titulo: ReactNode; icono?: ReactNode; meta?: ReactNode; children: ReactNode }) {
  return (
    <div className="overflow-hidden rounded-card border border-mc-hair/70 bg-white shadow-card">
      <div className="flex items-center gap-2 bg-noche-mc px-4 py-2.5 text-white">
        {icono}
        <span className="text-[12px] font-bold uppercase tracking-[0.12em]">{titulo}</span>
        {meta && <span className="ml-auto text-[11px] text-white/60">{meta}</span>}
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

export type Acento = 'azul' | 'verde' | 'dorado' | 'rojo' | 'gris' | 'noche';
const ACENTO: Record<Exclude<Acento, 'noche'>, string> = {
  azul: 'border-l-mc-blue',
  verde: 'border-l-mc-green',
  dorado: 'border-l-mc-gold',
  rojo: 'border-l-mc-red',
  gris: 'border-l-mc-grey',
};

/** Indicador clave: borde de color a la izquierda, o relleno azul noche para el destacado. */
export function Kpi({ valor, etiqueta, nota, acento = 'azul', pildora }: { valor: ReactNode; etiqueta: string; nota?: ReactNode; acento?: Acento; pildora?: ReactNode }) {
  const noche = acento === 'noche';
  return (
    <div
      className={`rounded-card px-4 py-3.5 shadow-card transition hover:-translate-y-0.5 hover:shadow-elevada ${
        noche ? 'bg-noche-mc text-white' : `border border-l-[3px] border-mc-hair/70 bg-white ${ACENTO[acento]}`
      }`}
    >
      <div className={`text-[10px] font-bold uppercase tracking-[0.14em] ${noche ? 'text-white/70' : 'text-mc-grey'}`}>{etiqueta}</div>
      <div className={`mt-1 font-mono text-[22px] font-semibold leading-tight ${noche ? 'text-white' : 'text-mc-navy'}`}>{valor}</div>
      {pildora && <div className="mt-1.5">{pildora}</div>}
      {nota && <div className={`mt-1.5 text-xs ${noche ? 'text-white/70' : 'text-mc-grey'}`}>{nota}</div>}
    </div>
  );
}

export function Boton({
  children,
  onClick,
  tipo = 'secundario',
  disabled,
  type = 'button',
}: {
  children: ReactNode;
  onClick?: () => void;
  tipo?: 'primario' | 'secundario' | 'peligro';
  disabled?: boolean;
  type?: 'button' | 'submit';
}) {
  const base = 'inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50';
  const estilo =
    tipo === 'primario'
      ? 'bg-mc-blue text-white shadow-sm hover:bg-mc-blue2'
      : tipo === 'peligro'
        ? 'border border-red-200 bg-white text-red-700 hover:bg-red-50'
        : 'border border-mc-hair bg-white text-mc-navy hover:bg-mc-tint';
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${estilo}`}>
      {children}
    </button>
  );
}

/** Selector con etiqueta chica arriba, como los filtros de la barra de Reports. */
export function Select({
  valor,
  onChange,
  opciones,
  todo,
  ariaLabel,
  etiqueta,
}: {
  valor: string;
  onChange: (v: string) => void;
  opciones: { id: string; label: string }[];
  todo: string;
  ariaLabel: string;
  etiqueta?: string;
}) {
  const select = (
    <select
      aria-label={ariaLabel}
      value={valor}
      onChange={(e) => onChange(e.target.value)}
      className={`rounded-lg border bg-white px-2.5 py-1.5 text-sm text-mc-navy transition focus:border-mc-blue focus:outline-none focus:ring-2 focus:ring-mc-blue/15 ${
        valor ? 'border-mc-blue/60 font-semibold' : 'border-mc-hair'
      }`}
    >
      <option value="">{todo}</option>
      {opciones.map((o) => (
        <option key={o.id} value={o.id}>
          {o.label}
        </option>
      ))}
    </select>
  );
  if (!etiqueta) return select;
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">{etiqueta}</span>
      {select}
    </label>
  );
}
