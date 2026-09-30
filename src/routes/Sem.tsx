/** Tablero SEM: recomendaciones de campañas, segmentadas por cliente → campaña → grupo. */
import { useCallback, useMemo } from 'react';
import { useCatalogo, useRecomendaciones } from '@/hooks/useDatos';
import Tablero from '@/components/tablero/Tablero';
import Filtros, { aplicarFiltros, useFiltros } from '@/components/tablero/Filtros';
import { Cargando, ErrorBox, Vacio } from '@/components/shared/Ui';
import { campanaCorta } from '@/utils/formato';
import type { Recomendacion } from '@/services/recomendaciones';

export default function Sem() {
  const recs = useRecomendaciones('SEM');
  const cat = useCatalogo();
  const [filtros, setFiltro] = useFiltros();

  const meses = useMemo(() => [...new Set(recs.datos.map((r) => r.mesAlta))].sort().reverse(), [recs.datos]);
  const campanas = useMemo(
    () => cat.campanas.filter((c) => c.estado !== 'REMOVED').map((c) => ({ id: c.id, label: campanaCorta(c.nombre), marca: c.marca, pais: c.unidad })),
    [cat.campanas],
  );
  const paises = useMemo(
    () => [...new Set(cat.campanas.filter((c) => !filtros.marca || c.marca === filtros.marca).map((c) => c.unidad))].filter((p) => p !== 'Sin asignar').sort(),
    [cat.campanas, filtros.marca],
  );
  const campanaDe = cat.campana;
  const paisDe = useCallback(
    (r: Recomendacion) => campanaDe(r.campanaId)?.unidad ?? (typeof r.evidencia.unidad === 'string' ? r.evidencia.unidad : null),
    [campanaDe],
  );
  const grupos = useMemo(() => cat.grupos.map((g) => ({ id: g.id, label: g.nombre, campanaId: g.campanaId })), [cat.grupos]);
  const visibles = useMemo(() => aplicarFiltros(recs.datos, filtros, paisDe), [recs.datos, filtros, paisDe]);

  if (recs.error) return <ErrorBox mensaje={recs.error} />;
  return (
    <div className="animate-fade-in">
      <header className="mb-4">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-blue">SEM · campañas de búsqueda</div>
        <h1 className="text-xl">Mejoras por campaña y grupo de anuncios</h1>
        <p className="mt-1 text-sm text-mc-grey">Arrastrá cada tarjeta a la columna que corresponda. Se renuevan cada mes con la extracción; las que la API confirma aplicadas se marcan solas.</p>
      </header>
      <Filtros valores={filtros} onChange={setFiltro} paises={paises} campanas={campanas} grupos={grupos} meses={meses} />
      {recs.cargando ? (
        <Cargando />
      ) : recs.datos.length === 0 ? (
        <Vacio>No hay recomendaciones cargadas. Corré scripts/publicar.py desde el proyecto de análisis.</Vacio>
      ) : (
        <Tablero
          recomendaciones={visibles}
          aplicarLocal={recs.aplicarLocal}
          contexto={(r) => ({ campana: cat.campana(r.campanaId)?.nombre ?? null, grupo: cat.grupo(r.grupoId)?.nombre ?? null })}
        />
      )}
    </div>
  );
}
