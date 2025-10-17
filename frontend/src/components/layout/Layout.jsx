import React, { useState } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex flex-col flex-1 min-h-screen overflow-y-auto">
      {/* 🔝 Topbar */}
      <Topbar onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />

      <div className="flex flex-1 overflow-hidden">
        {/* 📱 Sidebar en móviles */}
        <div
          className={`fixed inset-y-0 left-0 z-40 bg-gray-800 text-white transform ${
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
          } transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:w-64`}
        >
          <Sidebar onClose={() => setIsSidebarOpen(false)} />
        </div>

        {/* 🌐 Contenido principal */}
        <main className="flex-1 p-6 bg-gray-50 min-h-screen overflow-y-auto">
          <div className="max-w-7xl mx-auto bg-white rounded-lg shadow-sm p-6">
            {children}
          </div>
        </main>
      </div>

      {/* Fondo oscuro para cerrar menú en móvil */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default Layout;
