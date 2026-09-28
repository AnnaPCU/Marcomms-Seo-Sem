/**
 * Sesión de Supabase Auth como contexto de React.
 * Google (restringido a los dominios del grupo por trigger en la base) y enlace mágico por correo como alternativa.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import { DOMINIOS_PERMITIDOS } from '@/constants/estados';

interface Auth {
  sesion: Session | null;
  email: string | null;
  cargando: boolean;
  entrarConGoogle: () => Promise<void>;
  entrarConEmail: (email: string) => Promise<void>;
  salir: () => Promise<void>;
}

const Ctx = createContext<Auth | null>(null);

export function dominioPermitido(email: string): boolean {
  const dominio = email.trim().toLowerCase().split('@')[1] ?? '';
  return DOMINIOS_PERMITIDOS.includes(dominio);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Session | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let vivo = true;
    void supabase.auth.getSession().then(({ data }) => {
      if (!vivo) return;
      setSesion(data.session);
      setCargando(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_ev, s) => {
      setSesion(s);
      setCargando(false);
    });
    return () => {
      vivo = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  const entrarConGoogle = useCallback(async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin, queryParams: { prompt: 'select_account' } },
    });
    if (error) throw error;
  }, []);

  const entrarConEmail = useCallback(async (email: string) => {
    if (!dominioPermitido(email)) throw new Error('Solo cuentas @onepeterson.com o @controlunion.com');
    const { error } = await supabase.auth.signInWithOtp({ email: email.trim(), options: { emailRedirectTo: window.location.origin } });
    if (error) throw error;
  }, []);

  const salir = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const valor = useMemo<Auth>(
    () => ({ sesion, email: sesion?.user.email ?? null, cargando, entrarConGoogle, entrarConEmail, salir }),
    [sesion, cargando, entrarConGoogle, entrarConEmail, salir],
  );
  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useAuth(): Auth {
  const v = useContext(Ctx);
  if (!v) throw new Error('useAuth se usa dentro de AuthProvider');
  return v;
}
