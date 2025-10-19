import React, { useState, useEffect } from "react";
import ReportLayout from "./ReportLayout";
import { getSalesReport } from "../../api/axiosClient";
import { toast } from "react-toastify";

const SalesReport = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [status, setStatus] = useState("");

  const fetchSales = async () => {
    try {
      setLoading(true);
      const data = await getSalesReport({
        start: startDate,
        end: endDate,
      });
      setSales(data);
    } catch (error) {
      console.error("Error al obtener ventas:", error);
      toast.error("❌ No se pudieron cargar las ventas");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (sales.length === 0) {
      toast.warning("⚠️ No hay datos para exportar");
      return;
    }

    const csvContent = [
      ["ID", "Cliente", "Fecha", "Status", "Total"],
      ...sales.map((s) => [
        s.id,
        s.quotation_name,
        s.sale_date || s.created_at,
        s.status,
        s.total_amount || s.total,
      ]),
    ]
      .map((e) => e.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "reporte_ventas.csv";
    link.click();
  };

  useEffect(() => {
    fetchSales();
  }, [startDate, endDate]);

  return (
    <ReportLayout
      title="📈 Reporte de Ventas"
      onExport={handleExport}
      filters={
        <>
          <div className="flex flex-col">
            <label className="text-sm text-gray-700">Desde</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="border border-gray-300 bg-white text-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-sm text-gray-700">Hasta</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="border border-gray-300 bg-white text-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
            />
          </div>
          <button
            onClick={fetchSales}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
          >
            Filtrar
          </button>
        </>
      }
    >
      {loading ? (
        <p className="text-center text-gray-500 py-4">Cargando datos...</p>
      ) : (
        <table className="w-full text-sm text-left border-collapse">
          <thead className="bg-emerald-700 text-white">
            <tr>
              <th className="px-4 py-2">ID Venta</th>
              <th className="px-4 py-2">Cliente</th>
              <th className="px-4 py-2">Fecha</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {sales.length > 0 ? (
              sales.map((sale) => (
                <tr key={sale.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{sale.id}</td>
                  <td className="px-4 py-2">{sale.quotation_name}</td>
                  <td className="px-4 py-2">
                    {new Date(
                      sale.sale_date || sale.created_at
                    ).toLocaleDateString("es-MX")}
                  </td>
                  <td className="px-4 py-2">{sale.status}</td>
                  <td className="px-4 py-2">
                    ${Number(sale.total_amount || sale.total_price || 0).toFixed(2)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="4"
                  className="text-center text-gray-400 py-4 italic"
                >
                  No se encontraron ventas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </ReportLayout>
  );
};

export default SalesReport;
