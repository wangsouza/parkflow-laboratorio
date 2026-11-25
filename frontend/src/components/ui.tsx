import { forwardRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes } from "react";
import { AlertTriangle, CheckCircle2, Info, Loader2, XCircle, type LucideIcon } from "lucide-react";

const cx = (...c: (string | false | undefined)[]) => c.filter(Boolean).join(" ");

/* ---------- Botão ---------- */
type Variante = "primario" | "secundario" | "perigo" | "fantasma";
const VARIANTES: Record<Variante, string> = {
  primario: "bg-brand-600 text-white hover:bg-brand-700 shadow-sm shadow-brand-600/30 focus-visible:outline-brand-600",
  secundario: "bg-white text-navy-900 ring-1 ring-slate-300 hover:bg-slate-50 focus-visible:outline-brand-600",
  perigo: "bg-rose-600 text-white hover:bg-rose-700 focus-visible:outline-rose-600",
  fantasma: "text-slate-600 hover:bg-slate-200/60 focus-visible:outline-brand-600",
};

interface BotaoProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante; carregando?: boolean; icone?: LucideIcon; larga?: boolean;
}
export function Botao({ variante = "primario", carregando, icone: Icone, larga, children, className, disabled, ...r }: BotaoProps) {
  return (
    <button
      {...r}
      disabled={disabled || carregando}
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition",
        "focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-60",
        VARIANTES[variante], larga && "w-full", className,
      )}
    >
      {carregando ? <Loader2 className="size-4 animate-spin" aria-hidden /> : Icone && <Icone className="size-4" aria-hidden />}
      {children}
    </button>
  );
}

/* ---------- Campos ---------- */
interface CampoProps extends InputHTMLAttributes<HTMLInputElement> {
  rotulo: string; erro?: string; ajuda?: string; icone?: LucideIcon; direita?: ReactNode;
}
export const Campo = forwardRef<HTMLInputElement, CampoProps>(function Campo(
  { rotulo, erro, ajuda, icone: Icone, direita, id, className, ...r }, ref,
) {
  const campoId = id ?? `campo-${rotulo.toLowerCase().replace(/\W+/g, "-")}`;
  return (
    <div>
      <label htmlFor={campoId} className="mb-1.5 block text-sm font-medium text-slate-700">{rotulo}</label>
      <div className="relative">
        {Icone && <Icone className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden />}
        <input
          ref={ref} id={campoId} aria-invalid={!!erro} aria-describedby={erro ? `${campoId}-erro` : undefined}
          {...r}
          className={cx(
            "w-full rounded-xl border bg-white py-2.5 text-sm text-slate-900 placeholder:text-slate-400 transition",
            "focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15",
            Icone ? "pl-10" : "pl-3.5", direita ? "pr-11" : "pr-3.5",
            erro ? "border-rose-400" : "border-slate-300", className,
          )}
        />
        {direita && <div className="absolute right-2 top-1/2 -translate-y-1/2">{direita}</div>}
      </div>
      {erro ? <p id={`${campoId}-erro`} role="alert" className="mt-1.5 text-xs font-medium text-rose-600">{erro}</p>
        : ajuda && <p className="mt-1.5 text-xs text-slate-500">{ajuda}</p>}
    </div>
  );
});

export function Seletor({ rotulo, children, id, ...r }: SelectHTMLAttributes<HTMLSelectElement> & { rotulo: string }) {
  const campoId = id ?? `seletor-${rotulo.toLowerCase().replace(/\W+/g, "-")}`;
  return (
    <div>
      <label htmlFor={campoId} className="mb-1.5 block text-sm font-medium text-slate-700">{rotulo}</label>
      <select id={campoId} {...r} className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15">
        {children}
      </select>
    </div>
  );
}

/* ---------- Cartões e indicadores ---------- */
export function Cartao({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cx("min-w-0 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200/70 sm:p-6", className)}>{children}</section>;
}

export function CartaoTitulo({ titulo, subtitulo, acao }: { titulo: string; subtitulo?: string; acao?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 className="text-base font-semibold text-navy-900">{titulo}</h2>
        {subtitulo && <p className="mt-0.5 text-sm text-slate-500">{subtitulo}</p>}
      </div>
      {acao}
    </div>
  );
}

