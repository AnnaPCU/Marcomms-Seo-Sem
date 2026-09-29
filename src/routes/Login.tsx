/** Acceso: contraseña compartida del equipo y el nombre de quien entra (para el historial). */
import { useState, type FormEvent } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Boton } from '@/components/shared/Ui';

export default function Login() {
  const { entrar, nombre } = useAuth();
  const [contrasena, setContrasena] = useState('');
  const [quien, setQuien] = useState(nombre ?? '');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await entrar(contrasena, quien);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-mc-navy px-4">
      <form onSubmit={(e) => void enviar(e)} className="w-full max-w-sm rounded-card bg-white p-7 shadow-card animate-fade-in">
        <img src="/marca/marcomms-horizontal-600.png" alt="MarComms" className="h-8 w-auto" />
        <h1 className="mt-5 text-lg">SEO · SEM</h1>
        <p className="mt-1 text-sm text-mc-grey">Tablero de recomendaciones para las campañas y los sitios de Control Union y Peterson Solutions.</p>

        <label className="mt-6 block text-xs font-semibold uppercase tracking-[0.12em] text-mc-grey" htmlFor="quien">
          Tu nombre
        </label>
        <input
          id="quien"
          value={quien}
          onChange={(e) => setQuien(e.target.value)}
          placeholder="Para saber quién movió cada tarjeta"
          autoComplete="name"
          className="mt-1 w-full rounded-lg border border-mc-hair px-3 py-2 text-sm focus:border-mc-blue focus:outline-none"
        />

        <label className="mt-4 block text-xs font-semibold uppercase tracking-[0.12em] text-mc-grey" htmlFor="contrasena">
          Contraseña del equipo
        </label>
        <input
          id="contrasena"
          type="password"
          required
          autoFocus
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          autoComplete="current-password"
          className="mt-1 w-full rounded-lg border border-mc-hair px-3 py-2 text-sm focus:border-mc-blue focus:outline-none"
        />

        <div className="mt-5">
          <Boton tipo="primario" type="submit" disabled={!contrasena || enviando}>
            {enviando ? 'Entrando…' : 'Entrar'}
          </Boton>
        </div>
        {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      </form>
    </div>
  );
}
