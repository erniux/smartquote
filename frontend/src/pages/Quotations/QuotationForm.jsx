import { createPortal } from "react-dom";
import React, { useState, useEffect } from "react";
import axiosClient from "../../api/axiosClient.js";
import ProductSelector from "./ProductSelector.jsx";
import { toast } from "react-toastify";
import { motion } from "framer-motion";




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



  // ================================
  // 🔁 Cargar cotización existente
  // ================================
  useEffect(() => {
    if (!quotation || !quotation.id) return;

    axios
    .get(`/quotations/${quotation.id}/`)
    .then((res) => {
      const data = res.data;

      setFormData({
        ...data,
        items: data.items || [],
        expenses: data.expenses || [],
      });
    })
    .catch((err) => {
      //setMessage("❌ No se pudo cargar la cotización");
      toast.error("❌ No se pudo cargar la cotización");

    });
    }, [quotation]);

  // ================================
  // 🧮 Calcular totales (frontend)
  // ================================
  const calculateTotals = (data) => {
    const subtotalItems = data.items.reduce(
      (sum, i) => sum + Number(i.unit_price || 0) * Number(i.quantity || 0),
      0
    );
    const subtotalExpenses = data.expenses.reduce(
      (sum, e) => sum + Number(e.total_cost || 0),
      0
    );
    const subtotal = subtotalItems + subtotalExpenses;
    const tax = subtotal * 0.16;
    const total = subtotal + tax;
    return {
      subtotal: subtotal.toFixed(2),
      tax: tax.toFixed(2),
      total: total.toFixed(2),
    };
  };

  // ================================
  // ➕ Añadir y eliminar items/expenses
  // ================================
  const addItem = () =>
    setFormData((prev) => ({
      ...prev,
      items: [...prev.items, { id: null, name: "", quantity: 1, unit_price: 0 }],
    }));

  const removeItem = (index) =>
    setFormData((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));

  const addExpense = () =>
    setFormData((prev) => ({
      ...prev,
      expenses: [
        ...prev.expenses,
        { id: null, name: "", category: "material", quantity: 1, unit_cost: 0, total_cost: 0 },
      ],
    }));

  const removeExpense = (index) =>
    setFormData((prev) => ({
      ...prev,
      expenses: prev.expenses.filter((_, i) => i !== index),
    }));

  // ================================
  // 📨 Enviar formulario
  // ================================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const url = isEditing
        ? `/quotations/${quotation.id}/`
        : "/quotations/";
      const method = isEditing ? "put" : "post";

      const totals = calculateTotals(formData);

      const payload = {
        customer_name: formData.customer_name,
        customer_email: formData.customer_email,
        currency: formData.currency,
        date: formData.date,
        notes: formData.notes,
        subtotal: totals.subtotal,
        tax: totals.tax,
        total: totals.total,
        items: formData.items.map((item) => ({
          id: item.id,
          name: item.name,
          metal_symbol: item.metal_symbol,
          price: Number(item.price || item.unit_price || 0).toFixed(2),
          quantity: Number(item.quantity || 0).toFixed(2),
          unit_price: Number(item.unit_price || 0).toFixed(2),
        })),
        expenses: formData.expenses.map((exp) => ({
          id: exp.id || null,
          name: exp.name,
          description: exp.description || "",
          category: exp.category || "other",
          quantity: Number(exp.quantity || 0).toFixed(2),
          unit_cost: Number(exp.unit_cost || 0).toFixed(2),
          total_cost: Number(exp.total_cost || 0).toFixed(2),
        })),
      };

      const response = await axiosClient[method](url, payload);
      //setMessage(isEditing ? "✅ Cotización actualizada" : "✅ Cotización creada");
      toast.success(isEditing ? "✅ Cotización actualizada" : "✅ Cotización creada");
      setTimeout(() => {
        onSuccess(response.data);
        onClose();
      }, 800);
    } catch (err) { 
      //setMessage("❌ Error al guardar cotización");
      toast.error("❌ Error al guardar cotización");
    } finally {
      setLoading(false);
    }
  };

  // ================================
  // 💬 Render del modal
  // ================================
  if (!formData) {
    return null;
 }
  console.log("🟢 Se está renderizando el modal QuotationForm");

  return (
    
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-[9999]" style={{ backdropFilter: "blur(4px)" }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.25 }}
          className="bg-emerald-900 p-8 rounded-lg text-white w-11/12 md:w-2/3 lg:w-1/2 relative shadow-2xl border border-emerald-700"
        >
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-200 hover:text-white text-xl">
          ✖
        </button>

        <h2 className="text-xl font-bold mb-4">
          {isEditing ? `Editar: ${formData.customer_name}` : "Nueva Cotización"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Cliente"
              value={formData.customer_name}
              onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
              className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-2 w-full"
            />
            <input
              type="email"
              placeholder="Correo electrónico"
              value={formData.customer_email}
              onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
              className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-2 w-full"
            />
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-2 w-full"
            />
            <input
              type="text"
              placeholder="Moneda"
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-2 w-full"
            />
          </div>

          <textarea
            placeholder="Notas"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="w-full bg-emerald-800 border border-emerald-600 rounded-md px-3 py-2 h-24"
          />

          {/* ITEMS */}
          <div>
            <h3 className="font-semibold mb-2 text-lg">Productos / Servicios</h3>
            {formData.items.map((item, index) => (
              <div key={index} className="flex items-center gap-2 mb-2">
                <ProductSelector
                  selectedProduct={item}
                  onProductSelect={(selected) => {
                    const newItems = [...formData.items];
                    newItems[index] = {
                      ...newItems[index],
                      id: selected.id,
                      name: selected.name,
                      metal_symbol: selected.metal_symbol,
                      price: selected.price,
                      unit_price: selected.price,
                    };
                    setFormData({ ...formData, items: newItems });
                  }}
                />
                <input
                  type="number"
                  placeholder="Cantidad"
                  value={item.quantity}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].quantity = e.target.value;
                    setFormData({ ...formData, items: newItems });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-1 w-1/4"
                />
                <input
                  type="number"
                  placeholder="Precio unitario"
                  value={item.unit_price}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].unit_price = e.target.value;
                    setFormData({ ...formData, items: newItems });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-1 w-1/4"
                />
                <button type="button" onClick={() => removeItem(index)} className="text-rose-400 hover:text-rose-500">✖</button>
              </div>
            ))}
            <button type="button" onClick={addItem} className="bg-emerald-700 hover:bg-emerald-600 px-3 py-1 rounded-md mt-2">
              + Agregar producto
            </button>
          </div>

          {/* EXPENSES */}
          <div>
            <h3 className="font-semibold mb-2 text-lg">Gastos adicionales</h3>
            {formData.expenses.map((exp, index) => (
              <div key={index} className="flex items-center gap-2 mb-2">
                {/* Nombre del gasto */}
                <input
                  type="text"
                  placeholder="Nombre del gasto"
                  value={exp.name}
                  onChange={(e) => {
                    const newExps = [...formData.expenses];
                    newExps[index].name = e.target.value;
                    setFormData({ ...formData, expenses: newExps });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-1 w-1/3"
                />

                {/* Categoría */}
                <select
                  value={exp.category || "other"}
                  onChange={(e) => {
                    const newExps = [...formData.expenses];
                    newExps[index].category = e.target.value;
                    setFormData({ ...formData, expenses: newExps });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-2 py-1 w-1/4 text-slate-100"
                >
                  <option value="material">Material</option>
                  <option value="labor">Mano de obra</option>
                  <option value="transport">Transporte</option>
                  <option value="other">Otro</option>
                </select>

                {/* Cantidad */}
                <input
                  type="number"
                  placeholder="Cantidad"
                  value={exp.quantity}
                  onChange={(e) => {
                    const newExps = [...formData.expenses];
                    newExps[index].quantity = e.target.value;
                    setFormData({ ...formData, expenses: newExps });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-1 w-1/5"
                />

                {/* Costo unitario */}
                <input
                  type="number"
                  placeholder="Costo unitario"
                  value={exp.unit_cost}
                  onChange={(e) => {
                    const newExps = [...formData.expenses];
                    newExps[index].unit_cost = e.target.value;
                    setFormData({ ...formData, expenses: newExps });
                  }}
                  className="bg-emerald-800 border border-emerald-600 rounded-md px-3 py-1 w-1/5"
                />

                {/* Botón eliminar */}
                <button
                  type="button"
                  onClick={() => removeExpense(index)}
                  className="text-rose-400 hover:text-rose-500"
                >
                  ✖
                </button>
              </div>
            ))}

            <button type="button" onClick={addExpense} className="bg-emerald-700 hover:bg-emerald-600 px-3 py-1 rounded-md mt-2">
              + Agregar gasto
            </button>
          </div>

          {/* SUBMIT */}
          <div className="text-center mt-6">
            <button
              type="submit"
              disabled={loading}
              className="bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded-md font-semibold text-white"
            >
              {loading ? "Guardando..." : "Guardar Cotización"}
            </button>
            {message && <p className="text-center text-sm mt-2">{message}</p>}
          </div>
        </form>
      
      </motion.div>
    </div>
  );
}
