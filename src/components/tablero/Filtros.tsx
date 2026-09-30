/** Barra de filtros del tablero. Los valores viven en la URL para poder compartir una vista. */
import { useSearchParams } from 'react-router-dom';
import { MARCAS, PRIORIDADES } from '@/constants/estados';
import { Select } from '@/components/shared/Ui';
import type { Recomendacion } from '@/services/recomendaciones';
import { mesCorto } from '@/utils/formato';

export interface FiltrosValores {
  marca: string;
  pais: string;
  campana: string;
  grupo: string;
  sitio: string;
  mes: string;
  prioridad: string;
  q: string;
}

export function useFiltros(): [FiltrosValores, (k: keyof FiltrosValores, v: string) => void] {
  const [params, setParams] = useSearchParams();
  const valores: FiltrosValores = {
    marca: params.get('marca') ?? '',
    pais: params.get('pais') ?? '',
    campana: params.get('campana') ?? '',
    grupo: params.get('grupo') ?? '',
    sitio: params.get('sitio') ?? '',
    mes: params.get('mes') ?? '',
    prioridad: params.get('prioridad') ?? '',
    q: params.get('q') ?? '',
  };
  const set = (k: keyof FiltrosValores, v: string) => {
    const p = new URLSearchParams(params);
    if (v) p.set(k, v);
    else p.delete(k);
    if (k === 'campana') p.delete('grupo');
    if (k === 'marca' || k === 'pais') {
      if (k === 'marca') p.delete('pais');
      p.delete('campana');
      p.delete('grupo');
    }
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
      (!q || r.titulo.toLowerCase().includes(q) || r.detalle.toLowerCase().includes(q)),
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
}

export default function Filtros({ valores, onChange, paises, campanas, grupos, sitios, meses }: Props) {
  const campanasVisibles = (campanas ?? []).filter((c) => (!valores.marca || c.marca === valores.marca) && (!valores.pais || c.pais === valores.pais));
  const gruposVisibles = (grupos ?? []).filter((g) => valores.campana && g.campanaId === valores.campana);
  return (
    <div className="mb-4 flex flex-wrap items-center gap-2">
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
        placeholder="Buscar…"
        className="min-w-[180px] flex-1 rounded-lg border border-mc-hair bg-white px-2.5 py-1.5 text-sm focus:border-mc-blue focus:outline-none"
      />
    </div>
  );
}