const TONS = {
  azul: "bg-brand-50 text-brand-600", verde: "bg-emerald-50 text-emerald-600",
  ambar: "bg-amber-50 text-amber-600", violeta: "bg-violet-50 text-violet-600", marinho: "bg-navy-900 text-white",
};
export function Indicador({ rotulo, valor, icone: Icone, tom = "azul", detalhe }: {
  rotulo: string; valor: ReactNode; icone: LucideIcon; tom?: keyof typeof TONS; detalhe?: ReactNode;
}) {
  return (
    <div className="animar-entrada rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200/70">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500">{rotulo}</span>
        <span className={cx("grid size-9 place-items-center rounded-xl", TONS[tom])}><Icone className="size-[18px]" aria-hidden /></span>
      </div>
      <div className="mt-3 text-3xl font-bold tracking-tight text-navy-900 tabular-nums">{valor}</div>
      {detalhe && <div className="mt-2 text-xs text-slate-500">{detalhe}</div>}
    </div>
  );
}

export function PageHeader({ titulo, descricao, acao }: { titulo: string; descricao?: string; acao?: ReactNode }) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-navy-900">{titulo}</h1>
        {descricao && <p className="mt-1 text-sm text-slate-500">{descricao}</p>}
      </div>
      {acao}
    </header>
  );
}

/* ---------- Feedback ---------- */
const TIPOS_ALERTA = {
  sucesso: { cls: "bg-emerald-50 text-emerald-900 ring-emerald-200", Icone: CheckCircle2 },
  erro: { cls: "bg-rose-50 text-rose-900 ring-rose-200", Icone: XCircle },
  aviso: { cls: "bg-amber-50 text-amber-900 ring-amber-200", Icone: AlertTriangle },
  info: { cls: "bg-brand-50 text-brand-700 ring-brand-100", Icone: Info },
};
export function Alerta({ tipo, titulo, children }: { tipo: keyof typeof TIPOS_ALERTA; titulo?: string; children?: ReactNode }) {
  const { cls, Icone } = TIPOS_ALERTA[tipo];
  return (
    <div role={tipo === "erro" ? "alert" : "status"} className={cx("animar-entrada flex gap-3 rounded-xl p-4 text-sm ring-1", cls)}>
      <Icone className="mt-0.5 size-5 shrink-0" aria-hidden />
      <div>{titulo && <p className="font-semibold">{titulo}</p>}{children && <div className={titulo ? "mt-0.5" : ""}>{children}</div>}</div>
    </div>
  );
}

export function Selo({ tom, children }: { tom: "verde" | "azul" | "cinza" | "ambar"; children: ReactNode }) {
  const t = { verde: "bg-emerald-50 text-emerald-700 ring-emerald-200", azul: "bg-brand-50 text-brand-700 ring-brand-100",
    cinza: "bg-slate-100 text-slate-600 ring-slate-200", ambar: "bg-amber-50 text-amber-700 ring-amber-200" }[tom];
  return <span className={cx("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1", t)}>{children}</span>;
}

export function Carregando({ texto = "Carregando…" }: { texto?: string }) {
  return <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-500"><Loader2 className="size-4 animate-spin" aria-hidden />{texto}</div>;
}

export function Vazio({ icone: Icone, titulo, texto }: { icone: LucideIcon; titulo: string; texto?: string }) {
  return (
    <div className="flex flex-col items-center py-10 text-center">
      <span className="grid size-12 place-items-center rounded-2xl bg-slate-100 text-slate-400"><Icone className="size-6" aria-hidden /></span>
      <p className="mt-3 text-sm font-semibold text-slate-700">{titulo}</p>
      {texto && <p className="mt-1 max-w-xs text-sm text-slate-500">{texto}</p>}
    </div>
  );
}

/* ---------- Tabela ---------- */
export function Tabela({ colunas, children }: { colunas: string[]; children: ReactNode }) {
  return (
    <div className="-mx-5 overflow-x-auto sm:mx-0">
      <table className="w-full min-w-[26rem] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
            {colunas.map((c) => <th key={c} scope="col" className="px-5 py-2.5 font-semibold first:pl-5 sm:px-3 sm:first:pl-3">{c}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">{children}</tbody>
      </table>
    </div>
  );
}
export const Td = ({ children, className }: { children: ReactNode; className?: string }) =>
  <td className={cx("px-5 py-3 sm:px-3", className)}>{children}</td>;

export function Placa({ valor }: { valor: string }) {
  return (
    <span className="placa-mono inline-block rounded-md border border-slate-300 bg-white px-2 py-0.5 text-[13px] font-bold text-navy-900 shadow-[inset_0_-2px_0_0_#1f57d6]">
      {valor}
    </span>
  );
}
