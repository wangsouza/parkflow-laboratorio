import { useEffect, useState, type FormEvent } from "react";
import { Eye, EyeOff, Lock, LogIn, ShieldCheck, User } from "lucide-react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { Logo } from "../components/Logo";
import { Alerta, Botao, Campo } from "../components/ui";

function Relogio() {
  const [agora, setAgora] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setAgora(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <time dateTime={agora.toISOString()} className="tabular-nums">
      {agora.toLocaleString("pt-BR", { weekday: "short", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
    </time>
  );
}

export default function Login() {
  const { usuario: logado, entrar } = useAuth();
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrar, setMostrar] = useState(false);
  const [erros, setErros] = useState<{ usuario?: string; senha?: string }>({});
  const [erroApi, setErroApi] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  if (logado) return <Navigate to="/" replace />;

  async function enviar(e: FormEvent) {
    e.preventDefault();
    const novos: typeof erros = {};
    if (!usuario.trim()) novos.usuario = "Informe o usuário.";
    if (!senha) novos.senha = "Informe a senha.";
    setErros(novos); setErroApi(null);
    if (Object.keys(novos).length) return;

    setCarregando(true);
    try {
      await entrar(usuario.trim(), senha);
    } catch (err) {
      setErroApi(err instanceof ApiError ? err.mensagem : "Não foi possível entrar. Tente novamente.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="asfalto relative grid min-h-full place-items-center overflow-hidden p-4">
      <div className="vagas pointer-events-none absolute inset-x-0 bottom-0 h-72" aria-hidden />
      <div className="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between px-6 py-4 text-xs font-medium text-white/60">
        <span className="flex items-center gap-2"><span className="size-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />Terminal 01 · Operacional</span>
        <Relogio />
      </div>

      <main className="animar-entrada relative w-full max-w-md">
        <div className="rounded-3xl bg-white p-7 shadow-2xl shadow-black/30 sm:p-9">
          <Logo />
          <h1 className="mt-8 text-2xl font-bold tracking-tight text-navy-900">Bem-vindo de volta</h1>
          <p className="mt-1 text-sm text-slate-500">Entre com suas credenciais para operar o estacionamento.</p>

          <form onSubmit={enviar} noValidate className="mt-6 space-y-4">
            {erroApi && <Alerta tipo="erro">{erroApi}</Alerta>}
            <Campo rotulo="Usuário" icone={User} autoComplete="username" autoFocus value={usuario}
              onChange={(e) => setUsuario(e.target.value)} erro={erros.usuario} placeholder="ex.: operador" />
            <Campo rotulo="Senha" icone={Lock} type={mostrar ? "text" : "password"} autoComplete="current-password"
              value={senha} onChange={(e) => setSenha(e.target.value)} erro={erros.senha} placeholder="••••••••"
              direita={
                <button type="button" onClick={() => setMostrar((m) => !m)} aria-label={mostrar ? "Ocultar senha" : "Mostrar senha"}
                  className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
                  {mostrar ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              } />
            <Botao type="submit" larga icone={LogIn} carregando={carregando}>Entrar</Botao>
          </form>

          <div className="mt-6 flex items-start gap-2.5 rounded-xl bg-slate-50 p-3.5 text-xs text-slate-500 ring-1 ring-slate-200">
            <ShieldCheck className="mt-0.5 size-4 shrink-0 text-brand-600" aria-hidden />
            <p>Ambiente de demonstração. Usuários: <b className="text-slate-700">admin</b> e <b className="text-slate-700">operador</b> — as senhas estão no README.</p>
          </div>
        </div>
        <p className="mt-5 text-center text-xs text-white/50">ParkFlow · Laboratório de Testes com IA</p>
      </main>
    </div>
  );
}
