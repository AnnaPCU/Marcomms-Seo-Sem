/** Diálogo para dejar por escrito por qué se descarta una recomendación. */
import { useState } from 'react';
import { Boton } from '@/components/shared/Ui';

export default function MotivoDescarte({ titulo, onCancelar, onConfirmar }: { titulo: string; onCancelar: () => void; onConfirmar: (motivo: string) => void }) {
  const [motivo, setMotivo] = useState('');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-mc-navy/40 p-4" role="dialog" aria-modal="true">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (motivo.trim()) onConfirmar(motivo.trim());
        }}
        className="w-full max-w-md rounded-card bg-white p-5 shadow-card animate-fade-in"
      >
        <h3 className="text-base">Descartar recomendación</h3>
        <p className="mt-1 text-sm text-mc-grey">{titulo}</p>
        <label className="mt-4 block text-xs font-semibold uppercase tracking-[0.12em] text-mc-grey" htmlFor="motivo">
          Motivo
        </label>
        <textarea
          id="motivo"
          autoFocus
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          rows={3}
          placeholder="Por ejemplo: la campaña se pausó, el cliente no lo aprueba, ya no aplica…"
          className="mt-1 w-full rounded-lg border border-mc-hair px-3 py-2 text-sm focus:border-mc-blue focus:outline-none"
        />
        <div className="mt-4 flex justify-end gap-2">
          <Boton onClick={onCancelar}>Cancelar</Boton>
          <Boton tipo="peligro" type="submit" disabled={!motivo.trim()}>
            Descartar
          </Boton>
        </div>
      </form>
    </div>
  );
}
