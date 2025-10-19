import React, { useState } from "react";
import QuotationList from "./QuotationList.jsx";
import { DocumentTextIcon } from "@heroicons/react/24/outline";

const QuotationPage = () => {
  // 👇 Un solo estado para el filtro
  const [statusFilter, setStatusFilter] = useState("all");
    const [searchTerm, setSearchTerm] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

  return (
    <div className="flex flex-col gap-6">
      {/* Título */}
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <DocumentTextIcon className="h-8 w-8 text-emerald-600" />
        Cotizaciones
      </h1>

<div className="bg-[#5d8f88]/90 p-4 rounded-md shadow-sm flex flex-wrap items-center gap-3 justify-between sm:justify-start">
  {/* 🔎 Buscador */}
  <div className="relative flex-1 min-w-[220px]">
    <span className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.8}
        stroke="white"
        className="w-5 h-5 opacity-80"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 21l-4.35-4.35M17.65 9.5A8.15 8.15 0 119.5 1.35 8.15 8.15 0 0117.65 9.5z"
        />
      </svg>
    </span>

    <input
      type="text"
      placeholder="Buscar cliente o correo..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      className="w-full rounded-md pl-10 pr-4 py-2 text-white placeholder-white/90 bg-[#003b32] focus:outline-none focus:ring-2 focus:ring-emerald-400"
    />
  </div>


  {/* 📅 Fechas */}
  <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
    <label className="text-white text-sm">Desde:</label>
    <input
      type="date"
      value={startDate}
      onChange={(e) => setStartDate(e.target.value)}
      className="rounded-md px-3 py-1 bg-[#003b32] text-white focus:outline-none focus:ring-2 focus:ring-emerald-400"
    />

    <label className="text-white text-sm">Hasta:</label>
    <input
      type="date"
      value={endDate}
      onChange={(e) => setEndDate(e.target.value)}
      className="rounded-md px-3 py-1 bg-[#003b32] text-white focus:outline-none focus:ring-2 focus:ring-emerald-400"
    />
  </div>

  {/* 📋 Estado */}
  <div className="min-w-[120px]">
    <select
      value={statusFilter}
      onChange={(e) => setStatusFilter(e.target.value)}
      className="w-full bg-[#003b32] text-white text-sm rounded-md shadow-sm focus:ring-2 focus:ring-emerald-400 px-3 py-2 outline-none"
    >
      <option value="all">Todas</option>
      <option value="draft">Borrador</option>
      <option value="pending">Pendiente</option>
      <option value="confirmed">Confirmada</option>
      <option value="cancelled">Cancelada</option>
    </select>
  </div>

  {/* 🧹 Limpiar filtros */}
  <button
    onClick={() => {
      setSearchTerm("");
      setStartDate("");
      setEndDate("");
      setStatusFilter("all");
    }}
    className="bg-white text-[#003b32] font-semibold px-3 py-2 rounded-md hover:bg-gray-100 shadow-sm transition min-w-[120px]"
  >
    Limpiar filtros
  </button>
</div>


      {/* 📄 Listado filtrado */}
      <QuotationList
        statusFilter={statusFilter}
        searchTerm={searchTerm}
        startDate={startDate}
        endDate={endDate}
      />
    </div>
  );
};

export default QuotationPage;
