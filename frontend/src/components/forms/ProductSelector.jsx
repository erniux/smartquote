import React, { useState, useEffect } from "react";
import axios from "axios";

export default function ProductSelector({ value, onChange }) {
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

    const handleSelect = (product) => {
    onChange(product); // ahora enviamos el objeto completo
    setQuery(product.name);
    setShowDropdown(false);
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
        className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm focus:ring-green-500 focus:border-green-500"
      />
      {showDropdown && options.length > 0 && (
        <ul className="absolute z-10 bg-white border border-gray-200 w-full rounded-md shadow-md mt-1 max-h-40 overflow-y-auto text-sm">
          {options.map((p) => (
            <li
              key={p.id}
              onClick={() => handleSelect(p)}
              className="px-3 py-2 hover:bg-emerald-50 cursor-pointer"
            >
              {p.name}
              {p.metal_symbol && (
                <span className="text-xs text-slate-400 ml-2">
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
