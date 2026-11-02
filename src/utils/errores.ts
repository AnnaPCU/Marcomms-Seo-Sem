// Texto legible para cualquier error: los de Supabase (PostgREST) no son instancias de Error sino objetos
// { code, message, hint }, y String(e) los mostraba como «[object Object]».
export function mensajeError(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (e && typeof e === 'object') {
    const { code, message, hint } = e as { code?: string; message?: string; hint?: string };
    if (code === 'PGRST106')
      return 'La base de datos no expone el esquema seo_sem. Hay que volver a agregarlo en Supabase › Project Settings › Data API › Exposed schemas.';
    if (message) return [message, hint].filter(Boolean).join(' · ');
  }
  return String(e);
}
