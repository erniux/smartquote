import React from "react";

export default function InvoiceModal({ invoiceUrl, onClose }) {
  if (!invoiceUrl) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-[90vw] md:w-[70vw] h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-4 bg-emerald-900 text-white">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            🧾 Factura emitida
          </h2>
          <button
            onClick={onClose}
            className="text-white bg-emerald-700 hover:bg-emerald-600 px-3 py-1 rounded-md transition"
          >
            Cerrar
          </button>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 bg-gray-100">
          <iframe
            src={invoiceUrl}
            title="Factura PDF"
            width="100%"
            height="100%"
            className="border-none"
          ></iframe>
        </div>
      </div>
    </div>
  );
}
