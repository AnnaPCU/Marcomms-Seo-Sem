/**
 * Sesión de Supabase Auth como contexto de React.
 * Acceso solo con la contraseña compartida del equipo: la app inicia sesión con la cuenta interna del tablero
 * (seo-sem@onepeterson.com) y la contraseña que escribe la persona. No hay usuarios individuales.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';

/** Cuenta interna del tablero. No es un secreto: lo que protege el acceso es la contraseña. */
export const CUENTA_TABLERO = 'seo-sem@onepeterson.com';

interface Auth {
  sesion: Session | null;
  cargando: boolean;
  entrar: (contrasena: string) => Promise<void>;
  salir: () => Promise<void>;
}

const Ctx = createContext<Auth | null>(null);

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

  const entrar = useCallback(async (contrasena: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email: CUENTA_TABLERO, password: contrasena });
    if (error) {
      const m = error.message;
      throw new Error(
        m.includes('Invalid login') ? 'Contraseña incorrecta' : m.includes('not confirmed') ? 'La cuenta del tablero todavía no está confirmada en Supabase (Authentication → Users).' : m,
      );
    }
  }, []);

  const salir = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const valor = useMemo<Auth>(() => ({ sesion, cargando, entrar, salir }), [sesion, cargando, entrar, salir]);
  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useAuth(): Auth {
  const v = useContext(Ctx);
  if (!v) throw new Error('useAuth se usa dentro de AuthProvider');
  return v;
}
