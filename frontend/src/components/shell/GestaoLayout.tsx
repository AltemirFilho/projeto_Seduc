import { useState } from "react";
import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { navGestao } from "./navGestao";

// Shell da gestão: sidebar (coluna do grid em ≥lg, drawer no mobile) + topbar + conteúdo.
export function GestaoLayout() {
  const [drawerAberto, setDrawerAberto] = useState(false);

  return (
    <div className="min-h-screen bg-bg lg:grid lg:grid-cols-[280px_1fr]">
      <Sidebar grupos={navGestao} aberto={drawerAberto} aoFechar={() => setDrawerAberto(false)} />

      <div className="flex flex-col min-h-screen min-w-0">
        <Topbar aoAbrirMenu={() => setDrawerAberto(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
