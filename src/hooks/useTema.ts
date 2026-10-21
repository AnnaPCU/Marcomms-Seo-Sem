/**
 * Tema claro / oscuro. La elección se guarda en el navegador (clave «mc-seo-sem:tema») y la aplica index.html antes de
 * pintar, así no hay parpadeo. Sin elección guardada, sigue la preferencia del sistema operativo.
 */
import { useCallback, useState } from 'react';

export type Tema = 'claro' | 'oscuro';
const CLAVE = 'mc-seo-sem:tema';

const actual = (): Tema => (document.documentElement.classList.contains('dark') ? 'oscuro' : 'claro');

export function aplicarTema(t: Tema) {
  const raiz = document.documentElement;
  raiz.classList.add('cambiando-tema');
  raiz.classList.toggle('dark', t === 'oscuro');
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', t === 'oscuro' ? '#0d1022' : '#1b1e42');
  window.setTimeout(() => raiz.classList.remove('cambiando-tema'), 250);
  try {
    localStorage.setItem(CLAVE, t);
  } catch {
    /* sin almacenamiento: el tema vale para esta visita */
  }
}

export function useTema(): [Tema, () => void] {
  const [tema, setTema] = useState<Tema>(actual);
  const alternar = useCallback(() => {
    const nuevo: Tema = actual() === 'oscuro' ? 'claro' : 'oscuro';
    aplicarTema(nuevo);
    setTema(nuevo);
  }, []);
  return [tema, alternar];
}
