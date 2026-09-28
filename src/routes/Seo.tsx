/** Tablero SEO: recomendaciones sobre los sitios, segmentadas por cliente → propiedad de Search Console. */
import { useMemo } from 'react';
import { useRecomendaciones } from '@/hooks/useDatos';
import Tablero from '@/components/tablero/Tablero';
import Filtros, { aplicarFiltros, useFiltros } from '@/components/tablero/Filtros';
import { Cargando, ErrorBox, Vacio } from '@/components/shared/Ui';

export default function Seo() {
  const recs = useRecomendaciones('SEO');
  const [filtros, setFiltro] = useFiltros();
  const meses = useMemo(() => [...new Set(recs.datos.map((r) => r.mesAlta))].sort().reverse(), [recs.datos]);
  const sitios = useMemo(
    () => [...new Set(recs.datos.filter((r) => !filtros.marca || r.marca === filtros.marca).map((r) => r.sitio).filter((s): s is string => Boolean(s)))].sort(),
    [recs.datos, filtros.marca],
  );
  const visibles = useMemo(() => aplicarFiltros(recs.datos, filtros), [recs.datos, filtros]);

  if (recs.error) return <ErrorBox mensaje={recs.error} />;
  return (
    <div className="animate-fade-in">
      <header className="mb-4">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-blue">SEO · sitios</div>
        <h1 className="text-xl">Mejoras por sitio y página</h1>
        <p className="mt-1 text-sm text-mc-grey">Salen del histórico de Search Console. Las de plantilla (hreflang, PDFs, títulos) se repiten en varios sitios y se corrigen una sola vez.</p>
      </header>
      <Filtros valores={filtros} onChange={setFiltro} sitios={sitios} meses={meses} />
      {recs.cargando ? (
        <Cargando />
      ) : recs.datos.length === 0 ? (
        <Vacio>No hay recomendaciones SEO cargadas todavía.</Vacio>
      ) : (
        <Tablero recomendaciones={visibles} aplicarLocal={recs.aplicarLocal} contexto={() => ({ campana: null, grupo: null })} />
      )}
    </div>
  );
}
