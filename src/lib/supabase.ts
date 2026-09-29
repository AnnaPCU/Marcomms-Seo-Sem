/**
 * Único cliente de Supabase de la app (patrón MarComms Hub).
 * Corre en el navegador con la publishable key; la sesión la maneja Supabase Auth.
 * Las tablas viven en el esquema `seo_sem` del proyecto compartido con el Hub; `db.schema` lo fija para todas las consultas.
 * Nada fuera de src/services debería importar este archivo.
 */
import { createClient } from '@supabase/supabase-js';
import type { Database } from '@/lib/database.types';

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined;

if (!url || !key) {
  throw new Error('Faltan VITE_SUPABASE_URL o VITE_SUPABASE_PUBLISHABLE_KEY. Copiá .env.example como .env.local.');
}

export const supabase = createClient<Database, 'seo_sem'>(url, key, {
  db: { schema: 'seo_sem' },
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
});
