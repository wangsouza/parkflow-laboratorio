import { NavLink, Outlet } from "react-router-dom";
import { Calculator, Car, History, LayoutDashboard, LogIn, LogOut } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { Logo } from "./Logo";

const ITENS = [
  { para: "/", rotulo: "Painel", icone: LayoutDashboard, fim: true },
  { para: "/entrada", rotulo: "Entrada", icone: LogIn },
  { para: "/veiculos", rotulo: "Veículos", icone: Car },
  { para: "/tarifa", rotulo: "Tarifa", icone: Calculator },
  { para: "/saida", rotulo: "Saída", icone: LogOut },
  { para: "/historico", rotulo: "Histórico", icone: History },
];

export function Layout() {
  const { usuario, sair } = useAuth();
  return (
    <div className="min-h-full lg:grid lg:grid-cols-[16rem_1fr]">
      {/* Barra lateral (desktop) */}
      <aside className="asfalto sticky top-0 hidden h-screen flex-col justify-between p-5 lg:flex">
        <div>
          <Logo claro />
          <nav className="mt-10 space-y-1" aria-label="Principal">
            {ITENS.map(({ para, rotulo, icone: Icone, fim }) => (
              <NavLink key={para} to={para} end={fim}
                className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition ${
                  isActive ? "bg-white/12 text-white ring-1 ring-white/15" : "text-white/65 hover:bg-white/8 hover:text-white"}`}>
                <Icone className="size-[18px]" aria-hidden />{rotulo}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="rounded-xl bg-white/8 p-3.5 ring-1 ring-white/10">
          <p className="truncate text-sm font-semibold text-white">{usuario?.usuario}</p>
          <p className="text-xs capitalize text-white/60">{usuario?.perfil}</p>
          <button onClick={sair} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-white/10 py-2 text-xs font-semibold text-white transition hover:bg-white/20">
            <LogOut className="size-3.5" aria-hidden />Sair
          </button>
        </div>
      </aside>

      {/* Cabeçalho (mobile/tablet) */}
      <header className="asfalto sticky top-0 z-30 flex items-center justify-between px-4 py-3 lg:hidden">
        <Logo claro />
        <button onClick={sair} aria-label="Sair" className="rounded-lg bg-white/10 p-2 text-white"><LogOut className="size-5" /></button>
      </header>

      <main className="mx-auto w-full max-w-6xl p-4 pb-28 sm:p-6 lg:p-8 lg:pb-8">
        <Outlet />
      </main>

      {/* Navegação inferior (mobile/tablet) */}
      <nav aria-label="Principal" className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-6 border-t border-slate-200 bg-white/95 backdrop-blur lg:hidden">
        {ITENS.map(({ para, rotulo, icone: Icone, fim }) => (
          <NavLink key={para} to={para} end={fim}
            className={({ isActive }) => `flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium ${isActive ? "text-brand-600" : "text-slate-500"}`}>
            <Icone className="size-5" aria-hidden />{rotulo}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

