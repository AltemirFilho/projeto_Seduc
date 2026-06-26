import { QueryClient } from "@tanstack/react-query";
import { ApiError } from "./api/client";

// Não re-tentar erros de cliente (4xx, incl. os 403 de auth do backend);
// re-tentar só falhas transitórias (rede / 5xx).
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (tentativas, erro) => {
        if (erro instanceof ApiError && erro.status >= 400 && erro.status < 500) return false;
        return tentativas < 2;
      },
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});
