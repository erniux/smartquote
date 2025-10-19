import React, { useEffect, useState, useContext } from "react";
import axiosClient from "../../api/axiosClient.js";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import { UserIcon } from "@heroicons/react/24/outline";
import QuotationModal from "../../components/modals/QuotationModal.jsx";
import QuotationForm from "./QuotationForm.jsx";
import { AuthContext } from "../../context/AuthContext.jsx";


export default function QuotationList({ statusFilter, searchTerm, startDate, endDate }) {
  const { user } = useContext(AuthContext);
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [editingQuotation, setEditingQuotation] = useState(null);
  const [creating, setCreating] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [quotationToCancel, setQuotationToCancel] = useState(null);
  


  const API_URL = "/quotations/";

  useEffect(() => {
    fetchQuotations();
  }, []);

  const fetchQuotations = async () => {
    try {
      const response = await axiosClient.get(API_URL);
      setQuotations(response.data);
    } catch (error) {
      console.error("Error al obtener cotizaciones:", error);
      toast.error("❌ Error al cargar cotizaciones");
    } finally {
      setLoading(false);
    }
  };

  // 🧠 Filtro local (igual que en Ventas)
  const filtered = quotations.filter((q) => {
    const matchStatus =
      statusFilter === "all" ? true : q.status === statusFilter;

    const search = searchTerm.toLowerCase();
    const matchSearch =
      q.customer_name?.toLowerCase().includes(search) ||
      q.customer_email?.toLowerCase().includes(search) ||
      q.id.toString().includes(search);

    const date = new Date(q.date);
    const matchStart = startDate ? date >= new Date(startDate) : true;
    const matchEnd = endDate ? date <= new Date(endDate) : true;

    return matchStatus && matchSearch && matchStart && matchEnd;
  });


  const handleDuplicate = async (id) => {
    try {
      const response = await axiosClient.post(
        `/quotations/${id}/duplicate/`
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

  const handleCancelQuotation = (quotationId) => {
    setQuotationToCancel(quotationId);
    setCancelReason("");
    setShowCancelModal(true);
};

  const confirmCancelQuotation = async () => {
    if (!cancelReason.trim()) {
    //  alert("Por favor escribe la razón de cancelación.");
      toast.success("✅ Por favor escribe la razón de cancelación.");

      return;
    }

    try {
      const res = await axiosClient.post(
        `/quotations/${quotationToCancel}/cancel/`,
        { reason: cancelReason }
      );

      // alert("❌ Cotización cancelada correctamente.");
      toast.success("✅ Cotización cancelada correctamente.");

      console.log("Cancelación:", res.data);

      setShowCancelModal(false);
      setQuotationToCancel(null);
      setCancelReason("");
      fetchQuotations(); // 🔄 refrescar lista
    } catch (error) {
      console.error("Error al cancelar cotización:", error);
      // alert(error.response?.data?.error || "No se pudo cancelar la cotización.");
      toast.error(error.response?.data?.error || "❌ No se pudo cancelar la cotización.");
    }
  };


  const handleGenerateSale = async (id) => {
    try {
      const response = await axiosClient.post(
        `/quotations/${id}/generate-sale/`
      );

      toast.success(`✅ Venta generada (ID ${response.data.sale_id})`);


      // 🔄 refrescar la lista para reflejar el cambio
      fetchQuotations();

    } catch (error) {
         toast.warning(`${error.response.data.detail}`, { icon: "❕" });
    }
  };

  if (loading) {
    return (
      <p className="text-gray-500 text-center mt-10">
        Cargando cotizaciones...
      </p>
    );
  }
  
  console.log("🧩 Estado creating:", creating);

  return (
    
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      {creating && (
  <>
    {console.log("🧱 Renderizando QuotationForm")}
    <QuotationForm
      quotation={null}
      onClose={() => setCreating(false)}
      onSuccess={() => {
        setCreating(false);
        fetchQuotations();
      }}
    />
  </>
)}

      {user && ["vendedor", "manager", "admin"].includes(user.role) && (
        <button
          onClick={() => {
            console.log("🟢 setCreating(true) ejecutado");
            setCreating(true);
          }}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded-lg shadow-md transition"
        >
          + Nueva Cotización
        </button>
      )}

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
                 <div className="flex flex-wrap justify-end gap-2 mt-1">
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md font-medium whitespace-nowrap">
                    {q.currency}
                  </span>
                  <span className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded-md font-medium whitespace-nowrap">
                    {q.status.toUpperCase()}
                  </span>
                </div>

              </div>
              <div className="mb-4">
                {q.status === "cancelled" && q.cancellation_reason && (
                  <p className="text-xs text-rose-300 mt-1 italic">
                    Motivo: {q.cancellation_reason}
                  </p>
                )}

                {q.status === "cancelled" && q.cancelled_at && (
                  <p className="text-xs text-rose-400">
                    Cancelada el {new Date(q.cancelled_at).toLocaleDateString()}
                  </p>
                )}
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
                    onClick={() => {
                      console.log("🧩 Editando cotización:", q);
                      setEditingQuotation(q);
                    }}
                    className="w-full bg-blue-500 text-white py-2 rounded-lg font-medium hover:bg-blue-600 transition"
                  >
                    Editar Cotización
                  </button>
                )}

                {/* 🟡 Generar Venta (solo si NO está cancelada ni confirmada) */}
                {!["confirmed"].includes(q.status) && q.status !== "cancelled" && !q.sale && (
                  <button
                    onClick={() => handleGenerateSale(q.id)}
                    className="w-full bg-amber-500 text-white py-2 rounded-lg font-medium hover:bg-amber-600 transition"
                  >
                    Generar Venta
                  </button>
                )}

                {q.status !== "cancelled" && q.status !== "confirmed" && (
                  <button
                    onClick={() => handleCancelQuotation(q.id)}
                    className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-md transition"
                  >
                    Cancelar
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

          {/* ➕ Modal de Creación */}
          {creating && (
            <QuotationForm
              quotation={null}
              onClose={() => setCreating(false)}
              onSuccess={() => {
                setCreating(false);
                fetchQuotations();
              }}
            />
          )}

          {showCancelModal && (
            <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
              <div className="bg-emerald-900 text-white p-6 rounded-2xl w-96 shadow-lg border border-emerald-700">
                <h2 className="text-lg font-semibold text-rose-300 mb-4">
                  Cancelar cotización
                </h2>

                <label className="block text-sm mb-1 text-emerald-100">
                  Motivo de cancelación:
                </label>
                <textarea
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  rows="4"
                  className="w-full p-2 rounded-md bg-emerald-800 border border-emerald-600 focus:ring-2 focus:ring-rose-400 focus:outline-none text-white text-sm"
                  placeholder="Escribe aquí el motivo..."
                />

                <div className="flex justify-end mt-4 gap-3">
                  <button
                    onClick={() => setShowCancelModal(false)}
                    className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-2 rounded-md text-sm transition"
                  >
                    Volver
                  </button>
                  <button
                    onClick={confirmCancelQuotation}
                    className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-md text-sm transition"
                  >
                    Confirmar cancelación
                  </button>
                </div>
              </div>
            </div>
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
