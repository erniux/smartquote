import React, { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import {UserIcon} from "@heroicons/react/24/outline";
import PaymentModal from "../modals/PaymentModal.jsx";
import InvoiceModal from "../modals/InvoiceModal.jsx";
import QuotationModal from "../modals/QuotationModal.jsx";



export default function SalesList({ statusFilter, searchTerm, startDate, endDate }) {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE = "http://localhost:8000/api/sales/";
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedSale, setSelectedSale] = useState(null);

  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [invoiceUrl, setInvoiceUrl] = useState(null);

  const [showQuotationModal, setShowQuotationModal] = useState(false);
  const [selectedQuotationId, setSelectedQuotationId] = useState(null);


  const formatCurrency = (value) => {
  if (value == null) return "$0.00";
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
  }).format(value);
};


  useEffect(() => {
    fetchSales();
  }, []);

  const fetchSales = async () => {
    try {
      const response = await axios.get(API_BASE);
      setSales(response.data);
    } catch (error) {
      toast.error("❌ Error al cargar las ventas");
    } finally {
      setLoading(false);
    }
  };

   // --- Filtros locales ---
  const filtered = sales.filter((sale) => {
    // 1️⃣ Filtrar por estado
    const matchStatus =
      statusFilter === "all" ? true : sale.status === statusFilter;

    // 2️⃣ Filtrar por texto (cliente, correo, número)
    const search = searchTerm.toLowerCase();
    const matchSearch =
      sale.quotation_name?.toLowerCase().includes(search) ||
      sale.id.toString().includes(search) ||
      sale.quotation_id?.toString().includes(search);

    // 3️⃣ Filtrar por fechas
    const saleDate = new Date(sale.sale_date);
    const matchStart = startDate ? saleDate >= new Date(startDate) : true;
    const matchEnd = endDate ? saleDate <= new Date(endDate) : true;

    return matchStatus && matchSearch && matchStart && matchEnd;
  });



  // --- Acciones ---
  const markDelivered = async (id) => {
    try {
      await axios.post(`${API_BASE}${id}/mark_delivered/`);
      toast.success("🚚 Venta marcada como entregada");
      fetchSales();
    } catch {
      toast.error("❌ No se pudo marcar como entregada");
    }
  };

  const markClosed = async (id) => {
    try {
      await axios.post(`${API_BASE}${id}/mark_closed/`);
      toast.success("✅ Venta cerrada y factura generada");
      fetchSales();
    } catch {
      toast.error("❌ No se pudo cerrar la venta");
    }
  };

  const handleSavePayment = async ({ amount, method, note }) => {
    if (!selectedSale) return;

    const sale = selectedSale;
    const total = parseFloat(sale.total_amount);
    const totalPagado = (sale.payments || []).reduce(
      (sum, p) => sum + parseFloat(p.amount || 0),
      0
    );
    const nuevoTotal = totalPagado + amount;

    let newStatus = sale.status;
    if (nuevoTotal >= total) {
      newStatus = "paid";
    } else if (nuevoTotal > 0 && nuevoTotal < total) {
      newStatus = "partially_paid";
    }

    try {
      await axios.post(`${API_BASE}${sale.id}/add_payment/`, {
        amount,
        method,
        note,
      });

      if (newStatus !== sale.status) {
        await axios.patch(`${API_BASE}${sale.id}/`, { status: newStatus });
      }

      toast.success(
        `Pago registrado. Estado actualizado a ${
          newStatus === "paid"
            ? "Pagada"
            : newStatus === "partially_paid"
            ? "Pago parcial"
            : "Pendiente"
        }`
      );

      setShowPaymentModal(false);
      setSelectedSale(null);
      fetchSales();
    } catch (error) {
      console.error("Error al registrar pago:", error);
      toast.error("❌ Error al registrar el pago");
    }
  };

  const cancelSale = async (id) => {
    if (!window.confirm("¿Cancelar esta venta?")) return;
    try {
      await axios.patch(`${API_BASE}${id}/`, { status: "cancelada" });
      toast.info("🚫 Venta cancelada");
      fetchSales();
    } catch {
      toast.error("❌ No se pudo cancelar la venta");
    }
  };

  if (loading)
    return (
      <p className="text-gray-500 text-center mt-10 animate-pulse">
        Cargando ventas...
      </p>
    );

 if (sales.length === 0)
    return (
        <p className="text-gray-500 text-center mt-10">
            No hay ventas registradas.
        </p>
    );
 

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          
        </h2>
      </div>
       {filtered.length === 0 ? (
        <div className="text-center text-slate-500 py-12">
          <p>No hay cotizaciones con este estado.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((sale) => (
            <motion.div
                key={sale.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-6 border border-slate-200 hover:-translate-y-1 flex flex-col justify-between"
            >
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800">
                    Venta #{sale.id}
                </h3>
                <span
                    className={`text-xs font-semibold px-3 py-1 rounded-full uppercase ${
                    sale.status === "closed"
                        ? "bg-gray-100 text-gray-700"
                        : sale.status === "paid"
                        ? "bg-green-100 text-green-700"
                        : sale.status === "delivered"
                        ? "bg-blue-100 text-blue-700"
                        : sale.status === "cancelada"
                        ? "bg-red-100 text-red-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                >
                    {sale.status}
                </span>
                </div>

                {/* Body */}
                <div className="flex items-center gap-2 text-gray-500 mb-2">
                <UserIcon className="h-5 w-5 text-gray-400" />
                <span className="text-sm">{sale.quotation_name || "-"}</span>
                </div>

                <div className="p-4 text-sm text-gray-700 space-y-1">
  <p>
    Total:{" "}
    <span className="font-semibold text-emerald-700">
      {formatCurrency(sale.total_amount)}
    </span>
  </p>
  <p>Fecha: {sale.sale_date}</p>
  {sale.delivery_date && <p>Entrega: {sale.delivery_date}</p>}
  {sale.warranty_end && <p>Garantía: {sale.warranty_end}</p>}

  {/* 🔗 Links */}
  <div className="pt-2 space-y-1 border-t border-gray-200 mt-2">
    <p>
      🔖{" "}
      <button
        onClick={() => {
          setSelectedQuotationId(sale.quotation_id);
          setShowQuotationModal(true);
        }}
        className="text-emerald-500 hover:underline font-medium"
      >
        Ver cotización #{sale.quotation_id}
      </button>
    </p>

    {sale.status === "closed" && sale.invoice_pdf_url && (
      <p>
        🧾{" "}
        <button
          onClick={() => {
            setInvoiceUrl(sale.invoice_pdf_url);
            setShowInvoiceModal(true);
          }}
          className="text-blue-700 hover:underline font-medium"
        >
          Ver factura emitida
        </button>
      </p>
    )}
  </div>

</div>

{/* Footer */}
<div className="flex flex-col gap-2 p-4 border-t border-gray-100">

  {/* Pendiente o Pago parcial */}
  {["pending", "partially_paid"].includes(sale.status) && (
    <button
      onClick={() => {
          setSelectedSale(sale);
          setShowPaymentModal(true);
      }}
      className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-md transition"
    >
      Registrar Pago
    </button>
  )}

  {/* Pagada → Generar Entrega */}
  {sale.status === "paid" && (
    <button
      onClick={() => markDelivered(sale.id)}
      className="w-full bg-blue-700 hover:bg-blue-800 text-white font-medium py-2 rounded-md transition"
    >
      Generar Entrega
    </button>
  )}

  {/* Entregada → Generar Factura */}
  {sale.status === "delivered" && (
    <button
      onClick={() => markClosed(sale.id)}
      className="w-full bg-orange-700 hover:bg-orange-800 text-white font-medium py-2 rounded-md transition"
    >
      Generar Factura
    </button>
  )}

  {/* Cancelar solo si no está cerrada ni cancelada */}
  {!["closed", "cancelada"].includes(sale.status) && (
    <button
      onClick={() => cancelSale(sale.id)}
      className="w-full bg-red-900 hover:bg-red-700 text-white font-medium py-2 rounded-md transition"
    >
      Cancelar Venta
    </button>
  )}
  {showPaymentModal && selectedSale && (
    <PaymentModal
      sale={selectedSale}
      onClose={() => {
        setShowPaymentModal(false);
        setSelectedSale(null);
      }}
      onSave={handleSavePayment}
    />
  )}

</div>
</motion.div>
      ))}
</div>
  )}
</div>
    );
}


