import React, { useState } from "react";
import { createProduct } from "../../api/axiosClient";
import { toast } from "react-toastify";

const ProductModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    margin: "",
    unit: "",
    metal_symbol: "",
  });

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createProduct(formData);
      toast.success("✅ Producto creado correctamente");
      onSuccess();
      onClose();
    } catch (error) {
      console.error(error);
      toast.error("❌ Error al crear producto");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-green-700 mb-4">Nuevo Producto</h2>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input name="name" placeholder="Nombre" onChange={handleChange} className="border p-2 w-full rounded" required />
          <textarea name="description" placeholder="Descripción" onChange={handleChange} className="border p-2 w-full rounded" />
          <input name="price" type="number" placeholder="Precio USD" onChange={handleChange} className="border p-2 w-full rounded" required />
          <input name="margin" type="number" placeholder="Margen (%)" onChange={handleChange} className="border p-2 w-full rounded" />
          <input name="unit" placeholder="Unidad" onChange={handleChange} className="border p-2 w-full rounded" />
          <input name="metal_symbol" placeholder="Símbolo del metal" onChange={handleChange} className="border p-2 w-full rounded" />

          <div className="flex justify-end gap-3 mt-4">
            <button type="button" onClick={onClose} className="bg-gray-400 hover:bg-gray-500 text-white px-3 py-1 rounded">
              Cancelar
            </button>
            <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded">
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductModal;
