import React, { useState } from "react";
import QuotationList from "../../components/forms/QuotationList.jsx";

const QuotationPage = () => {
  // Estado local del filtro
  const [selectedStatus, setSelectedStatus] = useState("all");

  return (
    <div className="flex flex-col gap-6">
      {/* Título */}
      <h1 className="text-2xl font-bold text-slate-700">Cotizaciones</h1>

      {/* 🔍 Filtro de estado */}
      <div className="bg-white shadow p-4 rounded-lg flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <label htmlFor="status" className="text-sm font-medium text-slate-600">
            Filtrar por estado:
          </label>

          <select
            id="status"
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
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
      <QuotationList selectedStatus={selectedStatus} />
    </div>
  );
};

export default QuotationPage;
