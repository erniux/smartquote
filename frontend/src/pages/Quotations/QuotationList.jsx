import React, { useState, useEffect } from "react";
import {
  FaEnvelope,
  FaMoneyBillWave,
  FaCalendarAlt,
  FaInfoCircle,
} from "react-icons/fa";
import QuotationForm from "./QuotationForm.jsx";

const QuotationList = ({ statusFilter }) => {
  const [quotations, setQuotations] = useState([]);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [editingQuotation, setEditingQuotation] = useState(null);

  // Simulamos datos (en producción vienen del backend)
  useEffect(() => {
    setQuotations([
      {
        id: 1,
        customer_name: "Jose Martinez Fernandez",
        customer_email: "jose@test.com",
        subtotal: 49017.1,
        total: 56859.83,
        date: "2025-10-12",
        status: "draft",
        currency: "MXN",
      },
      {
        id: 2,
        customer_name: "Roberto Flores Fernandez",
        customer_email: "roberto@test.com",
        subtotal: 5882.05,
        total: 6823.18,
        date: "2025-10-12",
        status: "confirmed",
        currency: "MXN",
      },
      {
        id: 3,
        customer_name: "Erna Tercero Rodríguez",
        customer_email: "erniux@esmeralda.mx",
        subtotal: 14882.04,
        total: 17263.17,
        date: "2025-10-12",
        status: "cancelled",
        currency: "MXN",
      },
    ]);
  }, []);

  // 🔍 Aplicar filtro de estado
  const filtered =
    statusFilter === "all"
      ? quotations
      : quotations.filter((q) => q.status === statusFilter);

  // 🔄 Refrescar lista (simulado)
  const fetchQuotations = () => {
    setQuotations([...quotations]);
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {filtered.map((q) => (
        <div
          key={q.id}
          className="bg-white rounded-xl shadow hover:shadow-lg transition p-6 flex flex-col justify-between"
        >
          {/* --- Información principal --- */}
          <div>
            <h3 className="text-lg font-semibold text-slate-700 mb-1">
              {q.customer_name}
            </h3>
            <p className="flex items-center text-sm text-gray-500 mb-2">
              <FaEnvelope className="mr-2 text-gray-400" /> {q.customer_email}
            </p>

            <p className="flex items-center text-sm text-gray-500 mb-1">
              <FaMoneyBillWave className="mr-2 text-green-500" /> Subtotal:
              <span className="ml-1 font-medium text-slate-600">
                {q.subtotal.toLocaleString("es-MX", {
                  style: "currency",
                  currency: q.currency,
                })}
              </span>
            </p>

            <p className="flex items-center text-sm text-gray-500 mb-1">
              <FaMoneyBillWave className="mr-2 text-green-500" /> Total:
              <span className="ml-1 font-semibold text-green-600">
                {q.total.toLocaleString("es-MX", {
                  style: "currency",
                  currency: q.currency,
                })}
              </span>
            </p>

            <p className="flex items-center text-sm text-gray-500">
              <FaCalendarAlt className="mr-2 text-blue-400" /> Fecha: {q.date}
            </p>

            {/* Etiqueta de estado */}
            <span
              className={`mt-3 inline-block text-xs font-semibold px-3 py-1 rounded-full ${
                q.status === "draft"
                  ? "bg-blue-100 text-blue-700"
                  : q.status === "confirmed"
                  ? "bg-green-100 text-green-700"
                  : q.status === "cancelled"
                  ? "bg-red-100 text-red-700"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {q.status.toUpperCase()}
            </span>
          </div>

          {/* --- Botones --- */}
          <div className="mt-4 flex flex-col gap-2">
            <button
              onClick={() => setSelectedQuotation(q)}
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center transition"
            >
              <FaInfoCircle className="mr-2" /> Ver Detalle
            </button>

            {/* 🟢 Editar solo si está en Draft */}
            {q.status === "draft" && (
              <button
                onClick={() => setEditingQuotation(q)}
                className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition"
              >
                Editar Cotización
              </button>
            )}
          </div>
        </div>
      ))}

      {/* --- Modal Detalle --- */}
      {selectedQuotation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-11/12 max-w-lg relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-700"
              onClick={() => setSelectedQuotation(null)}
            >
              ✕
            </button>
            <h2 className="text-xl font-bold text-slate-800 mb-4">
              Detalles de la Cotización
            </h2>
            <p>
              <strong>Cliente:</strong> {selectedQuotation.customer_name}
            </p>
            <p>
              <strong>Correo:</strong> {selectedQuotation.customer_email}
            </p>
            <p>
              <strong>Estado:</strong> {selectedQuotation.status}
            </p>
            <p>
              <strong>Fecha:</strong> {selectedQuotation.date}
            </p>
            <p className="mt-3 text-green-600 font-semibold text-lg">
              Total:{" "}
              {selectedQuotation.total.toLocaleString("es-MX", {
                style: "currency",
                currency: selectedQuotation.currency,
              })}
            </p>
          </div>
        </div>
      )}

      {/* --- Modal de Edición --- */}
      {editingQuotation && (
        <QuotationForm
          quotation={editingQuotation}
          onClose={() => setEditingQuotation(null)}
          onSuccess={() => {
            setEditingQuotation(null);
            fetchQuotations();
          }}
        />
      )}
    </div>
  );
};

export default QuotationList;
