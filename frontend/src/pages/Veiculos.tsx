import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Car, LogOut, Search } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { EstadiaAtiva } from "../api/types";
import { Alerta, Botao, Campo, Carregando, Cartao, PageHeader, Placa, Selo, Tabela, Td, Vazio } from "../components/ui";
import { formatarDataHora, formatarDuracao, formatarMoeda, mascararPlaca } from "../lib/format";

export default function Veiculos() {
  const [ativos, setAtivos] = useState<EstadiaAtiva[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [busca, setBusca] = useState("");

  const carregar = useCallback(async () => {
    try { setAtivos(await api.ativos()); setErro(null); }
    catch (e) { setErro(e instanceof ApiError ? e.mensagem : "Falha ao consultar os veículos."); }
  }, []);
  useEffect(() => { void carregar(); const t = setInterval(() => void carregar(), 20_000); return () => clearInterval(t); }, [carregar]);

  const filtrados = useMemo(
    () => (ativos ?? []).filter((a) => a.estadia.placa.includes(busca.replace("-", "").toUpperCase())),
    [ativos, busca],
  );

  return (
    <>
      <PageHeader titulo="Veículos estacionados" descricao="Veículos com estadia ativa e a tarifa acumulada até agora."
        acao={<Link to="/entrada"><Botao type="button">Nova entrada</Botao></Link>} />
      <Cartao>
        <div className="mb-4 max-w-xs">
          <Campo rotulo="Buscar por placa" icone={Search} value={busca} onChange={(e) => setBusca(mascararPlaca(e.target.value))} placeholder="ABC1234" />
        </div>
        {erro && <Alerta tipo="erro">{erro}</Alerta>}
        {!ativos && !erro ? <Carregando /> : filtrados.length === 0 ? (
          <Vazio icone={Car} titulo={busca ? "Nenhum veículo encontrado" : "Nenhum veículo no pátio"} texto={busca ? "Revise a placa digitada." : "As entradas registradas aparecerão aqui."} />
        ) : (
          <Tabela colunas={["Placa", "Entrada", "Permanência", "Tarifa atual", "Operador", ""]}>
            {filtrados.map(({ estadia, tarifa_parcial: t }) => (
              <tr key={estadia.id}>
                <Td><Placa valor={estadia.placa} /></Td>
                <Td>{formatarDataHora(estadia.entrada_em)}</Td>
                <Td>{formatarDuracao(t.permanencia_segundos)}</Td>
                <Td className="font-semibold tabular-nums">
                  {t.atendimento_manual ? <Selo tom="ambar">Atendimento manual</Selo> : formatarMoeda(t.valor_centavos)}
                </Td>
                <Td>{estadia.operador_entrada}</Td>
                <Td className="text-right">
                  <Link to={`/saida?placa=${estadia.placa}`} className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:underline">
                    <LogOut className="size-4" aria-hidden />Saída
                  </Link>
                </Td>
              </tr>
            ))}
          </Tabela>
        )}
      </Cartao>
    </>
  );
}
