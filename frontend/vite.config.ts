import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Em desenvolvimento, as chamadas a /api/* são repassadas ao backend FastAPI (porta 8000),
// evitando problemas de CORS. Para outro backend: VITE_PROXY_TARGET=http://host:porta npm run dev
const alvo = process.env.VITE_PROXY_TARGET ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: alvo, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
    },
  },
});
