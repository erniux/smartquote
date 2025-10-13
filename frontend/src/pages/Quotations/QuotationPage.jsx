import React, { useState } from "react";
import QuotationList from "../../components/forms/QuotationList.jsx";

const QuotationPage = () => {
  const [statusFilter, setStatusFilter] = useState("Todas");

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-slate-700">Cotizaciones</h1>

      {/* 🔍 Filtro de estado */}
      <div className="bg-white shadow p-4 rounded-lg flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <label className="text-sm font-medium text-slate-600">
            Filtrar por estado:
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500"
          >
            <option>Todas</option>
            <option>Pendiente</option>
            <option>Confirmada</option>
            <option>Cerrada</option>
          </select>
        </div>

        {/* 🎨 Botón destacado */}
        <button
          className="bg-green-600 hover:bg-green-700 text-white font-medium px-5 py-2 rounded-lg shadow transition-colors duration-200"
          onClick={() => console.log(`Filtrando por: ${statusFilter}`)}
        >
          Aplicar filtro
        </button>
      </div>

      {/* 📄 Listado filtrado */}
      <QuotationList statusFilter={statusFilter} />
    </div>
  );
};

export default QuotationPage;
