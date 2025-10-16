import React, { useState, useEffect } from "react";
import axios from "axios";

export default function ProductSelector({ selectedProduct, onProductSelect, currency = "MXN" }) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [price, setPrice] = useState(null);

  // ✅ Mostrar el producto actual cuando se edita
  useEffect(() => {
    if (selectedProduct && selectedProduct.name) {
      setQuery(selectedProduct.name);
      setPrice(selectedProduct.price || selectedProduct.unit_price || null);
    }
  }, [selectedProduct]);

  // 🔍 Buscar productos por nombre
  useEffect(() => {
    const fetchProducts = async () => {
      if (query.length < 2) {
        setOptions([]);
        return;
      }
      try {
        const response = await axios.get(
          `http://localhost:8000/api/products/?search=${query}`
        );
        setOptions(response.data);
      } catch (error) {
        console.error("Error al buscar productos:", error);
      }
    };

    const delay = setTimeout(fetchProducts, 300);
    return () => clearTimeout(delay);
  }, [query]);

  // 🧮 Al seleccionar producto, obtener precio del metal
  const handleSelect = async (product) => {
    setQuery(product.name);
    setShowDropdown(false);

    let finalPrice = Number(product.price) || 0;

    try {
      if (product.metal_symbol) {
        const res = await axios.get(
          `http://localhost:8000/api/metalprice/?symbol=${product.metal_symbol}&currency=${currency}`
        );
        if (res.data && res.data.price_local) {
          finalPrice = Number(res.data.price_local);
        }
      }
    } catch (error) {
      console.error("Error al obtener precio del metal:", error);
    }

    // 💰 Actualizamos el estado local
    setPrice(finalPrice);

    // 📤 Propagamos todo hacia arriba (incluye unit_price)
    onProductSelect({
      id: product.id,
      name: product.name,
      metal_symbol: product.metal_symbol,
      price: finalPrice,
      unit_price: finalPrice, // <- sincroniza automáticamente
    });
  };


  return (
    <div className="relative w-full">
      <input
        type="text"
        placeholder="Buscar producto..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setShowDropdown(true);
        }}
        onFocus={() => setShowDropdown(true)}
        className="w-full border border-emerald-700 bg-emerald-900/60 rounded-md px-2 py-1 text-sm text-slate-100 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500"
      />

      {/* 🔻 Lista de resultados */}
      {showDropdown && options.length > 0 && (
        <ul className="absolute z-20 bg-emerald-950 border border-emerald-700 w-full rounded-md shadow-md mt-1 max-h-40 overflow-y-auto text-sm text-slate-100">
          {options.map((p) => (
            <li
              key={p.id}
              onClick={() => handleSelect(p)}
              className="px-3 py-2 hover:bg-emerald-700 cursor-pointer flex justify-between items-center"
            >
              <span>
                {p.name}
                {p.metal_symbol && (
                  <span className="text-xs text-emerald-300 ml-2">
                    ({p.metal_symbol})
                  </span>
                )}
              </span>
              <span className="text-xs text-emerald-400">
                ${parseFloat(p.price).toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
      )}

      {/* 💰 Mostrar precio del metal seleccionado */}
      {price !== null && price !== undefined && (
        <p className="text-xs text-emerald-300 mt-1">
          Precio actual del metal: $
          {Number(price).toFixed(2)} {currency}
        </p>
      )}

    </div>
  );
}
