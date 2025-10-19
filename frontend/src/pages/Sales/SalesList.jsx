import React, { useEffect, useState, useContext } from "react";
import axiosClient from "../../api/axiosClient.js";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import PaymentModal from "../../components/modals/PaymentModal.jsx";
import InvoiceModal from "../../components/modals/InvoiceModal.jsx";
import QuotationModal from "../../components/modals/QuotationModal.jsx";
import { AuthContext } from "../../context/AuthContext.jsx";

export default function SalesList({ statusFilter, searchTerm, startDate, endDate }) {
  const { user } = useContext(AuthContext);
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedSale, setSelectedSale] = useState(null);
  const [showQuotationModal, setShowQuotationModal] = useState(false);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [invoiceUrl, setInvoiceUrl] = useState(null);

  const API_URL = "/sales/"
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
      const response = await axiosClient.get(API_URL);
      setSales(response.data);
    } catch (error) {
      console.log("Error al obtener ventas", error)
      toast.error("❌ Error al cargar las ventas");
    } finally {
      setLoading(false);
    }
  };

  const openQuotationModal = async (quotationId) => {
    try {
      const response = await axiosClient.get(`/quotations/${quotationId}/`);
      setSelectedQuotation(response.data);
      setShowQuotationModal(true);
    } catch (error) {
      toast.error("❌ No se pudo cargar la cotización.");
    }
  };

  const markDelivered = async (id) => {
    try {
      await axiosClient.post(`${API_URL}${id}/mark_delivered/`);
      toast.success("🚚 Venta marcada como entregada");
      fetchSales();
    } catch {
      toast.error("❌ No se pudo marcar como entregada");
    }
  };

  const markClosed = async (id) => {
    try {
      await axiosClient.post(`${API_URL}${id}/mark_closed/`);
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
    if (nuevoTotal >= total) newStatus = "paid";
    else if (nuevoTotal > 0 && nuevoTotal < total) newStatus = "partially_paid";

    try {
      await axiosClient.post(`${API_URL}${sale.id}/add_payment/`, {
        amount,
        method,
        note,
      });

      if (newStatus !== sale.status) {
        await axiosClient.patch(`${API_URL}${sale.id}/`, { status: newStatus });
      }

      toast.success(`💰 Pago registrado (${newStatus.toUpperCase()})`);
      setShowPaymentModal(false);
      setSelectedSale(null);
      fetchSales();
    } catch (error) {
      toast.error("❌ Error al registrar el pago");
    }
  };

  if (loading)
    return <p className="text-gray-500 text-center mt-10 animate-pulse">Cargando ventas...</p>;

  const filtered = sales.filter((sale) => {
    const matchStatus = statusFilter === "all" ? true : sale.status === statusFilter;
    const search = searchTerm.toLowerCase();
    const matchSearch =
      sale.quotation_name?.toLowerCase().includes(search) ||
      sale.id.toString().includes(search) ||
      sale.quotation_id?.toString().includes(search);
    const saleDate = new Date(sale.sale_date);
    const matchStart = startDate ? saleDate >= new Date(startDate) : true;
    const matchEnd = endDate ? saleDate <= new Date(endDate) : true;
    return matchStatus && matchSearch && matchStart && matchEnd;
  });

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">🧾 Ventas</h2>

      {filtered.length === 0 ? (
        <p className="text-center text-gray-500 py-12">No hay ventas que coincidan.</p>
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
              <div className="flex justify-between items-center p-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800">Venta #{sale.id}</h3>
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

              <div className="p-4 text-sm text-gray-700 space-y-1">
                <p>💲 Total: <span className="font-semibold text-emerald-700">{formatCurrency(sale.total_amount)}</span></p>
                <p>📅 Fecha: {sale.sale_date}</p>
                {sale.delivery_date && <p>🚚 Entrega: {sale.delivery_date}</p>}
                {sale.warranty_end && <p>🛡️ Garantía: {sale.warranty_end}</p>}
                <div className="pt-2 border-t border-gray-200 mt-2 space-y-1">
                  <p>
                    🔖{" "}
                    <a
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        openQuotationModal(sale.quotation_id);
                      }}
                      className="text-emerald-700 hover:underline font-medium"
                    >
                      Ver cotización #{sale.quotation_id}
                    </a>
                  </p>

                  {sale.status === "closed" && sale.invoice_pdf_url && (
                    <p>
                      🧾{" "}
                      <a
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          setInvoiceUrl(sale.invoice_pdf_url);
                          setShowInvoiceModal(true);
                        }}
                        className="text-blue-700 hover:underline font-medium"
                      >
                        Ver factura emitida
                      </a>
                    </p>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-2 p-4 border-t border-gray-100">
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

                {sale.status === "paid" && (
                  <button
                    onClick={() => markDelivered(sale.id)}
                    className="w-full bg-blue-700 hover:bg-blue-800 text-white font-medium py-2 rounded-md transition"
                  >
                    Generar Entrega
                  </button>
                )}

                {sale.status === "delivered" && (
                  <button
                    onClick={() => markClosed(sale.id)}
                    className="w-full bg-orange-700 hover:bg-orange-800 text-white font-medium py-2 rounded-md transition"
                  >
                    Generar Factura
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Modales */}
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

      {showQuotationModal && selectedQuotation && (
        <QuotationModal
          quotation={selectedQuotation}
          onClose={() => {
            setShowQuotationModal(false);
            setSelectedQuotation(null);
          }}
        />
      )}

      {showInvoiceModal && invoiceUrl && (
        <InvoiceModal
          invoiceUrl={invoiceUrl}
          onClose={() => {
            setShowInvoiceModal(false);
            setInvoiceUrl(null);
          }}
        />
      )}
    </div>
  );
}
