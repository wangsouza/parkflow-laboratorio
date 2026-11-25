import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { Layout } from "./components/Layout";
import { ToastProvider } from "./components/Toast";
import Dashboard from "./pages/Dashboard";
import Entrada from "./pages/Entrada";
import Historico from "./pages/Historico";
import Login from "./pages/Login";
import Saida from "./pages/Saida";
import Tarifa from "./pages/Tarifa";
import Veiculos from "./pages/Veiculos";

function Protegido() {
  const { usuario } = useAuth();
  return usuario ? <Layout /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<Protegido />}>
              <Route index element={<Dashboard />} />
              <Route path="entrada" element={<Entrada />} />
              <Route path="veiculos" element={<Veiculos />} />
              <Route path="tarifa" element={<Tarifa />} />
              <Route path="saida" element={<Saida />} />
              <Route path="historico" element={<Historico />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
