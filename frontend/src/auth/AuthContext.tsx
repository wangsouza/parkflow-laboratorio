import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, aoSessaoExpirar, sessao } from "../api/client";
import type { Token } from "../api/types";

interface Contexto {
  usuario: Token | null;
  entrar: (usuario: string, senha: string) => Promise<void>;
  sair: () => void;
}

const AuthContext = createContext<Contexto | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Token | null>(() => {
    const salvo = sessao.obter();
    return salvo && new Date(salvo.expira_em) > new Date() ? salvo : null;
  });

  const sair = useCallback(() => { sessao.limpar(); setUsuario(null); }, []);
  useEffect(() => aoSessaoExpirar(sair), [sair]);

  const entrar = useCallback(async (nome: string, senha: string) => {
    const token = await api.login(nome, senha);
    sessao.salvar(token);
    setUsuario(token);
  }, []);

  const valor = useMemo(() => ({ usuario, entrar, sair }), [usuario, entrar, sair]);
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth(): Contexto {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de <AuthProvider>");
  return ctx;
}
