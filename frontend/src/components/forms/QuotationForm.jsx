import React, { useState } from "react";
import axios from "axios";
import ProductSelector from "./ProductSelector.jsx";

export default function QuotationForm({ quotation = null, onClose, onSuccess }) {
  const isEditing = !!quotation;

  const [formData, setFormData] = useState(
    quotation
      ? {
          customer_name: quotation.customer_name || "",
          customer_email: quotation.customer_email || "",
          currency: quotation.currency || "MXN",
          date: quotation.date || new Date().toISOString().split("T")[0],
          notes: quotation.notes || "",
          items: quotation.items || [],
          expenses: quotation.expenses || [],
        }
      : {
          customer_name: "",
          customer_email: "",
          currency: "MXN",
          date: new Date().toISOString().split("T")[0],
          notes: "",
          items: [],
          expenses: [],
        }
  );

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
      items: [...prev.items, { product: "", quantity: 1 }],
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

  // --- Envío del formulario ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const url = isEditing
        ? `http://localhost:8000/api/quotations/${quotation.id}/`
        : "http://localhost:8000/api/quotations/";
      const method = isEditing ? "put" : "post";

      const response = await axios[method](url, formData);

      setMessage(isEditing ? "✅ Cotización actualizada" : "✅ Cotización creada con éxito");

      setTimeout(() => {
        onSuccess(response.data);
        onClose();
      }, 1500);
    } catch (error) {
      console.error("Error al guardar cotización:", error.response?.data || error);
      setMessage("❌ Error al guardar la cotización");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-2xl shadow-lg w-full max-w-2xl space-y-4 relative max-h-[90vh] overflow-y-auto"
      >
        {/* Botón cerrar */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-lg"
        >
          ✕
        </button>

        {/* Título dinámico */}
        <h2 className="text-xl font-bold text-slate-800 mb-2">
          {isEditing ? "Editar Cotización" : "Nueva Cotización"}
        </h2>

        {/* Datos básicos */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-600">Cliente:</label>
            <input
              type="text"
              name="customer_name"
              value={formData.customer_name}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600">Correo electrónico:</label>
            <input
              type="email"
              name="customer_email"
              value={formData.customer_email}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600">Moneda:</label>
            <select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="MXN">MXN</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600">Fecha:</label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>

        {/* Notas */}
        <div>
          <label className="block text-sm font-medium text-slate-600">Notas:</label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={2}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        {/* Items */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-slate-700">Productos / Servicios</h3>
            <button
              type="button"
              onClick={addItem}
              className="text-sm text-emerald-600 hover:underline"
            >
              + Agregar producto
            </button>
          </div>
          {formData.items.map((item, i) => (
            <div key={i} className="flex items-center gap-2 mb-2">
              <div className="w-2/5">
                <ProductSelector
                  value={item.product}
                  onChange={(value) => updateItem(i, "product", value)}
                />
              </div>
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => updateItem(i, "quantity", e.target.value)}
                className="w-1/4 border border-gray-300 rounded-md px-2 py-1 text-sm"
              />
              <button
                type="button"
                onClick={() => removeItem(i)}
                className="text-red-500 text-sm hover:underline"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>

        {/* Expenses */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-slate-700">Gastos adicionales</h3>
            <button
              type="button"
              onClick={addExpense}
              className="text-sm text-emerald-600 hover:underline"
            >
              + Agregar gasto
            </button>
          </div>
          {formData.expenses.map((exp, i) => (
            <div key={i} className="grid grid-cols-5 gap-2 mb-2">
              <input
                type="text"
                placeholder="Nombre"
                value={exp.name}
                onChange={(e) => updateExpense(i, "name", e.target.value)}
                className="col-span-2 border border-gray-300 rounded-md px-2 py-1 text-sm"
              />
              <select
                value={exp.category}
                onChange={(e) => updateExpense(i, "category", e.target.value)}
                className="border border-gray-300 rounded-md px-2 py-1 text-sm"
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
                className="border border-gray-300 rounded-md px-2 py-1 text-sm"
              />
              <input
                type="number"
                min="0"
                value={exp.unit_cost}
                onChange={(e) => updateExpense(i, "unit_cost", e.target.value)}
                className="border border-gray-300 rounded-md px-2 py-1 text-sm"
              />
              <button
                type="button"
                onClick={() => removeExpense(i)}
                className="text-red-500 text-sm hover:underline col-span-5 text-right"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 transition"
        >
          {loading ? "Guardando..." : isEditing ? "Guardar Cambios" : "Guardar Cotización"}
        </button>

        {message && (
          <p className="text-center text-sm mt-2 text-slate-600">{message}</p>
        )}
      </form>
    </div>
  );
}
