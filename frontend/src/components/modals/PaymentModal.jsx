import React, { useState } from "react";

export default function PaymentModal({ sale, onClose, onSave }) {
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState("transfer");
  const [note, setNote] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      alert("Por favor ingresa un monto válido");
      return;
    }
    onSave({
      amount: parseFloat(amount),
      method,
      note,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-emerald-900 text-white rounded-2xl shadow-lg border border-emerald-700 p-6 w-[400px] max-h-[90vh] overflow-y-auto animate-fadeIn">
        <h2 className="text-xl font-semibold mb-4 text-center">
          💰 Registrar pago — Venta #{sale.id}
        </h2>

        {/* 🧾 Historial de pagos */}
        {sale.payments && sale.payments.length > 0 ? (
          <div className="bg-emerald-800 rounded-lg p-3 mb-5 border border-emerald-700">
            <h3 className="text-sm font-semibold text-emerald-300 mb-2">
              Historial de pagos:
            </h3>
            <ul className="space-y-2 text-sm">
              {sale.payments.map((pago, idx) => (
                <li
                  key={idx}
                  className="flex justify-between items-center bg-emerald-950/40 px-3 py-2 rounded-md"
                >
                  <div>
                    <p className="font-medium text-emerald-100">
                      ${parseFloat(pago.amount).toLocaleString()}
                    </p>
                    <p className="text-xs text-emerald-300">
                      {new Date(pago.payment_date).toLocaleDateString()} —{" "}
                      {pago.method === "transfer"
                        ? "Transferencia"
                        : pago.method === "cash"
                        ? "Efectivo"
                        : "Crédito"}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-sm text-emerald-200 italic mb-4 text-center">
            No hay pagos registrados aún.
          </p>
        )}

        {/* 💳 Formulario nuevo pago */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Monto</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full p-2 rounded-md bg-emerald-800 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 focus:outline-none text-white"
              placeholder="Ej. 1500.00"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Método de pago</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full p-2 rounded-md bg-emerald-800 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 focus:outline-none text-white"
            >
              <option value="transfer">Transferencia</option>
              <option value="cash">Efectivo</option>
              <option value="credit">Crédito</option>
            </select>
          </div>

          <div>
            <label className="block text-sm mb-1">Notas (opcional)</label>
            <textarea
              rows="2"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full p-2 rounded-md bg-emerald-800 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 focus:outline-none text-white text-sm"
              placeholder="Detalles o comentarios..."
            />
          </div>

          <div className="flex justify-end gap-3 mt-5">
            <button
              type="button"
              onClick={onClose}
              className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-2 rounded-md text-sm transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="bg-emerald-400 hover:bg-emerald-300 text-emerald-900 font-semibold px-4 py-2 rounded-md text-sm transition"
            >
              Guardar Pago
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
