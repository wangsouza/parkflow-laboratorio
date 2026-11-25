import { useState, type FormEvent } from "react";
import { Calculator, Clock } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { Tarifa as TarifaDados } from "../api/types";
import { Alerta, Botao, Campo, Cartao, CartaoTitulo, PageHeader, Selo } from "../components/ui";
import { formatarDuracao, formatarMoeda, localParaIso, paraInputLocal } from "../lib/format";

const ATALHOS = [15, 16, 60, 61, 120, 121, 301, 1440, 1441];
const DESCRICAO_REGRA: Record<string, string> = {
  R01: "Tolerância gratuita (até 15 min)", R02: "Primeira hora (R$ 8,00)",
  R03: "Horas adicionais iniciadas (R$ 5,00 cada)", R04: "Tarifa máxima diária / limite de 24 h",
};
const rotuloAtalho = (m: number) => (m >= 60 && m % 60 === 0 ? `${m / 60} h` : m === 1441 ? "24 h 01 min" : `${m} min`);

export default function Tarifa() {
  const [entrada, setEntrada] = useState(() => paraInputLocal(new Date(Date.now() - 61 * 60_000)));
  const [saida, setSaida] = useState(() => paraInputLocal(new Date()));
  const [resultado, setResultado] = useState<TarifaDados | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  async function calcular(e?: FormEvent, entradaIso = entrada, saidaIso = saida) {
    e?.preventDefault();
    setErro(null); setCarregando(true);
    try { setResultado(await api.simular(localParaIso(entradaIso), localParaIso(saidaIso))); }
    catch (err) { setResultado(null); setErro(err instanceof ApiError ? err.mensagem : "Erro ao calcular a tarifa."); }
    finally { setCarregando(false); }
  }

  function aplicarAtalho(minutos: number) {
    const base = new Date(entrada);
    const novaSaida = paraInputLocal(new Date(base.getTime() + minutos * 60_000));
    setSaida(novaSaida);
    void calcular(undefined, entrada, novaSaida);
  }

  return (
    <>
      <PageHeader titulo="Simular tarifa" descricao="Calcule o valor para qualquer permanência, sem registrar nada." />
      <div className="grid gap-6 lg:grid-cols-2">
        <Cartao>
          <form onSubmit={calcular} className="space-y-4">
            {erro && <Alerta tipo="erro">{erro}</Alerta>}
            <Campo rotulo="Entrada" type="datetime-local" icone={Clock} value={entrada} onChange={(e) => setEntrada(e.target.value)} required />
            <Campo rotulo="Saída" type="datetime-local" icone={Clock} value={saida} onChange={(e) => setSaida(e.target.value)} required />
            <Botao type="submit" larga icone={Calculator} carregando={carregando}>Calcular tarifa</Botao>
          </form>
          <div className="mt-6">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Permanências de referência</p>
            <div className="flex flex-wrap gap-2">
              {ATALHOS.map((m) => (
                <button key={m} type="button" onClick={() => aplicarAtalho(m)}
                  className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700 ring-1 ring-slate-200 transition hover:bg-brand-50 hover:text-brand-700 hover:ring-brand-100">
                  {rotuloAtalho(m)}
                </button>
              ))}
            </div>
          </div>
        </Cartao>

        <Cartao className={resultado ? "animar-entrada" : ""}>
          <CartaoTitulo titulo="Resultado" />
          {!resultado ? <p className="py-8 text-center text-sm text-slate-500">Informe os horários e calcule para ver o valor.</p> : resultado.atendimento_manual ? (
            <Alerta tipo="aviso" titulo="Atendimento manual">{resultado.mensagem}</Alerta>
          ) : (
            <>
              <div className="rounded-2xl bg-navy-900 p-6 text-center text-white">
                <p className="text-sm text-white/60">Valor a cobrar</p>
                <p className="mt-1 text-5xl font-bold tabular-nums">{formatarMoeda(resultado.valor_centavos)}</p>
              </div>
              <dl className="mt-5 space-y-3 text-sm">
                <div className="flex justify-between"><dt className="text-slate-500">Permanência</dt><dd className="font-semibold">{formatarDuracao(resultado.permanencia_segundos)}</dd></div>
                <div className="flex justify-between gap-4"><dt className="text-slate-500">Regra aplicada</dt>
                  <dd className="text-right font-semibold"><Selo tom="azul">{resultado.regra}</Selo> <span className="block text-xs font-normal text-slate-500">{DESCRICAO_REGRA[resultado.regra]}</span></dd></div>
              </dl>
            </>
          )}
        </Cartao>
      </div>
    </>
  );
}
