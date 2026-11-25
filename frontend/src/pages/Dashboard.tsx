import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { Banknote, Calculator, Car, CircleParking, LogIn, LogOut, RefreshCw, Settings2 } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { EstadiaAtiva, Estadia, Resumo } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { useToast } from "../components/Toast";
import { Alerta, Botao, Campo, Carregando, Cartao, CartaoTitulo, Indicador, PageHeader, Placa, Selo, Tabela, Td, Vazio } from "../components/ui";
import { formatarDataHora, formatarDuracao, formatarHora, formatarMoeda } from "../lib/format";

export default function Dashboard() {
  const { usuario } = useAuth();
  const avisar = useToast();
  const [resumo, setResumo] = useState<Resumo | null>(null);
  const [ativos, setAtivos] = useState<EstadiaAtiva[]>([]);
  const [recentes, setRecentes] = useState<Estadia[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [atualizando, setAtualizando] = useState(false);
  const [capacidade, setCapacidade] = useState("");
  const [salvando, setSalvando] = useState(false);

  const carregar = useCallback(async () => {
    setAtualizando(true);
    try {
      const [r, a, h] = await Promise.all([api.resumo(), api.ativos(), api.historico({ limite: 6 })]);
      setResumo(r); setAtivos(a); setRecentes(h.itens); setErro(null);
    } catch (e) {
      setErro(e instanceof ApiError ? e.mensagem : "Falha ao carregar o painel.");
    } finally { setAtualizando(false); }
  }, []);

  useEffect(() => {
    void carregar();
    const t = setInterval(() => void carregar(), 20_000);
    return () => clearInterval(t);
  }, [carregar]);

  async function salvarCapacidade(e: FormEvent) {
    e.preventDefault();
    setSalvando(true);
    try {
      const r = await api.alterarCapacidade(Number(capacidade));
      avisar("sucesso", `Capacidade atualizada para ${r.capacidade} vagas.`);
      setCapacidade(""); await carregar();
    } catch (err) {
      avisar("erro", err instanceof ApiError ? err.mensagem : "Não foi possível alterar a capacidade.");
    } finally { setSalvando(false); }
  }

  if (!resumo && !erro) return <Carregando texto="Carregando painel…" />;
  const ocupacao = resumo ? Math.round((resumo.ocupadas / resumo.capacidade) * 100) : 0;

  return (
    <>
      <PageHeader titulo="Painel" descricao={resumo ? `Indicadores de ${new Date(resumo.data_referencia + "T12:00:00").toLocaleDateString("pt-BR", { dateStyle: "full" })}` : undefined}
        acao={<Botao variante="secundario" icone={RefreshCw} onClick={() => void carregar()} carregando={atualizando}>Atualizar</Botao>} />
      {erro && <div className="mb-4"><Alerta tipo="erro" titulo="Não foi possível atualizar">{erro}</Alerta></div>}

      {resumo && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-5">
            <Indicador rotulo="Estacionados" valor={resumo.ocupadas} icone={Car} detalhe={`${ocupacao}% de ocupação`} />
            <Indicador rotulo="Vagas livres" valor={resumo.vagas_disponiveis} icone={CircleParking} tom={resumo.vagas_disponiveis === 0 ? "ambar" : "verde"}
              detalhe={resumo.vagas_disponiveis === 0 ? "Lotado" : `de ${resumo.capacidade} vagas`} />
            <Indicador rotulo="Entradas hoje" valor={resumo.entradas_hoje} icone={LogIn} tom="violeta" />
            <Indicador rotulo="Saídas hoje" valor={resumo.saidas_hoje} icone={LogOut} tom="ambar" />
            <div className="col-span-2 lg:col-span-1"><Indicador rotulo="Arrecadado hoje" valor={formatarMoeda(resumo.arrecadado_hoje_centavos)} icone={Banknote} tom="marinho" /></div>
          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-200" role="progressbar" aria-label="Ocupação" aria-valuenow={ocupacao} aria-valuemin={0} aria-valuemax={100}>
            <div className={`h-full rounded-full transition-all ${ocupacao >= 90 ? "bg-amber-500" : "bg-brand-600"}`} style={{ width: `${Math.min(ocupacao, 100)}%` }} />
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <Link to="/entrada"><Botao larga icone={LogIn} type="button">Registrar entrada</Botao></Link>
            <Link to="/tarifa"><Botao larga variante="secundario" icone={Calculator} type="button">Calcular tarifa</Botao></Link>
            <Link to="/saida"><Botao larga variante="secundario" icone={LogOut} type="button">Registrar saída</Botao></Link>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
            <Cartao>
              <CartaoTitulo titulo="Veículos ativos" subtitulo={`${ativos.length} no pátio agora`} acao={<Link to="/veiculos" className="text-sm font-semibold text-brand-600 hover:underline">Ver todos</Link>} />
              {ativos.length === 0 ? <Vazio icone={Car} titulo="Pátio vazio" texto="Registre uma entrada para ver os veículos aqui." /> : (
                <Tabela colunas={["Placa", "Entrada", "Permanência", "Tarifa atual"]}>
                  {ativos.slice(0, 6).map(({ estadia, tarifa_parcial: t }) => (
                    <tr key={estadia.id}>
                      <Td><Placa valor={estadia.placa} /></Td>
                      <Td>{formatarHora(estadia.entrada_em)}</Td>
                      <Td>{formatarDuracao(t.permanencia_segundos)}</Td>
                      <Td className="font-semibold tabular-nums">{t.atendimento_manual ? <Selo tom="ambar">Manual</Selo> : formatarMoeda(t.valor_centavos)}</Td>
                    </tr>
                  ))}
                </Tabela>
              )}
            </Cartao>

            <Cartao>
              <CartaoTitulo titulo="Últimas movimentações" acao={<Link to="/historico" className="text-sm font-semibold text-brand-600 hover:underline">Histórico</Link>} />
              {recentes.length === 0 ? <Vazio icone={LogIn} titulo="Sem movimentações" /> : (
                <Tabela colunas={["Placa", "Movimento", "Valor", "Status"]}>
                  {recentes.map((e) => (
                    <tr key={e.id}>
                      <Td><Placa valor={e.placa} /></Td>
                      <Td>
                        <span className="text-xs text-slate-500">{e.saida_em ? "Saída" : "Entrada"}</span>
                        <br />{formatarDataHora(e.saida_em ?? e.entrada_em)}
                      </Td>
                      <Td className="tabular-nums">{formatarMoeda(e.valor_centavos)}</Td>
                      <Td><Selo tom={e.status === "ATIVA" ? "azul" : "verde"}>{e.status === "ATIVA" ? "Ativa" : "Finalizada"}</Selo></Td>
                    </tr>
                  ))}
                </Tabela>
              )}
            </Cartao>
          </div>

          {usuario?.perfil === "admin" && (
            <Cartao className="mt-6">
              <CartaoTitulo titulo="Configuração (admin)" subtitulo={`Capacidade atual: ${resumo.capacidade} vagas`} />
              <form onSubmit={salvarCapacidade} className="flex flex-wrap items-end gap-3">
                <div className="w-48"><Campo rotulo="Nova capacidade" type="number" min={1} max={500} required value={capacidade} onChange={(e) => setCapacidade(e.target.value)} /></div>
                <Botao type="submit" variante="secundario" icone={Settings2} carregando={salvando}>Salvar</Botao>
              </form>
            </Cartao>
          )}
        </>
      )}
    </>
  );
}
