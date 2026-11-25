import type {
  EstadiaAtiva, Estadia, FiltrosHistorico, Historico, Resumo, Saida, Tarifa, Token,
} from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "/api";
const CHAVE_TOKEN = "parkflow.token";

/** Erro devolvido pela API no formato { erro: { codigo, mensagem, detalhes } }. */
export class ApiError extends Error {
  constructor(public status: number, public codigo: string, mensagem: string, public detalhes: unknown[] = []) {
    super(mensagem);
  }
  get mensagem(): string { return this.message; }
}

export const sessao = {
  obter: (): Token | null => {
    const bruto = localStorage.getItem(CHAVE_TOKEN);
    return bruto ? (JSON.parse(bruto) as Token) : null;
  },
  salvar: (t: Token) => localStorage.setItem(CHAVE_TOKEN, JSON.stringify(t)),
  limpar: () => localStorage.removeItem(CHAVE_TOKEN),
};

let aoExpirar: (() => void) | null = null;
export function aoSessaoExpirar(fn: () => void) { aoExpirar = fn; }

async function requisicao<T>(caminho: string, init: RequestInit = {}, autenticado = true): Promise<T> {
  const cabecalhos = new Headers(init.headers);
  if (init.body) cabecalhos.set("Content-Type", "application/json");
  const token = sessao.obter();
  if (autenticado && token) cabecalhos.set("Authorization", `Bearer ${token.access_token}`);

  let resposta: Response;
  try {
    resposta = await fetch(`${BASE}${caminho}`, { ...init, headers: cabecalhos });
  } catch {
    throw new ApiError(0, "SEM_CONEXAO", "Não foi possível conectar ao servidor. Verifique se o backend está em execução.");
  }

  if (resposta.ok) return (await resposta.json()) as T;

  const corpo = await resposta.json().catch(() => null);
  const erro = corpo?.erro;
  if (resposta.status === 401 && autenticado) aoExpirar?.();
  throw new ApiError(
    resposta.status,
    erro?.codigo ?? "ERRO",
    erro?.mensagem ?? `Erro inesperado (HTTP ${resposta.status}).`,
    erro?.detalhes ?? [],
  );
}

const post = <T,>(c: string, corpo: unknown, auth = true) =>
  requisicao<T>(c, { method: "POST", body: JSON.stringify(corpo) }, auth);

export const api = {
  login: (usuario: string, senha: string) => post<Token>("/auth/login", { usuario, senha }, false),
  resumo: () => requisicao<Resumo>("/dashboard/resumo"),
  ativos: () => requisicao<EstadiaAtiva[]>("/veiculos/ativos"),
  consultar: (placa: string) => requisicao<EstadiaAtiva>(`/veiculos/${encodeURIComponent(placa)}`),
  entrada: (placa: string, entradaEm?: string) =>
    post<Estadia>("/veiculos/entrada", { placa, ...(entradaEm ? { entrada_em: entradaEm } : {}) }),
  saida: (placa: string, saidaEm?: string) =>
    post<Saida>("/veiculos/saida", { placa, ...(saidaEm ? { saida_em: saidaEm } : {}) }),
  simular: (entradaEm: string, saidaEm: string) =>
    post<Tarifa>("/tarifas/simular", { entrada_em: entradaEm, saida_em: saidaEm }),
  historico: (f: FiltrosHistorico = {}) => {
    const p = new URLSearchParams();
    Object.entries(f).forEach(([k, v]) => { if (v !== undefined && v !== "") p.set(k, String(v)); });
    return requisicao<Historico>(`/historico?${p.toString()}`);
  },
  alterarCapacidade: (capacidade: number) =>
    requisicao<{ capacidade: number }>("/configuracao/capacidade", {
      method: "PUT", body: JSON.stringify({ capacidade }),
    }),
};
