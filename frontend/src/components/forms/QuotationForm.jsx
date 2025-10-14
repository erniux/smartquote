import React, { useState } from "react";
import axios from "axios";
import ProductSelector from "./ProductSelector.jsx";

export default function QuotationForm({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    customer_name: "",
    customer_email: "",
    currency: "MXN",
    date: new Date().toISOString().split("T")[0],
    notes: "",
    items: [],
    expenses: [],
    status: "draft",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // --- Manejo de campos simples ---
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // --- Items dinámicos ---
  const addItem = () => {
    setFormData((prev) => ({
      ...prev,
      items: [
        ...prev.items,
        { product: "", product_name: "", unit_price: 0, quantity: 1, metal_symbol: "" },
      ],
    }));
  };

  const updateItem = (index, field, value) => {
    const items = [...formData.items];
    items[index][field] = value;
    setFormData((prev) => ({ ...prev, items }));
  };

  const removeItem = (index) => {
    const items = formData.items.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, items }));
  };

  // --- Expenses dinámicos ---
  const addExpense = () => {
    setFormData((prev) => ({
      ...prev,
      expenses: [
        ...prev.expenses,
        { name: "", category: "other", quantity: 1, unit_cost: 0 },
      ],
    }));
  };

  const updateExpense = (index, field, value) => {
    const expenses = [...formData.expenses];
    expenses[index][field] = value;
    setFormData((prev) => ({ ...prev, expenses }));
  };

  const removeExpense = (index) => {
    const expenses = formData.expenses.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, expenses }));
  };

  // --- 🧮 Calcular totales dinámicos ---
  const calculateTotals = () => {
    const subtotalItems = formData.items.reduce((acc, item) => {
      const q = parseFloat(item.quantity || 0);
      const p = parseFloat(item.unit_price || 0);
      return acc + q * p;
    }, 0);

    const subtotalExpenses = formData.expenses.reduce((acc, exp) => {
      const q = parseFloat(exp.quantity || 0);
      const c = parseFloat(exp.unit_cost || 0);
      return acc + q * c;
    }, 0);

    const subtotal = subtotalItems + subtotalExpenses;
    const iva = subtotal * 0.16;
    const total = subtotal + iva;

    return {
      subtotal: subtotal.toFixed(2),
      iva: iva.toFixed(2),
      total: total.toFixed(2),
    };
  };

  const totals = calculateTotals();

  // --- Envío del formulario ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post(
        "http://localhost:8000/api/quotations/",
        formData
      );
      setMessage("✅ Cotización creada con éxito");
      setTimeout(() => {
        onSuccess(response.data);
        onClose();
      }, 1500);
    } catch (error) {
      console.error("Error al crear cotización:", error.response?.data || error);
      setMessage("❌ Error al crear la cotización");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <form
        onSubmit={handleSubmit}
        className="bg-emerald-950 text-slate-100 p-6 rounded-2xl shadow-lg w-full max-w-2xl space-y-4 relative max-h-[90vh] overflow-y-auto border border-emerald-800"
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-white"
        >
          ✕
        </button>

        <h2 className="text-xl font-bold text-emerald-300">
          Nueva Cotización {formData.status === "draft" && "(Borrador)"}
        </h2>

        {/* Datos básicos */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300">
              Cliente:
            </label>
            <input
              type="text"
              name="customer_name"
              value={formData.customer_name}
              onChange={handleChange}
              required
              className="w-full border border-emerald-700 bg-emerald-900/40 rounded-md px-3 py-2 text-sm focus:ring-emerald-400 focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300">
              Correo electrónico:
            </label>
            <input
              type="email"
              name="customer_email"
              value={formData.customer_email}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900/40 rounded-md px-3 py-2 text-sm focus:ring-emerald-400 focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300">
              Moneda:
            </label>
            <select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900/40 rounded-md px-3 py-2 text-sm focus:ring-emerald-400 focus:border-emerald-400"
            >
              <option value="MXN">MXN</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300">
              Fecha:
            </label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900/40 rounded-md px-3 py-2 text-sm focus:ring-emerald-400 focus:border-emerald-400"
            />
          </div>
        </div>

        {/* Notas */}
        <div>
          <label className="block text-sm font-medium text-slate-300">
            Notas:
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={2}
            className="w-full border border-emerald-700 bg-emerald-900/40 rounded-md px-3 py-2 text-sm focus:ring-emerald-400 focus:border-emerald-400"
          />
        </div>

        {/* Items */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-emerald-300">
              Productos / Servicios
            </h3>
            <button
              type="button"
              onClick={addItem}
              className="text-sm text-emerald-400 hover:underline"
            >
              + Agregar producto
            </button>
          </div>

          {formData.items.map((item, i) => (
            <div
              key={i}
              className="flex flex-col bg-emerald-900/40 rounded-lg p-3 mb-2 border border-emerald-800"
            >
              <div className="flex items-center gap-2 mb-2">
                <div className="flex-1">
                  <ProductSelector
                    value={item.product}
                    currency={formData.currency}
                    onChange={(product) => {
                      updateItem(i, "product", product.id);
                      updateItem(i, "product_name", product.name);
                      updateItem(i, "unit_price", product.price || 0); 
                      updateItem(i, "metal_symbol", product.metal_symbol || "");
                    }}
                  />
                </div>

                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => updateItem(i, "quantity", e.target.value)}
                  className="w-20 border border-emerald-700 bg-emerald-900/40 rounded-md px-2 py-1 text-sm text-slate-100"
                />

                <button
                  type="button"
                  onClick={() => removeItem(i)}
                  className="text-red-400 hover:text-red-600 text-sm font-medium"
                >
                  ✕
                </button>
              </div>

              {item.product && (
                <div className="flex justify-between text-sm text-emerald-200 items-center">
                  <span className="flex items-center gap-2">
                    <strong>{item.product_name}</strong> —{" "}
                    <span className="text-emerald-300">
                      ${parseFloat(item.unit_price || 0).toLocaleString()}
                    </span>

                    {/* 🪙 Tooltip del metal */}
                    {item.metal_symbol && (
                      <span
                        title={`Precio basado en metal: ${item.metal_symbol}`}
                        className="ml-2 bg-emerald-800 text-emerald-100 text-xs px-2 py-0.5 rounded"
                      >
                        {item.metal_symbol}
                      </span>
                    )}
                  </span>

                  <span>
                    Total:{" "}
                    <strong>
                      $
                      {(
                        parseFloat(item.quantity || 0) *
                        parseFloat(item.unit_price || 0)
                      ).toLocaleString()}
                    </strong>
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Expenses */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-emerald-300">
              Gastos adicionales
            </h3>
            <button
              type="button"
              onClick={addExpense}
              className="text-sm text-emerald-400 hover:underline"
            >
              + Agregar gasto
            </button>
          </div>

          {formData.expenses.map((exp, i) => (
            <div
              key={i}
              className="grid grid-cols-5 gap-2 mb-2 bg-emerald-900/40 p-3 rounded-md border border-emerald-800"
            >
              <input
                type="text"
                placeholder="Nombre"
                value={exp.name}
                onChange={(e) => updateExpense(i, "name", e.target.value)}
                className="col-span-2 border border-emerald-700 bg-emerald-950/40 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <select
                value={exp.category}
                onChange={(e) => updateExpense(i, "category", e.target.value)}
                className="border border-emerald-700 bg-emerald-950/40 rounded-md px-2 py-1 text-sm text-slate-100"
              >
                <option value="material">Material</option>
                <option value="service">Servicio</option>
                <option value="labor">Mano de obra</option>
                <option value="other">Otro</option>
              </select>
              <input
                type="number"
                min="1"
                value={exp.quantity}
                onChange={(e) => updateExpense(i, "quantity", e.target.value)}
                className="border border-emerald-700 bg-emerald-950/40 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <input
                type="number"
                min="0"
                value={exp.unit_cost}
                onChange={(e) => updateExpense(i, "unit_cost", e.target.value)}
                className="border border-emerald-700 bg-emerald-950/40 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <button
                type="button"
                onClick={() => removeExpense(i)}
                className="text-red-400 hover:text-red-600 text-sm col-span-5 text-right"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>

        {/* 🧾 Resumen dinámico */}
        {formData.status === "draft" && (
          <div className="mt-6 border-t border-emerald-800 pt-4">
            <h3 className="text-md font-semibold text-emerald-300 mb-3">
              Resumen de Cotización (Borrador)
            </h3>

            <div className="bg-emerald-900/40 rounded-lg p-4 text-sm">
              <div className="flex justify-between mb-1">
                <span className="text-slate-300">Subtotal:</span>
                <span className="font-medium text-emerald-200">
                  ${totals.subtotal}
                </span>
              </div>

              <div className="flex justify-between mb-1">
                <span className="text-slate-300">IVA (16%):</span>
                <span className="font-medium text-emerald-200">
                  ${totals.iva}
                </span>
              </div>

              <div className="flex justify-between border-t border-emerald-800 pt-2 mt-2">
                <span className="font-semibold text-emerald-300">TOTAL:</span>
                <span className="font-bold text-emerald-400 text-lg">
                  ${totals.total}
                </span>
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-500 transition"
        >
          {loading ? "Guardando..." : "Guardar Cotización"}
        </button>

        {message && (
          <p className="text-center text-sm mt-2 text-emerald-300">{message}</p>
        )}
      </form>
    </div>
  );
}
