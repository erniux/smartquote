import React, { useState, useEffect } from "react";
import axios from "axios";

export default function ProductSelector({ value, onChange, currency = "MXN" }) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

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

    const delayDebounce = setTimeout(fetchProducts, 300);
    return () => clearTimeout(delayDebounce);
  }, [query]);

  const handleSelect = async (product) => {
    setQuery(product.name);
    setShowDropdown(false);

    let finalPrice = 0;

    try {
      // ⚙️ Si el producto tiene metal_symbol, consultar su precio
      if (product.metal_symbol) {
        const res = await axios.get(
          `http://localhost:8000/api/metalprice/?symbol=${product.metal_symbol}&currency=${currency}`
        );
        if (res.data && res.data.price_local) {
          finalPrice = parseFloat(res.data.price_local);
        } else {
          console.warn("⚠ No se encontró precio para el metal:", product.metal_symbol);
        }
      } else {
        // Si no tiene metal asociado, usar su propio precio
        finalPrice = parseFloat(product.price || 0);
      }
    } catch (error) {
      console.error("Error al obtener precio del metal:", error);
      finalPrice = parseFloat(product.price || 0);
    }

    // 🔁 Devolver al formulario el producto + precio correcto
    onChange({
      id: product.id,
      name: product.name,
      metal_symbol: product.metal_symbol,
      price: finalPrice, // 👈 ahora siempre toma el precio del metal si existe
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
        className="w-full border border-emerald-700 bg-emerald-950/40 rounded-md px-2 py-1 text-sm text-slate-100"
      />
      {showDropdown && options.length > 0 && (
        <ul className="absolute z-10 bg-emerald-900 border border-emerald-700 w-full rounded-md shadow-md mt-1 max-h-40 overflow-y-auto text-sm text-slate-100">
          {options.map((p) => (
            <li
              key={p.id}
              onClick={() => handleSelect(p)}
              className="px-3 py-2 hover:bg-emerald-700 cursor-pointer"
            >
              {p.name}
              {p.metal_symbol && (
                <span className="text-xs text-emerald-300 ml-2">
                  ({p.metal_symbol})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
