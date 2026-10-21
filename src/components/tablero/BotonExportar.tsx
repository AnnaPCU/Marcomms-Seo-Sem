/**
 * Botón «Exportar a Excel»: baja las tarjetas que se ven con los filtros actuales (todas las columnas: propuesta, en
 * proceso, hecha, descartada), con todo su contenido, su historial y una hoja «Léeme». La librería de Excel se carga
 * recién al hacer clic para no sumar peso a la primera carga.
 */
import { useState } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import { listarEventosDe, type Recomendacion } from '@/services/recomendaciones';
import { hojaHistorial, hojaLeeme, hojaTareas, nombreArchivo, type ContextoExport, type Hoja } from '@/utils/exportar';

const ENCABEZADO = { fontWeight: 'bold' as const, textColor: '#FFFFFF', backgroundColor: '#1B1E42', alignVertical: 'center' as const, wrap: true };

function aHoja(h: Hoja) {
  return {
    sheet: h.nombre,
    stickyRowsCount: 1,
    columns: h.anchos.map((width) => ({ width })),
    data: [
      h.encabezado.map((value) => ({ value, ...ENCABEZADO })),
      ...h.filas.map((f) => f.map((value) => (value === null ? null : { value, wrap: true, alignVertical: 'top' as const }))),
    ],
  };
}

export default function BotonExportar({
  recomendaciones,
  contexto,
  tipo,
  partesNombre,
}: {
  recomendaciones: Recomendacion[];
  contexto: ContextoExport;
  tipo: string;
  partesNombre: string[];
}) {
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportar = async () => {
    setOcupado(true);
    setError(null);
    try {
      const eventos = await listarEventosDe(recomendaciones.map((r) => r.id));
      const hojas = [hojaTareas(recomendaciones, contexto), hojaHistorial(recomendaciones, eventos), hojaLeeme(recomendaciones, eventos.length, contexto)];
      const { default: writeXlsxFile } = await import('write-excel-file/browser');
      await writeXlsxFile(hojas.map(aHoja), { fontFamily: 'Calibri', fontSize: 11 }).toFile(nombreArchivo(tipo, partesNombre));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setOcupado(false);
    }
  };

  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        onClick={() => void exportar()}
        disabled={ocupado || !recomendaciones.length}
        title={`Baja las ${recomendaciones.length} tarjetas de esta vista con todo su contenido y su historial`}
        className="inline-flex items-center gap-1.5 rounded-lg border border-mc-hair bg-mc-sup px-3 py-1.5 text-sm font-semibold text-mc-navy transition hover:border-mc-blue hover:text-mc-blue disabled:cursor-not-allowed disabled:opacity-50"
      >
        {ocupado ? <Loader2 size={15} className="animate-spin" /> : <FileSpreadsheet size={15} />}
        Exportar a Excel
        <span className="font-mono text-[11px] font-normal text-mc-grey">{recomendaciones.length}</span>
      </button>
      {error && <span className="text-xs text-red-700">No se pudo exportar: {error}</span>}
    </span>
  );
}
