import { useEffect, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { CarFront, CheckCircle2, LogOut, Search } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { EstadiaAtiva, Saida as SaidaDados } from "../api/types";
import { useToast } from "../components/Toast";
import { Alerta, Botao, Campo, Cartao, CartaoTitulo, PageHeader, Placa } from "../components/ui";
import { formatarDataHora, formatarDuracao, formatarMoeda, mascararPlaca } from "../lib/format";

export default function Saida() {
  const avisar = useToast();
  const [params] = useSearchParams();
  const [placa, setPlaca] = useState(mascararPlaca(params.get("placa") ?? ""));
  const [ativa, setAtiva] = useState<EstadiaAtiva | null>(null);
  const [comprovante, setComprovante] = useState<SaidaDados | null>(null);
  const [erro, setErro] = useState<{ tipo: "erro" | "aviso"; titulo?: string; texto: string } | null>(null);
  const [consultando, setConsultando] = useState(false);
  const [confirmando, setConfirmando] = useState(false);

  async function consultar(alvo = placa) {
    setErro(null); setAtiva(null); setComprovante(null);
    if (!alvo.trim()) { setErro({ tipo: "erro", texto: "Informe a placa do veículo." }); return; }
    setConsultando(true);
    try { setAtiva(await api.consultar(alvo)); }
    catch (e) {
      const msg = e instanceof ApiError ? e.mensagem : "Erro ao consultar o veículo.";
      setErro({ tipo: "erro", texto: e instanceof ApiError && e.status === 422 ? "Placa inválida. Use AAA-9999 ou AAA9A99." : msg });
    } finally { setConsultando(false); }
  }

  useEffect(() => { if (params.get("placa")) void consultar(params.get("placa")!); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function confirmar() {
    if (!ativa) return;
    setConfirmando(true); setErro(null);
    try {
      const r = await api.saida(ativa.estadia.placa);
      setComprovante(r); setAtiva(null); setPlaca("");
      avisar("sucesso", `Saída de ${r.estadia.placa} registrada.`);
    } catch (e) {
      if (e instanceof ApiError && e.codigo === "ATENDIMENTO_MANUAL") setErro({ tipo: "aviso", titulo: "Atendimento manual necessário", texto: e.mensagem });
      else setErro({ tipo: "erro", texto: e instanceof ApiError ? e.mensagem : "Erro ao registrar a saída." });
    } finally { setConfirmando(false); }
  }

  const t = ativa?.tarifa_parcial;
  return (
    <>
      <PageHeader titulo="Registrar saída" descricao="Consulte o valor a pagar e confirme a saída do veículo." />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,26rem)_1fr]">
        <Cartao>
          <form onSubmit={(e: FormEvent) => { e.preventDefault(); void consultar(); }} noValidate className="space-y-4">
            <Campo rotulo="Placa" icone={CarFront} value={placa} onChange={(e) => setPlaca(mascararPlaca(e.target.value))}
              placeholder="ABC-1234" autoComplete="off" autoFocus className="placa-mono text-base font-bold uppercase" />
            <Botao type="submit" larga variante="secundario" icone={Search} carregando={consultando}>Consultar valor</Botao>
          </form>
        </Cartao>

        <div className="space-y-4">
          {erro && <Alerta tipo={erro.tipo} titulo={erro.titulo}>{erro.texto}</Alerta>}

          {ativa && t && (
            <Cartao className="animar-entrada">
              <CartaoTitulo titulo="Confirmar saída" subtitulo="Valor calculado até agora" />
              <div className="flex flex-wrap items-center justify-between gap-4">
                <Placa valor={ativa.estadia.placa} />
                <span className="text-sm text-slate-500">Entrada em {formatarDataHora(ativa.estadia.entrada_em)} · {formatarDuracao(t.permanencia_segundos)}</span>
              </div>
              {t.atendimento_manual ? (
                <div className="mt-4"><Alerta tipo="aviso" titulo="Atendimento manual">{t.mensagem}</Alerta></div>
              ) : (
                <div className="mt-4 rounded-2xl bg-navy-900 p-6 text-center text-white">
                  <p className="text-sm text-white/60">Total a pagar</p>
                  <p className="mt-1 text-5xl font-bold tabular-nums">{formatarMoeda(t.valor_centavos)}</p>
                </div>
              )}
              <Botao className="mt-4" larga icone={LogOut} carregando={confirmando} onClick={() => void confirmar()}>
                {t.atendimento_manual ? "Tentar registrar saída" : "Confirmar saída e liberar vaga"}
              </Botao>
            </Cartao>
          )}

          {comprovante && (
            <Cartao className="animar-entrada border-t-4 border-emerald-500">
              <CartaoTitulo titulo="Saída registrada" subtitulo="Comprovante" acao={<CheckCircle2 className="size-6 text-emerald-500" aria-label="Sucesso" />} />
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div><dt className="text-slate-500">Placa</dt><dd className="mt-1"><Placa valor={comprovante.estadia.placa} /></dd></div>
                <div><dt className="text-slate-500">Valor cobrado</dt><dd className="mt-1 text-lg font-bold tabular-nums text-navy-900">{formatarMoeda(comprovante.estadia.valor_centavos)}</dd></div>
                <div><dt className="text-slate-500">Entrada</dt><dd className="mt-1 font-semibold">{formatarDataHora(comprovante.estadia.entrada_em)}</dd></div>
                <div><dt className="text-slate-500">Saída</dt><dd className="mt-1 font-semibold">{formatarDataHora(comprovante.estadia.saida_em)}</dd></div>
                <div><dt className="text-slate-500">Permanência</dt><dd className="mt-1 font-semibold">{formatarDuracao(comprovante.tarifa.permanencia_segundos)}</dd></div>
                <div><dt className="text-slate-500">Regra</dt><dd className="mt-1 font-semibold">{comprovante.tarifa.regra}</dd></div>
              </dl>
            </Cartao>
          )}
        </div>
      </div>
    </>
  );
}
