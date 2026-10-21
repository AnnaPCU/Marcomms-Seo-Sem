/**
 * Estado que sobrevive a un refresh, a cambiar de pestaña del tablero y a cerrar el navegador: se guarda en el
 * almacenamiento local del navegador (localStorage), por usuario y por dispositivo. Si el almacenamiento no está
 * disponible (modo privado, bloqueado) funciona como un useState común.
 */
import { useCallback, useMemo, useState, type Dispatch, type SetStateAction } from 'react';

const PREFIJO = 'mc-seo-sem:';

export function leerGuardado<T>(clave: string, inicial: T): T {
  try {
    const crudo = localStorage.getItem(PREFIJO + clave);
    return crudo === null ? inicial : (JSON.parse(crudo) as T);
  } catch {
    return inicial;
  }
}

export function guardar(clave: string, valor: unknown) {
  try {
    if (valor === undefined) localStorage.removeItem(PREFIJO + clave);
    else localStorage.setItem(PREFIJO + clave, JSON.stringify(valor));
  } catch {
    /* sin almacenamiento: no se recuerda, pero la vista funciona igual */
  }
}

export function usePersistente<T>(clave: string, inicial: T): [T, Dispatch<SetStateAction<T>>] {
  const [valor, setValor] = useState<T>(() => leerGuardado(clave, inicial));
  const set = useCallback<Dispatch<SetStateAction<T>>>(
    (nuevo) =>
      setValor((prev) => {
        const v = typeof nuevo === 'function' ? (nuevo as (p: T) => T)(prev) : nuevo;
        guardar(clave, v);
        return v;
      }),
    [clave],
  );
  return [valor, set];
}

/** Lo mismo para un conjunto (filas abiertas, por ejemplo): se guarda como lista. */
export function usePersistenteSet(clave: string, inicial: string[]): [Set<string>, Dispatch<SetStateAction<Set<string>>>] {
  const [lista, setLista] = usePersistente<string[]>(clave, inicial);
  const conjunto = useMemo(() => new Set(lista), [lista]);
  const set = useCallback<Dispatch<SetStateAction<Set<string>>>>(
    (nuevo) => setLista((prev) => [...(typeof nuevo === 'function' ? nuevo(new Set(prev)) : nuevo)]),
    [setLista],
  );
  return [conjunto, set];
}
