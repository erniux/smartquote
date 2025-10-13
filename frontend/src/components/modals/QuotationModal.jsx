import React from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";

export default function QuotationModal({ quotation, onClose }) {
  if (!quotation) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 relative animate-fade-in">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>

        <h2 className="text-2xl font-bold text-slate-800 mb-4">
          🧾 Detalles de la Cotización
        </h2>

        <div className="text-sm text-gray-600 space-y-1">
          <p><strong>Cliente:</strong> {quotation.customer_name}</p>
          <p><strong>Correo:</strong> {quotation.customer_email || "No registrado"}</p>
          <p><strong>Moneda:</strong> {quotation.currency}</p>
          <p><strong>Fecha:</strong> {quotation.date}</p>
        </div>

        <hr className="my-4" />

        <h3 className="font-semibold text-slate-700 mb-2">Productos / Servicios</h3>
        <ul className="space-y-2">
          {quotation.items?.map((item) => (
            <li key={item.id} className="border p-2 rounded-md text-sm flex justify-between">
              <span>{item.product_name}</span>
              <span className="font-semibold">${parseFloat(item.unit_price).toLocaleString()}</span>
            </li>
          ))}
        </ul>

        <hr className="my-4" />

        <div className="text-right">
          <p className="text-sm text-gray-500">Subtotal: ${parseFloat(quotation.subtotal).toLocaleString()}</p>
          <p className="text-sm text-gray-500">IVA: {quotation.tax}%</p>
          <p className="text-lg font-semibold text-emerald-700">
            Total: ${parseFloat(quotation.total).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
