/** Tablero SEM: recomendaciones de campañas, segmentadas por cliente → campaña → grupo. */
import { useCallback, useMemo } from 'react';
import { useCatalogo, useRecomendaciones } from '@/hooks/useDatos';
import Tablero from '@/components/tablero/Tablero';
import Filtros, { FiltroAcciones, aplicarFiltros, useFiltros } from '@/components/tablero/Filtros';
import { ErrorBox, Intro, SeccionTitulo, Vacio } from '@/components/shared/Ui';
import { EsqueletoTablero } from '@/components/shared/Loader';
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
  // sin el filtro de tipo de mejora: sirve para contar cuántas quedan en cada chip
  const sinAccion = useMemo(() => aplicarFiltros(recs.datos, { ...filtros, accion: '' }, paisDe), [recs.datos, filtros, paisDe]);
  const visibles = useMemo(() => aplicarFiltros(sinAccion, filtros, paisDe), [sinAccion, filtros, paisDe]);

  if (recs.error) return <ErrorBox mensaje={recs.error} />;
  return (
    <div className="animate-fade-in">
      <SeccionTitulo meta="Google Ads · Search">Mejoras por campaña y grupo de anuncios</SeccionTitulo>
      <Intro
        cifras={[
          { valor: visibles.length, etiqueta: 'tarjetas' },
          { valor: visibles.filter((r) => r.prioridad === 'alta' && r.estado !== 'hecha' && r.estado !== 'descartada').length, etiqueta: 'alta abiertas', tono: 'text-red-700' },
          { valor: visibles.filter((r) => r.estado === 'hecha').length, etiqueta: 'hechas', tono: 'text-emerald-700' },
        ]}
      >
        Arrastrá cada tarjeta a la columna que corresponda. Filtrá por cliente, país, campaña y grupo, y por tipo de mejora: anuncio, palabras clave, negativas, estructura. Se renuevan cada mes con la extracción; las que la API confirma aplicadas se marcan solas.
      </Intro>
      <Filtros valores={filtros} onChange={setFiltro} paises={paises} campanas={campanas} grupos={grupos} meses={meses} />
      <FiltroAcciones valor={filtros.accion} onChange={(v) => setFiltro('accion', v)} base={sinAccion} />
      {recs.cargando ? (
        <EsqueletoTablero />
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
