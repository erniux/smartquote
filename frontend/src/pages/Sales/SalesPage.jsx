import React, { useState } from "react";
import SalesList from "../../components/forms/SalesList.jsx";
import { DocumentTextIcon, UserIcon } from "@heroicons/react/24/outline";

const QuotationPage = () => {
  // 👇 Un solo estado para el filtro
  const [statusFilter, setStatusFilter] = useState("all");

  return (
    <div className="flex flex-col gap-6">
      {/* Título */}
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <DocumentTextIcon className="h-8 w-8 text-emerald-600" />
        Cotizaciones Recientes
      </h1>

      {/* 🔍 Filtro de estado */}
      <div className="bg-white shadow p-4 rounded-lg flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <label
            htmlFor="status"
            className="text-sm font-medium text-slate-600"
          >
            Filtrar por estado:
          </label>

          <select
            id="status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-white border border-gray-300 text-gray-700 text-sm rounded-md shadow-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 px-3 py-2 outline-none transition"
          >
            <option value="all">Todas</option>
            <option value="draft">Borrador</option>
            <option value="confirmed">Confirmada</option>
            <option value="cancelled">Cancelada</option>
          </select>
        </div>
      </div>

      {/* 📄 Listado filtrado */}
      <QuotationList statusFilter={statusFilter} />
    </div>
  );
};

export default QuotationPage;
