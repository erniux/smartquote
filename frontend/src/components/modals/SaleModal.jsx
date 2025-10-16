import React from "react";

export default function SaleModal({ sale, onClose }) {
  if (!sale) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-lg w-[90vw] md:w-[70vw] max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4 border-b pb-2">
          <h2 className="text-xl font-semibold text-gray-800">
            Detalles de la Venta #{sale.id}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-gray-900 font-semibold"
          >
            ✖
          </button>
        </div>

        <p className="text-gray-700 mb-2">
          <strong>Cliente:</strong> {sale.quotation_name}
        </p>
        <p className="text-gray-700 mb-2">
          <strong>Total:</strong> ${sale.total_amount}
        </p>
        <p className="text-gray-700 mb-2">
          <strong>Estado:</strong> {sale.status}
        </p>

        {sale.invoice_pdf_url && (
          <p className="text-gray-700 mt-3">
            <strong>Factura:</strong>{" "}
            <a
              href={sale.invoice_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Ver factura
            </a>
          </p>
        )}
      </div>
    </div>
  );
}
