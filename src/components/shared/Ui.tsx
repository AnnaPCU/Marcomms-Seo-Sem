/** Piezas chicas de interfaz reutilizadas en todas las vistas. */
import type { ReactNode } from 'react';
import type { Marca, Prioridad } from '@/lib/database.types';
import { MARCA_BY_ID, PRIORIDAD_BY_ID } from '@/constants/estados';

export function Chip({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-semibold leading-4 ${className}`}>{children}</span>;
}

/** Marca del cliente. Siempre en la paleta MarComms: nunca se usan los colores de Control Union ni de Peterson. */
export function ChipMarca({ marca }: { marca: Marca }) {
  return (
    <Chip className="bg-mc-navy text-white" >
      {MARCA_BY_ID[marca]?.corto ?? marca}
    </Chip>
  );
}

export function ChipPrioridad({ prioridad }: { prioridad: Prioridad }) {
  const p = PRIORIDAD_BY_ID[prioridad];
  return <Chip className={p?.clase ?? ''}>{p?.label ?? prioridad}</Chip>;
}

export function Cargando({ texto = 'Cargando…' }: { texto?: string }) {
  return <div className="py-10 text-center text-sm text-mc-grey">{texto}</div>;
}

export function ErrorBox({ mensaje }: { mensaje: string }) {
  return <div className="rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{mensaje}</div>;
}

export function Vacio({ children }: { children: ReactNode }) {
  return <div className="rounded-card border border-dashed border-mc-hair px-4 py-8 text-center text-sm text-mc-grey">{children}</div>;
}

export function Tarjeta({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-card border border-mc-hair bg-white shadow-card ${className}`}>{children}</div>;
}

export function Kpi({ valor, etiqueta, nota }: { valor: ReactNode; etiqueta: string; nota?: string }) {
  return (
    <Tarjeta className="px-4 py-3">
      <div className="font-mono text-2xl font-semibold text-mc-navy">{valor}</div>
      <div className="mt-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">{etiqueta}</div>
      {nota && <div className="mt-1 text-xs text-mc-grey">{nota}</div>}
    </Tarjeta>
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
      ? 'bg-mc-blue text-white hover:bg-mc-blue2'
      : tipo === 'peligro'
        ? 'border border-red-200 bg-white text-red-700 hover:bg-red-50'
        : 'border border-mc-hair bg-white text-mc-navy hover:bg-mc-tint';
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${estilo}`}>
      {children}
    </button>
  );
}

export function Select({
  valor,
  onChange,
  opciones,
  todo,
  ariaLabel,
}: {
  valor: string;
  onChange: (v: string) => void;
  opciones: { id: string; label: string }[];
  todo: string;
  ariaLabel: string;
}) {
  return (
    <select
      aria-label={ariaLabel}
      value={valor}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-mc-hair bg-white px-2.5 py-1.5 text-sm text-mc-navy focus:border-mc-blue focus:outline-none"
    >
      <option value="">{todo}</option>
      {opciones.map((o) => (
        <option key={o.id} value={o.id}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
