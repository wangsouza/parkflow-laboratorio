import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { CheckCircle2, XCircle } from "lucide-react";

type Tipo = "sucesso" | "erro";
interface Item { id: number; tipo: Tipo; texto: string }
const ToastContext = createContext<(tipo: Tipo, texto: string) => void>(() => undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [itens, setItens] = useState<Item[]>([]);
  const avisar = useCallback((tipo: Tipo, texto: string) => {
    const id = Date.now() + Math.random();
    setItens((atual) => [...atual, { id, tipo, texto }]);
    setTimeout(() => setItens((atual) => atual.filter((i) => i.id !== id)), 4500);
  }, []);

  return (
    <ToastContext.Provider value={avisar}>
      {children}
      <div aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-20 z-50 flex flex-col items-center gap-2 px-4 lg:bottom-6 lg:items-end lg:pr-6">
        {itens.map((i) => (
          <div key={i.id} className="animar-entrada pointer-events-auto flex max-w-sm items-center gap-2.5 rounded-xl bg-navy-900 px-4 py-3 text-sm font-medium text-white shadow-lg">
            {i.tipo === "sucesso" ? <CheckCircle2 className="size-5 text-emerald-400" aria-hidden /> : <XCircle className="size-5 text-rose-400" aria-hidden />}
            {i.texto}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
export const useToast = () => useContext(ToastContext);
