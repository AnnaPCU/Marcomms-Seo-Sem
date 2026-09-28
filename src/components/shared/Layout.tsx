/** Marco de la app: barra lateral con el logo MarComms, navegación y usuario. */
import { NavLink, Outlet } from 'react-router-dom';
import { Home, Megaphone, Search, History, LogOut } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const NAV = [
  { to: '/', label: 'Inicio', icono: Home, fin: true },
  { to: '/sem', label: 'SEM · campañas', icono: Megaphone, fin: false },
  { to: '/seo', label: 'SEO · sitios', icono: Search, fin: false },
  { to: '/historial', label: 'Historial', icono: History, fin: false },
];

export default function Layout() {
  const { email, salir } = useAuth();
  return (
    <div className="flex min-h-full">
      <aside className="flex w-60 shrink-0 flex-col border-r border-mc-hair bg-white">
        <div className="border-b border-mc-hair px-5 py-5">
          <img src="/marca/marcomms-horizontal-600.png" alt="MarComms" className="h-7 w-auto" />
          <div className="mt-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-mc-blue">SEO · SEM</div>
        </div>
        <nav className="flex-1 px-3 py-4">
          {NAV.map(({ to, label, icono: Icono, fin }) => (
            <NavLink
              key={to}
              to={to}
              end={fin}
              className={({ isActive }) =>
                `mb-1 flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-mc-navy text-white' : 'text-mc-ink hover:bg-mc-tint'
                }`
              }
            >
              <Icono size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-mc-hair px-4 py-3 text-xs text-mc-grey">
          <div className="truncate" title={email ?? ''}>
            {email}
          </div>
          <button type="button" onClick={() => void salir()} className="mt-1 inline-flex items-center gap-1 text-mc-navy hover:text-mc-blue">
            <LogOut size={12} /> Salir
          </button>
        </div>
      </aside>
      <main className="min-w-0 flex-1 px-6 py-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
