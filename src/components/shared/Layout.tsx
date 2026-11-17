/**
 * Marco de la app, como MarComms Reports: barra superior blanca fija. Arriba, el logo y las pestañas; abajo, los
 * filtros de la vista (cada vista los pone con <FiltrosHeader>) y, a la derecha, la frescura de los datos.
 */
import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { BarChart3, TrendingUp, LogOut, Megaphone, Moon, Search, Sun, Wallet, CircleCheck } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useExtracciones, useUltimoDiaGasto } from '@/hooks/useDatos';
import { useTema } from '@/hooks/useTema';
import { leerGuardado, guardar } from '@/hooks/usePersistente';
import { fecha } from '@/utils/formato';
import Logo from './Logo';
import { RanuraFiltros } from './ranura';

const NAV = [
  { to: '/', label: 'Presupuesto', icono: Wallet, fin: true },
  { to: '/sem', label: 'SEM', icono: Megaphone, fin: false },
  { to: '/seo', label: 'SEO', icono: Search, fin: false },
  { to: '/sitios', label: 'GA4', icono: BarChart3, fin: false },
  { to: '/impacto', label: 'Impacto', icono: TrendingUp, fin: false },
];

/**
 * Vuelve a la misma altura de la página al refrescar o al volver a una pestaña: guarda el scroll de cada sección y,
 * cuando llegan los datos y la página vuelve a tener ese alto, baja hasta ahí. Si la persona scrollea antes, no la mueve.
 */
function useRestaurarScroll(pathname: string) {
  useEffect(() => {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    const clave = `scroll:${pathname}`;
    const objetivo = leerGuardado<number>(clave, 0);
    let activo = objetivo > 0;
    const cortar = () => (activo = false);
    const inicio = Date.now();
    const intentar = () => {
      if (!activo) return;
      if (document.documentElement.scrollHeight >= objetivo + window.innerHeight - 2) {
        window.scrollTo(0, objetivo);
        activo = false;
      } else if (Date.now() - inicio < 5000) requestAnimationFrame(intentar);
      else {
        window.scrollTo(0, objetivo);
        activo = false;
      }
    };
    if (activo) requestAnimationFrame(intentar);
    else window.scrollTo(0, 0);
    let t = 0;
    const alScrollear = () => {
      window.clearTimeout(t);
      t = window.setTimeout(() => guardar(clave, Math.round(window.scrollY)), 150);
    };
    window.addEventListener('wheel', cortar, { passive: true });
    window.addEventListener('touchstart', cortar, { passive: true });
    window.addEventListener('keydown', cortar);
    window.addEventListener('scroll', alScrollear, { passive: true });
    return () => {
      activo = false;
      window.clearTimeout(t);
      window.removeEventListener('wheel', cortar);
      window.removeEventListener('touchstart', cortar);
      window.removeEventListener('keydown', cortar);
      window.removeEventListener('scroll', alScrollear);
    };
  }, [pathname]);
}

export default function Layout() {
  const { salir } = useAuth();
  const { pathname } = useLocation();
  const ext = useExtracciones();
  const ads = ext.datos.google_ads;
  // la fecha de datos es la más nueva entre el último cierre de mes y el último día de gasto diario cargado
  const diario = useUltimoDiaGasto();
  const adsHasta = [ads?.hasta ?? '', diario.datos ?? ''].sort().pop() || null;
  const [tema, alternarTema] = useTema();
  useRestaurarScroll(pathname);
  const [ranura, setRanura] = useState<HTMLDivElement | null>(null);

  return (
    <RanuraFiltros.Provider value={ranura}>
    <div className="min-h-full bg-mc-bg">
      <header className="z-30 border-b border-mc-hair/80 bg-mc-sup/95 backdrop-blur md:sticky md:top-0">
        <div className="h-[3px] bg-degrade-mc" />
        <div className="mx-auto flex max-w-[1240px] flex-wrap items-center gap-x-6 gap-y-2 px-6 py-2.5">
          <Logo className="h-8 w-auto" />
          <nav className="order-last flex w-full gap-1 overflow-x-auto [scrollbar-width:none] md:order-none md:w-auto [&::-webkit-scrollbar]:hidden">
            {NAV.map(({ to, label, icono: Icono, fin }) => (
              <NavLink
                key={to}
                to={to}
                end={fin}
                className={({ isActive }) =>
                  `flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-[13px] font-medium transition ${
                    isActive ? 'bg-mc-tint font-semibold text-mc-navy' : 'text-mc-grey hover:bg-mc-tint/60 hover:text-mc-navy'
                  }`
                }
              >
                <Icono size={15} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={alternarTema}
              title={tema === 'oscuro' ? 'Pasar a modo claro' : 'Pasar a modo oscuro'}
              aria-label={tema === 'oscuro' ? 'Pasar a modo claro' : 'Pasar a modo oscuro'}
              className="grid h-9 w-9 place-items-center rounded-lg border border-mc-hair text-mc-navy transition hover:border-mc-blue hover:text-mc-blue"
            >
              {tema === 'oscuro' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <button
              type="button"
              onClick={() => void salir()}
              title="Salir"
              className="grid h-9 w-9 place-items-center rounded-lg border border-mc-hair text-mc-navy transition hover:border-mc-blue hover:text-mc-blue"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
        <div className="border-t border-mc-hair/60">
          <div className="mx-auto flex max-w-[1240px] flex-wrap items-center gap-3 px-6 py-2.5">
            <div ref={setRanura} className="flex min-w-0 flex-1 flex-wrap items-center gap-2" />
            {adsHasta && (
              <span className="ml-auto hidden shrink-0 items-center gap-1.5 rounded-full bg-sky-50 px-3 py-1 text-[11px] font-semibold text-mc-blue2 ring-1 ring-sky-200 md:inline-flex">
                <CircleCheck size={13} /> Datos reales · Ads al {fecha(adsHasta)}
              </span>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1240px] px-6 py-7">
        <Outlet />
      </main>
      <footer className="mx-auto max-w-[1240px] px-6 pb-8 text-[11px] text-mc-grey">
        MarComms · Tablero SEO · SEM · Documento interno. Control Union y Peterson Solutions se muestran por separado y sin su identidad de marca.
      </footer>
    </div>
    </RanuraFiltros.Provider>
  );
}
