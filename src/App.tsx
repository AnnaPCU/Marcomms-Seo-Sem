/** Rutas de la app. Todo salvo /login exige sesión. */
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/hooks/useAuth';
import Layout from '@/components/shared/Layout';
import { PantallaCarga } from '@/components/shared/Loader';
import Login from '@/routes/Login';
import Inicio from '@/routes/Inicio';
import Sem from '@/routes/Sem';
import Seo from '@/routes/Seo';
import Historial from '@/routes/Historial';

function Privado() {
  const { sesion, cargando } = useAuth();
  if (cargando) return <PantallaCarga />;
  return sesion ? <Layout /> : <Navigate to="/login" replace />;
}

function Publico() {
  const { sesion, cargando } = useAuth();
  if (cargando) return <PantallaCarga />;
  return sesion ? <Navigate to="/" replace /> : <Login />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Publico />} />
          <Route element={<Privado />}>
            <Route index element={<Inicio />} />
            <Route path="sem" element={<Sem />} />
            <Route path="seo" element={<Seo />} />
            <Route path="historial" element={<Historial />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
