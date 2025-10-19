import React, { useState, useEffect } from "react";
import ReportLayout from "./ReportLayout";
import { getQuotationReport } from "../../api/axiosClient";
import { toast } from "react-toastify";

const QuotationsReport = () => {
  const [quotations, setQuotations] = useState([]);
  const [status, setStatus] = useState("all");
  const [loading, setLoading] = useState(false);

  const fetchQuotations = async () => {
    try {
      setLoading(true);
      const params = status !== "all" ? { status } : {};
      const data = await getQuotationReport(params);
      setQuotations(data);
    } catch (error) {
      console.error("Error al obtener cotizaciones:", error);
      toast.error("❌ No se pudieron cargar las cotizaciones");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (quotations.length === 0) {
      toast.warning("⚠️ No hay datos para exportar");
      return;
    }

    const csvContent = [
      ["ID", "Cliente", "Fecha", "Estatus", "Total"],
      ...quotations.map((q) => [
        q.id,
        q.client_name,
        q.created_at?.slice(0, 10),
        q.status,
        q.total_price,
      ]),
    ]
      .map((e) => e.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "reporte_cotizaciones.csv";
    link.click();
  };

  useEffect(() => {
    fetchQuotations();
  }, [status]);

  return (
    <ReportLayout
      title="📑 Reporte de Cotizaciones"
      onExport={handleExport}
      filters={
        <>
          <div className="flex flex-col">
            <label className="text-sm text-gray-700">Estatus</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm"
            >
              <option value="all">Todas</option>
              <option value="draft">Borrador</option>
              <option value="confirmed">Confirmadas</option>
              <option value="cancelled">Canceladas</option>
            </select>
          </div>
          <button
            onClick={fetchQuotations}
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
              <th className="px-4 py-2"># Cotización</th>
              <th className="px-4 py-2">Cliente</th>
              <th className="px-4 py-2">Fecha</th>
              <th className="px-4 py-2">Estatus</th>
              <th className="px-4 py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {quotations.length > 0 ? (
              quotations.map((q) => (
                <tr key={q.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{q.id}</td>
                  <td className="px-4 py-2">{q.customer_name}</td>
                  <td className="px-4 py-2">
                    {new Date(q.date).toLocaleDateString("es-MX")}
                  </td>
                  <td className="px-4 py-2 capitalize">{q.status}</td>
                  <td className="px-4 py-2">
                    ${Number(q.total).toFixed(2)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="5"
                  className="text-center text-gray-400 py-4 italic"
                >
                  No se encontraron cotizaciones.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </ReportLayout>
  );
};

export default QuotationsReport;
