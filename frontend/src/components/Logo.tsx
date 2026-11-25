/** Logotipo próprio do ParkFlow: o "P" de estacionamento dentro de um quadrado arredondado. */
export function LogoMarca({ tamanho = 44 }: { tamanho?: number }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 64 64" role="img" aria-label="Logotipo ParkFlow">
      <rect width="64" height="64" rx="16" fill="#1f57d6" />
      <rect x="3" y="3" width="58" height="58" rx="13" fill="none" stroke="rgba(255,255,255,.25)" strokeWidth="1.5" />
      <path d="M24 48V16h13a11 11 0 0 1 0 22H24" fill="none" stroke="#fff" strokeWidth="7"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Logo({ claro = false }: { claro?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <LogoMarca />
      <div className="leading-none">
        <div className={`text-xl font-bold tracking-tight ${claro ? "text-white" : "text-navy-900"}`}>
          Park<span className="text-brand-500">Flow</span>
        </div>
        <div className={`mt-1 text-[11px] font-medium uppercase tracking-[0.18em] ${claro ? "text-white/60" : "text-slate-500"}`}>
          Gestão de estacionamento
        </div>
      </div>
    </div>
  );
}
