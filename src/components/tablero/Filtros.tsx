/** Barra de filtros del tablero. Los valores viven en la URL para poder compartir una vista. */
import type { ReactNode } from 'react';
import { useEffect } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { guardar, leerGuardado } from '@/hooks/usePersistente';
import { ACCIONES, MARCA_BY_ID, MARCAS, PRIORIDAD_BY_ID, PRIORIDADES, accionesDe } from '@/constants/estados';
import { Select } from '@/components/shared/Ui';
import type { Recomendacion } from '@/services/recomendaciones';
import { mesCorto } from '@/utils/formato';
import IconoAccion from './IconoAccion';

export interface FiltrosValores {
  marca: string;
  pais: string;
  campana: string;
  grupo: string;
  sitio: string;
  mes: string;
  prioridad: string;
  accion: string;
  q: string;
}

export function useFiltros(): [FiltrosValores, (k: keyof FiltrosValores, v: string) => void] {
  const [params, setParams] = useSearchParams();
  const { pathname } = useLocation();
  const clave = `filtros:${pathname}`;
  // Se recuerdan por pestaña (SEM, SEO): al volver sin filtros en la URL, o al refrescar, se recuperan los últimos.
  useEffect(() => {
    if ([...params.keys()].length === 0) {
      const guardados = leerGuardado<string>(clave, '');
      if (guardados) setParams(new URLSearchParams(guardados), { replace: true });
    } else guardar(clave, params.toString());
  }, [clave, params, setParams]);
  const valores: FiltrosValores = {
    marca: params.get('marca') ?? '',
    pais: params.get('pais') ?? '',
    campana: params.get('campana') ?? '',
    grupo: params.get('grupo') ?? '',
    sitio: params.get('sitio') ?? '',
    mes: params.get('mes') ?? '',
    prioridad: params.get('prioridad') ?? '',
    accion: params.get('accion') ?? '',
    q: params.get('q') ?? '',
  };
  const set = (k: keyof FiltrosValores, v: string) => {
    // se parte de la URL actual y no de `params` del último render: dos cambios seguidos (p. ej. limpiar cliente y país)
    // no se pisan aunque React todavía no haya vuelto a dibujar
    const p = new URLSearchParams(window.location.search);
    if (v) p.set(k, v);
    else p.delete(k);
    if (k === 'campana') p.delete('grupo');
    if (k === 'marca' || k === 'pais') {
      if (k === 'marca') p.delete('pais');
      p.delete('campana');
      p.delete('grupo');
    }
    guardar(clave, p.toString()); // vacío también: si se limpian los filtros, no vuelven al recargar
    setParams(p, { replace: true });
  };
  return [valores, set];
}

/** `paisDe` resuelve el país de una tarjeta (el de su campaña, o el de la unidad para las que no tienen campaña). */
export function aplicarFiltros(lista: Recomendacion[], f: FiltrosValores, paisDe?: (r: Recomendacion) => string | null): Recomendacion[] {
  const q = f.q.trim().toLowerCase();
  return lista.filter(
    (r) =>
      (!f.marca || r.marca === f.marca) &&
      (!f.pais || (paisDe?.(r) ?? '').includes(f.pais)) &&
      (!f.campana || r.campanaId === f.campana) &&
      (!f.grupo || r.grupoId === f.grupo) &&
      (!f.sitio || r.sitio === f.sitio) &&
      (!f.mes || r.mesAlta === f.mes) &&
      (!f.prioridad || r.prioridad === f.prioridad) &&
      (!f.accion || accionesDe(r.evidencia).includes(f.accion)) &&
      (!q || r.titulo.toLowerCase().includes(q) || r.detalle.toLowerCase().includes(q)),
  );
}

/** Filtros activos en palabras, para la hoja «Léeme» del Excel. */
export function filtrosActivos(
  f: FiltrosValores,
  nombre: { campana?: (id: string) => string | undefined; grupo?: (id: string) => string | undefined } = {},
): { etiqueta: string; valor: string }[] {
  const out: { etiqueta: string; valor: string }[] = [];
  if (f.marca) out.push({ etiqueta: 'Cliente', valor: MARCA_BY_ID[f.marca as keyof typeof MARCA_BY_ID]?.label ?? f.marca });
  if (f.pais) out.push({ etiqueta: 'País', valor: f.pais });
  if (f.campana) out.push({ etiqueta: 'Campaña', valor: nombre.campana?.(f.campana) ?? f.campana });
  if (f.grupo) out.push({ etiqueta: 'Grupo de anuncios', valor: nombre.grupo?.(f.grupo) ?? f.grupo });
  if (f.sitio) out.push({ etiqueta: 'Sitio', valor: f.sitio });
  if (f.mes) out.push({ etiqueta: 'Mes de alta', valor: mesCorto(f.mes) });
  if (f.prioridad) out.push({ etiqueta: 'Prioridad', valor: PRIORIDAD_BY_ID[f.prioridad as keyof typeof PRIORIDAD_BY_ID]?.label ?? f.prioridad });
  if (f.accion) out.push({ etiqueta: 'Tipo de mejora', valor: ACCIONES.find((a) => a.id === f.accion)?.label ?? f.accion });
  if (f.q.trim()) out.push({ etiqueta: 'Búsqueda', valor: f.q.trim() });
  return out;
}

