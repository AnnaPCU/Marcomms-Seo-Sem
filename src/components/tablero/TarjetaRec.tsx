/** Una recomendación en el tablero: arrastrable entre columnas, clic para abrir el detalle. */
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { CheckCircle2 } from 'lucide-react';
import type { Recomendacion } from '@/services/recomendaciones';
import { ChipMarca, ChipPrioridad } from '@/components/shared/Ui';
import { PRIORIDAD_BY_ID } from '@/constants/estados';
import { campanaCorta, mesCorto } from '@/utils/formato';

export interface Contexto {
  campana: string | null;
  grupo: string | null;
}

export function CuerpoTarjeta({ rec, ctx, arrastrando }: { rec: Recomendacion; ctx: Contexto; arrastrando?: boolean }) {
  const ubicacion = rec.tipo === 'SEM' ? [ctx.campana ? campanaCorta(ctx.campana) : null, ctx.grupo].filter(Boolean).join(' › ') : [rec.sitio, rec.pagina].filter(Boolean).join(' ');
  return (
    <div className={`rounded-card border border-l-4 bg-white px-3 py-2.5 shadow-card ${arrastrando ? 'border-mc-blue' : 'border-mc-hair hover:border-mc-blue/60'} ${PRIORIDAD_BY_ID[rec.prioridad]?.borde ?? ''}`}>
      <div className="mb-1.5 flex items-center gap-1.5">
        <ChipMarca marca={rec.marca} />
        <ChipPrioridad prioridad={rec.prioridad} />
        {rec.verificadaApi && (
          <span title="La API confirmó que está aplicada" className="ml-auto text-mc-blue">
            <CheckCircle2 size={14} />
          </span>
        )}
      </div>
      <div className="text-[13px] font-semibold leading-snug text-mc-navy">{rec.titulo}</div>
      {ubicacion && <div className="mt-1 truncate text-[11px] text-mc-grey" title={ubicacion}>{ubicacion}</div>}
      <div className="mt-1.5 flex items-center justify-between text-[11px] text-mc-grey">
        <span>{mesCorto(rec.mesAlta)}</span>
        {rec.estado === 'descartada' && rec.motivoDescarte && <span className="truncate pl-2 italic" title={rec.motivoDescarte}>{rec.motivoDescarte}</span>}
      </div>
    </div>
  );
}

export default function TarjetaRec({ rec, ctx, onAbrir }: { rec: Recomendacion; ctx: Contexto; onAbrir: (r: Recomendacion) => void }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id: rec.id, data: { rec } });
  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Translate.toString(transform), opacity: isDragging ? 0.35 : 1 }}
      className="cursor-grab touch-none active:cursor-grabbing"
      onClick={() => onAbrir(rec)}
      {...listeners}
      {...attributes}
    >
      <CuerpoTarjeta rec={rec} ctx={ctx} />
    </div>
  );
}
