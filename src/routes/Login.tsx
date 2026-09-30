/** Acceso: solo la contraseña compartida del equipo, con la misma pantalla que MarComms Reports. */
import { useState, type FormEvent } from 'react';
import { Lock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export default function Login() {
  const { entrar } = useAuth();
  const [contrasena, setContrasena] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await entrar(contrasena);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-mc-bg px-4">
      <form onSubmit={(e) => void enviar(e)} className="relative w-full max-w-sm overflow-hidden rounded-card bg-white px-8 py-9 shadow-elevada animate-fade-in">
        <div className="absolute inset-x-0 top-0 h-1 bg-degrade-mc" />
        <img src="/marca/marcomms-vertical-260.png" alt="MarComms" className="h-20 w-auto" />
        <h1 className="mt-6 text-xl">Tablero SEO · SEM</h1>
        <p className="mt-1 text-sm text-mc-grey">Ingresá la contraseña del equipo para continuar.</p>

        <label className="mt-7 block text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-grey" htmlFor="contrasena">
          Contraseña
        </label>
        <div className="mt-1.5 flex items-center rounded-lg border border-mc-hair focus-within:border-mc-blue">
          <Lock size={16} className="ml-3 shrink-0 text-mc-grey" />
          <input
            id="contrasena"
            type="password"
            required
            autoFocus
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            autoComplete="current-password"
            placeholder="••••••••"
            className="w-full bg-transparent px-3 py-2.5 text-sm focus:outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={!contrasena || enviando}
          className="mt-5 w-full rounded-lg bg-mc-blue py-2.5 text-sm font-semibold text-white transition hover:bg-mc-blue2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
        {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      </form>
    </div>
  );
}