/**
 * Fila de chips para filtrar por tipo de mejora. `base` es la lista ya filtrada por todo lo demás, para que cada chip
 * muestre cuántas tarjetas quedarían.
 */
export function FiltroAcciones({ valor, onChange, base }: { valor: string; onChange: (v: string) => void; base: Recomendacion[] }) {
  const cuenta = (id: string) => base.filter((r) => accionesDe(r.evidencia).includes(id)).length;
  const chip = (activo: boolean) =>
    `inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[12.5px] font-medium ring-1 transition ${
      activo ? 'bg-mc-fuerte text-white ring-mc-fuerte' : 'bg-mc-sup text-mc-ink ring-mc-hair hover:bg-mc-tint hover:text-mc-navy'
    }`;
  return (
    <div className="-mt-2 mb-5 flex flex-wrap items-center gap-1.5" role="group" aria-label="Tipo de mejora">
      <span className="mr-1 text-[11px] font-bold uppercase tracking-[0.14em] text-mc-grey">Tipo de mejora</span>
      <button type="button" className={chip(!valor)} onClick={() => onChange('')} aria-pressed={!valor}>
        Todas <span className="font-mono text-[11px] opacity-70">{base.length}</span>
      </button>
      {ACCIONES.map((a) => {
        const n = cuenta(a.id);
        if (n === 0 && valor !== a.id) return null;
        return (
          <button key={a.id} type="button" className={chip(valor === a.id)} onClick={() => onChange(valor === a.id ? '' : a.id)} aria-pressed={valor === a.id} title={a.label}>
            <IconoAccion id={a.id} size={13} />
            {a.label} <span className="font-mono text-[11px] opacity-70">{n}</span>
          </button>
        );
      })}
    </div>
  );
}

interface Props {
  valores: FiltrosValores;
  onChange: (k: keyof FiltrosValores, v: string) => void;
  paises?: string[];
  campanas?: { id: string; label: string; marca: string; pais: string }[];
  grupos?: { id: string; label: string; campanaId: string }[];
  sitios?: string[];
  meses: string[];
  /** Algo más al final de la barra (p. ej. el botón de exportar). */
  extra?: ReactNode;
}

export default function Filtros({ valores, onChange, paises, campanas, grupos, sitios, meses, extra }: Props) {
  const campanasVisibles = (campanas ?? []).filter((c) => (!valores.marca || c.marca === valores.marca) && (!valores.pais || c.pais === valores.pais));
  const gruposVisibles = (grupos ?? []).filter((g) => valores.campana && g.campanaId === valores.campana);
  return (
    <div className="mb-5 flex flex-wrap items-center gap-2 rounded-card bg-mc-sup px-3 py-2.5 shadow-card">
      <Select ariaLabel="Cliente" valor={valores.marca} onChange={(v) => onChange('marca', v)} todo="Todos los clientes" opciones={MARCAS.map((m) => ({ id: m.id, label: m.label }))} />
      {paises && <Select ariaLabel="País" valor={valores.pais} onChange={(v) => onChange('pais', v)} todo="Todos los países" opciones={paises.map((p) => ({ id: p, label: p }))} />}
      {campanas && (
        <Select ariaLabel="Campaña" valor={valores.campana} onChange={(v) => onChange('campana', v)} todo="Todas las campañas" opciones={campanasVisibles.map((c) => ({ id: c.id, label: c.label }))} />
      )}
      {grupos && valores.campana && (
        <Select ariaLabel="Grupo de anuncios" valor={valores.grupo} onChange={(v) => onChange('grupo', v)} todo="Todos los grupos" opciones={gruposVisibles.map((g) => ({ id: g.id, label: g.label }))} />
      )}
      {sitios && <Select ariaLabel="Sitio" valor={valores.sitio} onChange={(v) => onChange('sitio', v)} todo="Todos los sitios" opciones={sitios.map((s) => ({ id: s, label: s }))} />}
      <Select ariaLabel="Mes" valor={valores.mes} onChange={(v) => onChange('mes', v)} todo="Todos los meses" opciones={meses.map((m) => ({ id: m, label: mesCorto(m) }))} />
      <Select ariaLabel="Prioridad" valor={valores.prioridad} onChange={(v) => onChange('prioridad', v)} todo="Prioridad" opciones={PRIORIDADES.map((p) => ({ id: p.id, label: p.label }))} />
      <input
        aria-label="Buscar"
        value={valores.q}
        onChange={(e) => onChange('q', e.target.value)}
        placeholder="Buscar en títulos y detalle…"
        className="min-w-[180px] flex-1 rounded-lg border border-mc-hair bg-mc-tint px-2.5 py-1.5 text-sm transition focus:border-mc-blue focus:bg-mc-sup focus:outline-none focus:ring-2 focus:ring-mc-blue/15"
      />
      {extra}
    </div>
  );
}
