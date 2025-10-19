import React from "react";
import { FaDownload } from "react-icons/fa";

const ReportLayout = ({ title, filters, children, onExport }) => {
  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* --- Encabezado del reporte --- */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-2">
          {title}
        </h1>

        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
        >
          <FaDownload />
          Exportar CSV
        </button>
      </div>

      {/* --- Filtros --- */}
      <div className="flex flex-wrap gap-4 bg-gray-100 p-4 rounded-lg shadow-sm">
        {filters}
      </div>

      {/* --- Tabla o contenido --- */}
      <div className="bg-white shadow rounded-lg overflow-x-auto p-4">
        {children}
      </div>
    </div>
  );
};

export default ReportLayout;
