import React, { useState, useEffect } from "react";
import axios from "axios";
import ProductSelector from "./ProductSelector.jsx";

export default function QuotationForm({ quotation = null, onClose, onSuccess }) {
  const isEditing = !!quotation;
  const [formData, setFormData] = useState({
    customer_name: "",
    customer_email: "",
    currency: "MXN",
    date: new Date().toISOString().split("T")[0],
    notes: "",
    items: [],
    expenses: [],
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [fetching, setFetching] = useState(false);

  // 🧩 Cargar datos actuales de la cotización al abrir modal en modo edición
  useEffect(() => {
    const fetchQuotation = async () => {
      if (!isEditing || !quotation?.id) return;
      setFetching(true);
      try {
        const res = await axios.get(`http://localhost:8000/api/quotations/${quotation.id}/`);
        const data = res.data;

        // Asegurar estructura para ProductSelector
        const preparedItems = (data.items || []).map((item) => ({
          id: item.id ?? null, // asegurar id numérico
          quantity: item.quantity,
          unit_price: item.unit_price,
          product: {
            id: item.product.id,
            name: item.product.name,
            metal_symbol: item.product.metal_symbol,
            price: item.product.price,
          },
        }));


        console.log("🧾 Items cargados desde API:", preparedItems);


        setFormData({
          customer_name: data.customer_name || "",
          customer_email: data.customer_email || "",
          currency: data.currency || "MXN",
          date: data.date || new Date().toISOString().split("T")[0],
          notes: data.notes || "",
          items: preparedItems,
          expenses: data.expenses || [],
        });
      } catch (err) {
        console.error("Error al cargar cotización:", err);
      } finally {
        setFetching(false);
      }
    };

    fetchQuotation();
  }, [isEditing, quotation?.id]);

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

      // 🧩 Asegurar estructura correcta antes de enviar
      const payload = { ...formData };

      // --- Normalizar items ---
      payload.items = formData.items.map((item) => ({
        // incluir id si existe (para actualizar), null si es nuevo
        id: item.id || null,
        product:
          typeof item.product === "object"
            ? {
                id: item.product.id,
                name: item.product.name,
                metal_symbol: item.product.metal_symbol,
                price: item.product.price,
              }
            : item.product,
        quantity: Number(item.quantity) || 1,
        unit_price:
          Number(item.unit_price) ||
          Number(item.product?.price || 0) ||
          0,
      }));

      // --- Normalizar expenses ---
      payload.expenses = formData.expenses.map((exp) => ({
        id: exp.id || null,
        name: exp.name,
        description: exp.description || "",
        category: exp.category || "other",
        quantity: Number(exp.quantity) || 1,
        unit_cost: Number(exp.unit_cost) || 0,
        total_cost:
          Number(exp.total_cost) ||
          (Number(exp.quantity) || 1) * (Number(exp.unit_cost) || 0),
      }));

      // 🧩 Enviar a la API
      const response = await axios[method](url, payload);

      setMessage(
        isEditing
          ? "✅ Cotización actualizada correctamente"
          : "✅ Cotización creada con éxito"
      );

      setTimeout(() => {
        onSuccess(response.data);
        onClose();
      }, 1200);
    } catch (error) {
      console.error("Error al guardar cotización:", error.response?.data || error);
      setMessage("❌ Error al guardar la cotización");
    } finally {
      setLoading(false);
    }
  };


  if (fetching)
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
        <div className="text-white bg-emerald-900 px-6 py-3 rounded-lg animate-pulse">
          Cargando cotización...
        </div>
      </div>
    );

  // --- Render principal ---
  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-emerald-950 text-slate-100 border border-emerald-800 p-6 rounded-2xl shadow-xl w-full max-w-2xl space-y-4 relative max-h-[90vh] overflow-y-auto"
      >
        {/* Botón cerrar */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 text-emerald-400 hover:text-emerald-200 text-lg"
        >
          ✕
        </button>

        {/* Título dinámico */}
        <h2 className="text-xl font-bold text-emerald-300 mb-3">
          {isEditing ? "Editar Cotización" : "Nueva Cotización"}
        </h2>

        {/* Datos básicos */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-emerald-200">Cliente:</label>
            <input
              type="text"
              name="customer_name"
              value={formData.customer_name}
              onChange={handleChange}
              required
              className="w-full border border-emerald-700 bg-emerald-900 rounded-md px-3 py-2 text-sm text-slate-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-200">Correo electrónico:</label>
            <input
              type="email"
              name="customer_email"
              value={formData.customer_email}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900 rounded-md px-3 py-2 text-sm text-slate-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-200">Moneda:</label>
            <select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900 rounded-md px-3 py-2 text-sm text-slate-100"
            >
              <option value="MXN">MXN</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-emerald-200">Fecha:</label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className="w-full border border-emerald-700 bg-emerald-900 rounded-md px-3 py-2 text-sm text-slate-100"
            />
          </div>
        </div>

        {/* Notas */}
        <div>
          <label className="block text-sm font-medium text-emerald-200">Notas:</label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={2}
            className="w-full border border-emerald-700 bg-emerald-900 rounded-md px-3 py-2 text-sm text-slate-100"
          />
        </div>

        {/* Items */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-emerald-300">Productos / Servicios</h3>
            <button
              type="button"
              onClick={addItem}
              className="text-sm text-emerald-400 hover:text-emerald-200"
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
                  currency={formData.currency}
                />
              </div>
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => updateItem(i, "quantity", e.target.value)}
                className="w-1/4 border border-emerald-700 bg-emerald-900 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <span className="text-xs text-emerald-400 w-1/4">
                {item.unit_price ? `$${item.unit_price}` : ""}
              </span>
              <button
                type="button"
                onClick={() => removeItem(i)}
                className="text-red-400 text-sm hover:text-red-300"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Expenses */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-emerald-300">Gastos adicionales</h3>
            <button
              type="button"
              onClick={addExpense}
              className="text-sm text-emerald-400 hover:text-emerald-200"
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
                className="col-span-2 border border-emerald-700 bg-emerald-900 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <select
                value={exp.category}
                onChange={(e) => updateExpense(i, "category", e.target.value)}
                className="border border-emerald-700 bg-emerald-900 rounded-md px-2 py-1 text-sm text-slate-100"
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
                className="border border-emerald-700 bg-emerald-900 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <input
                type="number"
                min="0"
                value={exp.unit_cost}
                onChange={(e) => updateExpense(i, "unit_cost", e.target.value)}
                className="border border-emerald-700 bg-emerald-900 rounded-md px-2 py-1 text-sm text-slate-100"
              />
              <button
                type="button"
                onClick={() => removeExpense(i)}
                className="text-red-400 text-sm hover:text-red-300 col-span-5 text-right"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-700 hover:bg-emerald-600 text-white py-2 rounded-lg font-medium transition"
        >
          {loading ? "Guardando..." : isEditing ? "Guardar Cambios" : "Guardar Cotización"}
        </button>

        {message && (
          <p className="text-center text-sm mt-2 text-emerald-300">{message}</p>
        )}
      </form>
    </div>
  );
}
