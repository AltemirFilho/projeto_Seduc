import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Vite roda em :3000 — porta já liberada no CORS do backend
// (SEDU_CORS_ORIGINS = http://localhost:3000, http://127.0.0.1:3000).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    strictPort: true,
  },
});
