import { useCallback, useEffect, useState, type FormEvent } from "react";
import { ChevronLeft, ChevronRight, Filter, History } from "lucide-react";
import { api, ApiError } from "../api/client";
import type { Historico as HistoricoDados, StatusEstadia } from "../api/types";
import { Alerta, Botao, Campo, Carregando, Cartao, PageHeader, Placa, Selo, Seletor, Tabela, Td, Vazio } from "../components/ui";
import { formatarDataHora, formatarMoeda, mascararPlaca } from "../lib/format";

const POR_PAGINA = 10;

export default function Historico() {
  const [filtros, setFiltros] = useState({ placa: "", status: "" as StatusEstadia | "", de: "", ate: "" });
  const [aplicados, setAplicados] = useState(filtros);
  const [pagina, setPagina] = useState(0);
  const [dados, setDados] = useState<HistoricoDados | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(async () => {
    try {
      setDados(await api.historico({
        placa: aplicados.placa || undefined, status: aplicados.status,
        // Datas do filtro → dia inteiro no horário local do navegador.
        de: aplicados.de ? new Date(`${aplicados.de}T00:00:00`).toISOString() : undefined,
        ate: aplicados.ate ? new Date(`${aplicados.ate}T23:59:59`).toISOString() : undefined,
        limite: POR_PAGINA, deslocamento: pagina * POR_PAGINA,
      }));
      setErro(null);
    } catch (e) {
      setDados(null);
      setErro(e instanceof ApiError ? (e.status === 422 ? "Filtro inválido. Confira a placa informada." : e.mensagem) : "Falha ao consultar o histórico.");
    }
  }, [aplicados, pagina]);
  useEffect(() => { void carregar(); }, [carregar]);

  function filtrar(e: FormEvent) { e.preventDefault(); setPagina(0); setAplicados(filtros); }
  function limpar() { const vazio = { placa: "", status: "" as const, de: "", ate: "" }; setFiltros(vazio); setAplicados(vazio); setPagina(0); }
  const totalPaginas = dados ? Math.max(1, Math.ceil(dados.total / POR_PAGINA)) : 1;

  return (
    <>
      <PageHeader titulo="Histórico de movimentações" descricao="Todas as estadias registradas, da mais recente para a mais antiga." />
      <Cartao>
        <form onSubmit={filtrar} className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_1fr_1fr_auto] lg:items-end">
          <Campo rotulo="Placa" value={filtros.placa} onChange={(e) => setFiltros({ ...filtros, placa: mascararPlaca(e.target.value) })} placeholder="ABC1234" />
          <Seletor rotulo="Status" value={filtros.status} onChange={(e) => setFiltros({ ...filtros, status: e.target.value as StatusEstadia | "" })}>
            <option value="">Todos</option><option value="ATIVA">Ativa</option><option value="FINALIZADA">Finalizada</option>
          </Seletor>
          <Campo rotulo="Entrada de" type="date" value={filtros.de} onChange={(e) => setFiltros({ ...filtros, de: e.target.value })} />
          <Campo rotulo="Entrada até" type="date" value={filtros.ate} onChange={(e) => setFiltros({ ...filtros, ate: e.target.value })} />
          <div className="flex gap-2"><Botao type="submit" icone={Filter}>Filtrar</Botao><Botao type="button" variante="fantasma" onClick={limpar}>Limpar</Botao></div>
        </form>

        {erro && <Alerta tipo="erro">{erro}</Alerta>}
        {!dados && !erro ? <Carregando /> : dados && (dados.itens.length === 0 ? (
          <Vazio icone={History} titulo="Nenhuma movimentação encontrada" texto="Ajuste os filtros ou registre novas operações." />
        ) : (
          <>
            <Tabela colunas={["Placa", "Entrada", "Saída", "Valor", "Status", "Operador"]}>
              {dados.itens.map((e) => (
                <tr key={e.id}>
                  <Td><Placa valor={e.placa} /></Td>
                  <Td>{formatarDataHora(e.entrada_em)}</Td>
                  <Td>{formatarDataHora(e.saida_em)}</Td>
                  <Td className="font-semibold tabular-nums">{formatarMoeda(e.valor_centavos)}</Td>
                  <Td><Selo tom={e.status === "ATIVA" ? "azul" : "verde"}>{e.status === "ATIVA" ? "Ativa" : "Finalizada"}</Selo></Td>
                  <Td className="text-slate-500">{e.operador_saida ?? e.operador_entrada}</Td>
                </tr>
              ))}
            </Tabela>
            <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
              <span>{dados.total} registro(s) · página {pagina + 1} de {totalPaginas}</span>
              <div className="flex gap-2">
                <Botao type="button" variante="secundario" icone={ChevronLeft} disabled={pagina === 0} onClick={() => setPagina((p) => p - 1)}>Anterior</Botao>
                <Botao type="button" variante="secundario" icone={ChevronRight} disabled={pagina + 1 >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>Próxima</Botao>
              </div>
            </div>
          </>
        ))}
      </Cartao>
    </>
  );
}
