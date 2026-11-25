import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { CarFront, CheckCircle2, Clock, LogIn } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { Estadia } from "../api/types";
import { useToast } from "../components/Toast";
import { Alerta, Botao, Campo, Cartao, CartaoTitulo, PageHeader, Placa } from "../components/ui";
import { formatarDataHora, localParaIso, mascararPlaca, paraInputLocal } from "../lib/format";

export default function Entrada() {
  const avisar = useToast();
  const [placa, setPlaca] = useState("");
  const [manual, setManual] = useState(false);
  const [horario, setHorario] = useState(paraInputLocal(new Date()));
  const [erroCampo, setErroCampo] = useState<string>();
  const [erro, setErro] = useState<string | null>(null);
  const [ticket, setTicket] = useState<Estadia | null>(null);
  const [carregando, setCarregando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setErro(null); setTicket(null);
    if (!placa.trim()) { setErroCampo("Informe a placa do veículo."); return; }
    setErroCampo(undefined);
    setCarregando(true);
    try {
      const estadia = await api.entrada(placa, manual ? localParaIso(horario) : undefined);
      setTicket(estadia); setPlaca("");
      avisar("sucesso", `Entrada de ${estadia.placa} registrada.`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.mensagem : "Erro ao registrar a entrada.";
      if (err instanceof ApiError && err.codigo === "VALIDACAO") setErroCampo("Placa inválida. Use AAA-9999 ou AAA9A99.");
      else setErro(msg);
    } finally { setCarregando(false); }
  }

  return (
    <>
      <PageHeader titulo="Registrar entrada" descricao="Informe a placa do veículo que está entrando no estacionamento." />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,26rem)_1fr]">
        <Cartao>
          <form onSubmit={enviar} noValidate className="space-y-4">
            {erro && <Alerta tipo="erro">{erro}</Alerta>}
            <Campo rotulo="Placa" icone={CarFront} value={placa} onChange={(e) => setPlaca(mascararPlaca(e.target.value))}
              placeholder="ABC-1234 ou BRA2E19" autoComplete="off" autoFocus erro={erroCampo}
              ajuda="Aceita placa convencional e Mercosul." className="placa-mono text-base font-bold uppercase" />
            <label className="flex cursor-pointer items-center gap-2.5 text-sm text-slate-600">
              <input type="checkbox" checked={manual} onChange={(e) => setManual(e.target.checked)} className="size-4 rounded border-slate-300 text-brand-600" />
              Informar horário manualmente
            </label>
            {manual && <Campo rotulo="Horário de entrada" type="datetime-local" icone={Clock} value={horario} onChange={(e) => setHorario(e.target.value)} />}
            <Botao type="submit" larga icone={LogIn} carregando={carregando}>Registrar entrada</Botao>
          </form>
        </Cartao>

        {ticket ? (
          <Cartao className="animar-entrada border-t-4 border-emerald-500">
            <CartaoTitulo titulo="Entrada registrada" subtitulo="Ticket digital" acao={<CheckCircle2 className="size-6 text-emerald-500" aria-label="Sucesso" />} />
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div><dt className="text-slate-500">Placa</dt><dd className="mt-1"><Placa valor={ticket.placa} /></dd></div>
              <div><dt className="text-slate-500">Nº da estadia</dt><dd className="mt-1 font-semibold tabular-nums">#{ticket.id}</dd></div>
              <div><dt className="text-slate-500">Entrada</dt><dd className="mt-1 font-semibold">{formatarDataHora(ticket.entrada_em)}</dd></div>
              <div><dt className="text-slate-500">Operador</dt><dd className="mt-1 font-semibold">{ticket.operador_entrada}</dd></div>
            </dl>
            <p className="mt-5 rounded-xl bg-brand-50 p-3 text-sm text-brand-700">Tolerância de 15 minutos sem cobrança. Depois, R$ 8,00 na primeira hora.</p>
            <Link to="/veiculos" className="mt-4 inline-block text-sm font-semibold text-brand-600 hover:underline">Ver veículos estacionados →</Link>
          </Cartao>
        ) : (
          <Cartao className="hidden bg-navy-900 text-white lg:block">
            <h2 className="text-base font-semibold">Tarifas em vigor</h2>
            <ul className="mt-4 space-y-3 text-sm text-white/80">
              <li className="flex justify-between"><span>Até 15 min</span><b className="text-white">Grátis</b></li>
              <li className="flex justify-between"><span>Primeira hora</span><b className="text-white">R$ 8,00</b></li>
              <li className="flex justify-between"><span>Hora adicional iniciada</span><b className="text-white">R$ 5,00</b></li>
              <li className="flex justify-between"><span>Máximo (até 24 h)</span><b className="text-white">R$ 30,00</b></li>
            </ul>
          </Cartao>
        )}
      </div>
    </>
  );
}
