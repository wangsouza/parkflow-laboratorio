const FUSO = "America/Sao_Paulo";

/** Centavos inteiros → "R$ 13,00". */
export function formatarMoeda(centavos: number | null | undefined): string {
  if (centavos === null || centavos === undefined) return "—";
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function formatarDataHora(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", {
    timeZone: FUSO, day: "2-digit", month: "2-digit", year: "2-digit", hour: "2-digit", minute: "2-digit",
  });
}

export function formatarHora(iso: string): string {
  return new Date(iso).toLocaleTimeString("pt-BR", { timeZone: FUSO, hour: "2-digit", minute: "2-digit" });
}

/** 5400 → "1h 30min"; 45 → "45s". */
export function formatarDuracao(segundos: number): string {
  if (segundos < 60) return `${segundos}s`;
  const h = Math.floor(segundos / 3600);
  const m = Math.floor((segundos % 3600) / 60);
  const s = segundos % 60;
  if (h === 0) return s ? `${m}min ${s}s` : `${m}min`;
  return m ? `${h}h ${m}min` : `${h}h`;
}

/** Converte o valor de <input type="datetime-local"> (hora local do navegador) em ISO-8601 com offset. */
export function localParaIso(valor: string): string {
  return new Date(valor).toISOString();
}

/** Date → valor aceito por <input type="datetime-local">. */
export function paraInputLocal(data: Date): string {
  const deslocada = new Date(data.getTime() - data.getTimezoneOffset() * 60_000);
  return deslocada.toISOString().slice(0, 16);
}

/** Máscara leve: maiúsculas, remove caracteres inválidos e limita o tamanho (AAA-9999 / AAA9A99). */
export function mascararPlaca(texto: string): string {
  return texto.toUpperCase().replace(/[^A-Z0-9-]/g, "").slice(0, 8);
}
