import React from "react";
import { XMarkIcon, DocumentTextIcon } from "@heroicons/react/24/outline";

export default function QuotationModal({ quotation, onClose }) {
  if (!quotation) return null;

  const subtotal = parseFloat(quotation.subtotal || 0);
  const iva = subtotal * 0.16;
  const total = parseFloat(quotation.total || 0);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative animate-fade-in overflow-y-auto max-h-[90vh]">
        {/* Botón cerrar */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition"
        >
          <XMarkIcon className="w-6 h-6" />
        </button>

        {/* Título */}
        <div className="flex items-center gap-2 mb-4">
          <DocumentTextIcon className="w-6 h-6 text-emerald-600" />
          <h2 className="text-xl font-bold text-slate-800">
            Detalles de la Cotización
          </h2>
        </div>

        {/* Información general */}
        <div className="space-y-1 text-sm text-slate-700 mb-4">
          <p>
            <span className="font-semibold">Cliente:</span>{" "}
            {quotation.customer_name}
          </p>
          <p>
            <span className="font-semibold">Correo:</span>{" "}
            {quotation.customer_email || "No especificado"}
          </p>
          <p>
            <span className="font-semibold">Moneda:</span> {quotation.currency}
          </p>
          <p>
            <span className="font-semibold">Fecha:</span> {quotation.date}
          </p>
        </div>

        <hr className="my-3" />

        {/* 🧾 Productos / Servicios */}
        <h3 className="text-sm font-semibold text-slate-600 mb-2">
          Productos / Servicios
        </h3>

        {quotation.items && quotation.items.length > 0 ? (
          <table className="w-full text-sm text-left border-collapse mb-6">
            <thead>
              <tr className="bg-slate-100 text-slate-700">
                <th className="px-3 py-2">Producto</th>
                <th className="px-3 py-2 text-center">Cant.</th>
                <th className="px-3 py-2 text-right">P. Unitario</th>
                <th className="px-3 py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {quotation.items.map((item) => {
                const totalItem =
                  parseFloat(item.unit_price || 0) *
                  parseFloat(item.quantity || 1);
                return (
                  <tr
                    key={item.id}
                    className="border-b border-slate-200 hover:bg-slate-50"
                  >
                    <td className="px-3 py-2">{item.product_name}</td>
                    <td className="px-3 py-2 text-center">
                      {item.quantity || 1}
                    </td>
                    <td className="px-3 py-2 text-right">
                      ${parseFloat(item.unit_price).toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                      })}
                    </td>
                    <td className="px-3 py-2 text-right font-medium">
                      ${totalItem.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p className="text-slate-400 text-sm mb-4">Sin productos.</p>
        )}

        {/* 🧾 Gastos adicionales */}
        <h3 className="text-sm font-semibold text-slate-600 mb-2">
          Gastos Adicionales
        </h3>

        {quotation.expenses && quotation.expenses.length > 0 ? (
          <table className="w-full text-sm text-left border-collapse mb-6">
            <thead>
              <tr className="bg-slate-100 text-slate-700">
                <th className="px-3 py-2">Concepto</th>
                <th className="px-3 py-2 text-center">Cant.</th>
                <th className="px-3 py-2 text-right">P. Unitario</th>
                <th className="px-3 py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {quotation.expenses.map((exp) => (
                <tr
                  key={exp.id}
                  className="border-b border-slate-200 hover:bg-slate-50"
                >
                  <td className="px-3 py-2">
                    {exp.name}{" "}
                    <span className="text-slate-400 text-xs">
                      ({exp.category})
                    </span>
                  </td>
                  <td className="px-3 py-2 text-center">{exp.quantity}</td>
                  <td className="px-3 py-2 text-right">
                    ${parseFloat(exp.unit_cost).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                    })}
                  </td>
                  <td className="px-3 py-2 text-right font-medium">
                    ${parseFloat(exp.total_cost).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-slate-400 text-sm mb-4">Sin gastos adicionales.</p>
        )}

        <hr className="my-3" />

        {/* Totales */}
        <div className="text-right space-y-1 text-sm">
          <p className="text-slate-600">
            Subtotal:{" "}
            <span className="font-medium text-slate-800">
              ${subtotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </p>
          <p className="text-slate-600">
            IVA:{" "}
            <span className="font-medium text-slate-800">
              ${iva.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </p>
          <p className="text-lg font-bold text-emerald-700">
            Total: ${total.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>
    </div>
  );
}
