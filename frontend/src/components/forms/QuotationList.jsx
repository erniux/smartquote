import React, { useEffect, useState } from "react";
import axios from "axios";
import { DocumentTextIcon, UserIcon } from "@heroicons/react/24/outline";
import QuotationModal from "../modals/QuotationModal";

export default function QuotationList({ statusFilter = "Todas" }) {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuotation, setSelectedQuotation] = useState(null);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/quotations/")
      .then((response) => setQuotations(response.data))
      .catch((error) => console.error("Error al obtener cotizaciones:", error))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <p className="text-gray-500 text-center mt-10">
        Cargando cotizaciones...
      </p>
    );
  }

  // 🧩 Filtro de cotizaciones por estado
  const filtered =
    statusFilter === "Todas"
      ? quotations
      : quotations.filter((q) => q.status === statusFilter);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <DocumentTextIcon className="h-8 w-8 text-emerald-600" />
        Cotizaciones Recientes
      </h1>

      {/* 🧠 Mostrar mensaje si no hay cotizaciones */}
      {filtered.length === 0 ? (
        <div className="text-center text-slate-500 py-12">
          <p>No hay cotizaciones con este estado.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((q) => (
            <div
              key={q.id}
              className="bg-white rounded-2xl shadow-md hover:shadow-xl transition p-6 border border-slate-200 hover:-translate-y-1"
            >
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-lg font-semibold text-slate-800">
                  {q.customer_name}
                </h2>
                <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md font-medium">
                  {q.currency}
                </span>
              </div>

              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <UserIcon className="h-5 w-5 text-gray-400" />
                <span className="text-sm">
                  {q.customer_email || "Sin correo"}
                </span>
              </div>

              <div className="text-sm text-slate-600 space-y-1">
                <p>
                  <span className="font-medium text-slate-700">Subtotal:</span>{" "}
                  ${parseFloat(q.subtotal).toLocaleString()}
                </p>
                <p>
                  <span className="font-medium text-slate-700">Total:</span>{" "}
                  <span className="font-semibold text-emerald-700">
                    ${parseFloat(q.total).toLocaleString()}
                  </span>
                </p>
                <p>
                  <span className="font-medium text-slate-700">Fecha:</span>{" "}
                  {q.date}
                </p>
              </div>

              <button
                onClick={() => setSelectedQuotation(q)}
                className="mt-4 w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 transition"
              >
                Ver Detalle
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 🪟 Modal de detalle */}
      {selectedQuotation && (
        <QuotationModal
          quotation={selectedQuotation}
          onClose={() => setSelectedQuotation(null)}
        />
      )}
    </div>
  );
}
