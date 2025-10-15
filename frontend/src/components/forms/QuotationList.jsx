import React, { useEffect, useState } from "react";
import axios from "axios";
import { DocumentTextIcon, UserIcon } from "@heroicons/react/24/outline";
import QuotationModal from "../modals/QuotationModal";
import QuotationForm from "./QuotationForm.jsx";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from "@heroicons/react/24/solid";

export default function QuotationList({ statusFilter }) {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [editingQuotation, setEditingQuotation] = useState(null);


  useEffect(() => {
    fetchQuotations();
  }, []);

  const statusConfig = {
    confirmed: {
      icon: <CheckCircleIcon className="w-4 h-4 text-emerald-700" />,
      classes: "bg-emerald-50 text-emerald-700",
    },
    cancelled: {
      icon: <XCircleIcon className="w-4 h-4 text-rose-700" />,
      classes: "bg-rose-50 text-rose-700",
    },
    draft: {
      icon: <ClockIcon className="w-4 h-4 text-yellow-700" />,
      classes: "bg-yellow-50 text-yellow-700",
    },
  };


  const fetchQuotations = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/quotations/");
      setQuotations(response.data);
    } catch (error) {
      console.error("Error al obtener cotizaciones:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicate = async (id) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/quotations/${id}/duplicate/`
      );
      setSuccessMessage(response.data.detail);
      fetchQuotations();
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (error) {
      console.error("Error al duplicar cotización:", error);
      setSuccessMessage("❌ No se pudo duplicar la cotización");
      setTimeout(() => setSuccessMessage(null), 4000);
    }
  };


  const handleGenerateSale = async (id) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/quotations/${id}/generate-sale/`
      );
      setSuccessMessage(`✅ Venta generada (ID ${response.data.sale_id})`);

      // 🔄 refrescar la lista para reflejar el cambio
      fetchQuotations();

      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (error) {
      console.error("Error al generar la venta:", error);
      setSuccessMessage("❌ Error al generar la venta");
      setTimeout(() => setSuccessMessage(null), 4000);
    }
  };

  if (loading) {
    return (
      <p className="text-gray-500 text-center mt-10">
        Cargando cotizaciones...
      </p>
    );
  }

  const filtered =
    statusFilter === "all"
      ? quotations
      : quotations.filter((q) => q.status === statusFilter);

   
  

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <DocumentTextIcon className="h-8 w-8 text-emerald-600" />
        Cotizaciones Recientes
      </h1>

      {successMessage && (
        <div className="bg-emerald-100 border border-emerald-400 text-emerald-800 px-4 py-2 rounded mb-4 text-center">
          {successMessage}
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="text-center text-slate-500 py-12">
          <p>No hay cotizaciones con este estado.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((q) => (
            <motion.div
              key={q.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-6 border border-slate-200 hover:-translate-y-1 flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h2 className="text-lg font-semibold text-slate-800">
                    {q.customer_name}
                  </h2>
                 <div className="flex items-center gap-2">
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md font-medium">
                    {q.currency}
                  </span>
                  <span
                    className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md font-medium  ${
                      statusConfig[q.status]?.classes || "bg-gray-50 text-gray-700"
                    }`}
                  >
                    {statusConfig[q.status]?.icon}
                    {q.status.toUpperCase()}
                  </span>
                </div>

              </div>

                <div className="flex items-center gap-2 text-gray-500 mb-2">
                  <UserIcon className="h-5 w-5 text-gray-400" />
                  <span className="text-sm">{q.customer_email || "Sin correo"}</span>
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
              </div>

              <div className="mt-4 flex flex-col gap-2">
                <button
                  onClick={() => setSelectedQuotation(q)}
                  className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 transition"
                >
                  Ver Detalle
                </button>

                {/* 🟢 Editar Cotización (solo Draft) */}
                {q.status === "draft" &&  (
                  <button
                    onClick={() => setEditingQuotation(q)}
                    className="w-full bg-blue-500 text-white py-2 rounded-lg font-medium hover:bg-blue-600 transition"
                  >
                    Editar Cotización
                  </button>
                )}

                {/* 🟡 Generar Venta (solo si NO está cancelada ni confirmada) */}
                {!["confirmed"].includes(q.status) && !q.sale && (
                  <button
                    onClick={() => handleGenerateSale(q.id)}
                    className="w-full bg-amber-500 text-white py-2 rounded-lg font-medium hover:bg-amber-600 transition"
                  >
                    Generar Venta
                  </button>
                )}

                {/* 🔁 Duplicar (si está Confirmada o Cancelada) */}
                {["confirmed", "cancelled"].includes(q.status) && (
                  <button
                    onClick={() => handleDuplicate(q.id)}
                    className="w-full bg-slate-600 text-white py-2 rounded-lg font-medium hover:bg-slate-700 transition"
                  >
                    Duplicar Cotización
                  </button>
                )}

                {/* 🧾 Si ya tiene venta, mostrar estatus */}
                {q.sale && (
                  <p className="text-sm text-emerald-600 font-medium text-center">
                    🧾 Venta generada (ID {q.sale.id})
                  </p>
                )}
              </div>

            </motion.div>
          ))}

          {/* 📝 Modal de Edición */}
          {editingQuotation && (
            <QuotationForm
              quotation={editingQuotation}
              onClose={() => setEditingQuotation(null)}
              onSuccess={() => {
                setEditingQuotation(null);
                fetchQuotations();  // 🔄 refresca la lista al guardar
              }}
            />
          )}

        </div>
      )}

      {selectedQuotation && (
        <QuotationModal
          quotation={selectedQuotation}
          onClose={() => setSelectedQuotation(null)}
        />
      )}
    </div>
  );
}
