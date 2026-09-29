/**
 * Tablero Kanban: cuatro columnas (propuesta → en proceso → hecha → descartada), arrastrar y soltar con dnd-kit.
 * Mover a «descartada» pide un motivo. Cada movimiento deja un evento en la base.
 */
import { useState } from 'react';
import { DndContext, DragOverlay, PointerSensor, useDroppable, useSensor, useSensors, type DragEndEvent, type DragStartEvent } from '@dnd-kit/core';
import type { Estado } from '@/lib/database.types';
import { ESTADOS } from '@/constants/estados';
import { cambiarEstado, type Recomendacion } from '@/services/recomendaciones';
import { useAuth } from '@/hooks/useAuth';
import TarjetaRec, { CuerpoTarjeta, type Contexto } from './TarjetaRec';
import DetalleRec from './DetalleRec';
import MotivoDescarte from './MotivoDescarte';

interface Props {
  recomendaciones: Recomendacion[];
  contexto: (r: Recomendacion) => Contexto;
  aplicarLocal: (fn: (prev: Recomendacion[]) => Recomendacion[]) => void;
}

function Columna({ estado, hijos, cantidad }: { estado: (typeof ESTADOS)[number]; hijos: React.ReactNode; cantidad: number }) {
  const { setNodeRef, isOver } = useDroppable({ id: estado.id });
  return (
    <div ref={setNodeRef} className={`flex min-h-[60vh] flex-col rounded-card border p-2 transition ${isOver ? 'border-mc-blue bg-mc-blue/5' : 'border-mc-hair bg-mc-tint'}`}>
      <div className="mb-2 flex items-center justify-between px-1">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-navy">{estado.label}</div>
          <div className="text-[11px] text-mc-grey">{estado.hint}</div>
        </div>
        <span className="rounded-md bg-white px-1.5 py-0.5 font-mono text-xs text-mc-navy">{cantidad}</span>
      </div>
      <div className="flex flex-1 flex-col gap-2">{hijos}</div>
    </div>
  );
}

export default function Tablero({ recomendaciones, contexto, aplicarLocal }: Props) {
  const { nombre } = useAuth();
  const [activa, setActiva] = useState<Recomendacion | null>(null);
  const [abierta, setAbierta] = useState<Recomendacion | null>(null);
  const [pendienteDescarte, setPendienteDescarte] = useState<Recomendacion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const sensores = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }));

  async function mover(rec: Recomendacion, a: Estado, motivo?: string) {
    if (rec.estado === a) return;
    const antes = rec.estado;
    aplicarLocal((prev) => prev.map((r) => (r.id === rec.id ? { ...r, estado: a, motivoDescarte: a === 'descartada' ? (motivo ?? null) : null } : r)));
    try {
      await cambiarEstado(rec, a, nombre, motivo);
      setError(null);
    } catch (e) {
      aplicarLocal((prev) => prev.map((r) => (r.id === rec.id ? { ...r, estado: antes } : r)));
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function alSoltar(ev: DragEndEvent) {
    setActiva(null);
    const rec = ev.active.data.current?.rec as Recomendacion | undefined;
    const destino = ev.over?.id as Estado | undefined;
    if (!rec || !destino || rec.estado === destino) return;
    if (destino === 'descartada') {
      setPendienteDescarte(rec);
      return;
    }
    void mover(rec, destino);
  }

  const abiertaActual = abierta ? (recomendaciones.find((r) => r.id === abierta.id) ?? abierta) : null;

  return (
    <>
      {error && <div className="mb-3 rounded-card border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">No se pudo guardar: {error}</div>}
      <DndContext sensors={sensores} onDragStart={(ev: DragStartEvent) => setActiva(ev.active.data.current?.rec as Recomendacion)} onDragEnd={alSoltar} onDragCancel={() => setActiva(null)}>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          {ESTADOS.map((estado) => {
            const lista = recomendaciones.filter((r) => r.estado === estado.id);
            return (
              <Columna
                key={estado.id}
                estado={estado}
                cantidad={lista.length}
                hijos={lista.map((r) => (
                  <TarjetaRec key={r.id} rec={r} ctx={contexto(r)} onAbrir={setAbierta} />
                ))}
              />
            );
          })}
        </div>
        <DragOverlay>{activa ? <CuerpoTarjeta rec={activa} ctx={contexto(activa)} arrastrando /> : null}</DragOverlay>
      </DndContext>

      {abiertaActual && (
        <DetalleRec
          rec={abiertaActual}
          ctx={contexto(abiertaActual)}
          onCerrar={() => setAbierta(null)}
          onMover={(a) => (a === 'descartada' ? setPendienteDescarte(abiertaActual) : void mover(abiertaActual, a))}
        />
      )}
      {pendienteDescarte && (
        <MotivoDescarte
          titulo={pendienteDescarte.titulo}
          onCancelar={() => setPendienteDescarte(null)}
          onConfirmar={(motivo) => {
            const rec = pendienteDescarte;
            setPendienteDescarte(null);
            void mover(rec, 'descartada', motivo);
          }}
        />
      )}
    </>
  );
}
