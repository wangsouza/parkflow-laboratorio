export type Perfil = "admin" | "operador";
export type StatusEstadia = "ATIVA" | "FINALIZADA";

export interface Token { access_token: string; token_type: string; expira_em: string; usuario: string; perfil: Perfil }
export interface Estadia {
  id: number; placa: string; entrada_em: string; saida_em: string | null; status: StatusEstadia;
  valor_centavos: number | null; operador_entrada: string; operador_saida: string | null;
}
export interface Tarifa {
  permanencia_segundos: number; valor_centavos: number | null; atendimento_manual: boolean;
  regra: string; mensagem: string | null;
}
export interface EstadiaAtiva { estadia: Estadia; tarifa_parcial: Tarifa }
export interface Saida { estadia: Estadia; tarifa: Tarifa }
export interface Historico { total: number; limite: number; deslocamento: number; itens: Estadia[] }
export interface Resumo {
  data_referencia: string; capacidade: number; ocupadas: number; vagas_disponiveis: number;
  entradas_hoje: number; saidas_hoje: number; arrecadado_hoje_centavos: number;
}
export interface FiltrosHistorico {
  placa?: string; status?: StatusEstadia | ""; de?: string; ate?: string; limite?: number; deslocamento?: number;
}
