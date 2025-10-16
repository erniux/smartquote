import React, { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import {CurrencyDollarIcon} from "@heroicons/react/24/outline";

export default function SalesList({ statusFilter, searchTerm, startDate, endDate }) {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE = "http://localhost:8000/api/sales/";

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

  const addPayment = async (id) => {
    const amount = prompt("💰 Monto del pago:");
    if (!amount || isNaN(amount)) return;
    try {
      await axios.post(`${API_BASE}${id}/add_payment/`, {
        amount: parseFloat(amount),
        method: "transfer",
      });
      toast.success("💰 Pago registrado correctamente");
      fetchSales();
    } catch {
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
          🧾 Ventas
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((sale) => (
          <div
            key={sale.id}
            className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200"
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
            <div className="p-4 text-sm text-gray-700 space-y-1">
              <p>
                Cliente:{" "}
                <span className="font-medium">
                  {sale.quotation_name || "—"}
                </span>
              </p>
              <p>
                Total:{" "}
                <span className="font-semibold text-emerald-700">
                  ${sale.total_amount?.toLocaleString()}
                </span>
              </p>
              <p>Fecha: {sale.sale_date}</p>
              {sale.delivery_date && <p>Entrega: {sale.delivery_date}</p>}
              {sale.warranty_end && <p>Garantía: {sale.warranty_end}</p>}
            </div>

            {/* Footer */}
            <div className="flex flex-col gap-2 p-4 border-t border-gray-100">
              <button
                onClick={() => addPayment(sale.id)}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-md transition"
              >
                Registrar Pago
              </button>

              <button
                onClick={() => markDelivered(sale.id)}
                className="w-full bg-purple-800 hover:bg-gray-900 text-white font-medium py-2 rounded-md transition"
              >
                Entrega Completada
              </button>


               {/* 🟢Generar Factura Solo si status es Entregada */}
                {sale.status === "delivered" &&  (
                   <button
                    onClick={() => markClosed(sale.id)}
                    className="w-full bg-orange-800 hover:bg-orange-900 text-white font-medium py-2 rounded-md transition"
                >
                    Generar Factura
                </button>
                )}

              <button
                onClick={() => cancelSale(sale.id)}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded-md transition"
              >
                Cancelar Venta
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
