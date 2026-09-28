/** Acceso: Google (cuentas del grupo) o enlace por correo. La base rechaza cualquier otro dominio. */
import { useState, type FormEvent } from 'react';
import { useAuth, dominioPermitido } from '@/hooks/useAuth';
import { Boton } from '@/components/shared/Ui';

export default function Login() {
  const { entrarConGoogle, entrarConEmail } = useAuth();
  const [email, setEmail] = useState('');
  const [enviado, setEnviado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function porEmail(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await entrarConEmail(email);
      setEnviado(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-mc-navy px-4">
      <div className="w-full max-w-sm rounded-card bg-white p-7 shadow-card animate-fade-in">
        <img src="/marca/marcomms-horizontal-600.png" alt="MarComms" className="h-8 w-auto" />
        <h1 className="mt-5 text-lg">SEO · SEM</h1>
        <p className="mt-1 text-sm text-mc-grey">Tablero de recomendaciones para las campañas y los sitios de Control Union y Peterson Solutions.</p>

        <div className="mt-6">
          <Boton tipo="primario" onClick={() => void entrarConGoogle().catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))}>
            Entrar con Google
          </Boton>
          <p className="mt-1 text-xs text-mc-grey">Cuentas @onepeterson.com o @controlunion.com.</p>
        </div>

        <div className="my-5 flex items-center gap-3 text-[11px] uppercase tracking-[0.12em] text-mc-grey">
          <span className="h-px flex-1 bg-mc-hair" /> o por correo <span className="h-px flex-1 bg-mc-hair" />
        </div>

        {enviado ? (
          <p className="rounded-lg bg-mc-tint px-3 py-2 text-sm text-mc-navy">Te mandamos un enlace a {email}. Abrilo desde este mismo navegador.</p>
        ) : (
          <form onSubmit={(e) => void porEmail(e)} className="flex gap-2">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="nombre@onepeterson.com"
              className="min-w-0 flex-1 rounded-lg border border-mc-hair px-3 py-1.5 text-sm focus:border-mc-blue focus:outline-none"
            />
            <Boton type="submit" disabled={!dominioPermitido(email)}>
              Enviar enlace
            </Boton>
          </form>
        )}
        {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      </div>
    </div>
  );
}
