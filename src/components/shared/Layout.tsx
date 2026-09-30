/**
 * Marco de la app, como MarComms Reports: barra superior blanca fija con el logo, la sección y la frescura de los
 * datos; pestañas con ícono debajo; contenido centrado sobre fondo gris claro.
 */
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { History, LogOut, Megaphone, Search, Wallet, CircleCheck } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useExtracciones } from '@/hooks/useDatos';
import { fecha } from '@/utils/formato';

const NAV = [
  { to: '/', label: 'Presupuesto', sub: 'Presupuesto y gasto de Google Ads', icono: Wallet, fin: true },
  { to: '/sem', label: 'SEM · campañas', sub: 'Mejoras por campaña y grupo de anuncios', icono: Megaphone, fin: false },
  { to: '/seo', label: 'SEO · sitios', sub: 'Mejoras por sitio y página', icono: Search, fin: false },
  { to: '/historial', label: 'Historial', sub: 'Movimientos del tablero', icono: History, fin: false },
];

export default function Layout() {
  const { salir } = useAuth();
  const { pathname } = useLocation();
  const ext = useExtracciones();
  const actual = NAV.find((n) => (n.fin ? pathname === n.to : pathname.startsWith(n.to))) ?? NAV[0];
  const ads = ext.datos.google_ads;

  return (
    <div className="min-h-full bg-mc-bg">
      <header className="sticky top-0 z-30 border-b border-mc-hair/80 bg-white/95 backdrop-blur">
        <div className="h-[3px] bg-degrade-mc" />
        <div className="mx-auto flex max-w-[1240px] items-center gap-4 px-6 py-3">
          <img src="/marca/marcomms-horizontal-600.png" alt="MarComms" className="h-8 w-auto" />
          <div className="hidden border-l border-mc-hair pl-4 sm:block">
            <div className="text-sm font-semibold text-mc-navy">{actual.label}</div>
            <div className="text-[11px] text-mc-grey">{actual.sub}</div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            {ads?.hasta && (
              <span className="hidden items-center gap-1.5 rounded-full bg-sky-50 px-3 py-1 text-[11px] font-semibold text-mc-blue2 ring-1 ring-sky-200 md:inline-flex">
                <CircleCheck size={13} /> Datos reales · Ads al {fecha(ads.hasta)}
              </span>
            )}
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
        <nav className="mx-auto flex max-w-[1240px] gap-1 overflow-x-auto px-6">
          {NAV.map(({ to, label, icono: Icono, fin }) => (
            <NavLink
              key={to}
              to={to}
              end={fin}
              className={({ isActive }) =>
                `-mb-px flex shrink-0 items-center gap-2 border-b-2 px-3 py-2.5 text-[13px] font-medium transition ${
                  isActive ? 'border-mc-blue text-mc-navy' : 'border-transparent text-mc-grey hover:text-mc-navy'
                }`
              }
            >
              <Icono size={15} />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="mx-auto max-w-[1240px] px-6 py-7">
        <Outlet />
      </main>
      <footer className="mx-auto max-w-[1240px] px-6 pb-8 text-[11px] text-mc-grey">
        MarComms · Tablero SEO · SEM · Documento interno. Control Union y Peterson Solutions se muestran por separado y sin su identidad de marca.
      </footer>
    </div>
  );
}
