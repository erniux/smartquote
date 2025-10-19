import React, { useEffect, useState } from "react";
import { getMetals } from "../../api/axiosClient";
import { toast } from "react-toastify";
import PageContainer from "../../components/layout/PageContainer";
import { MdOutlineAttachMoney } from "react-icons/md";
import MetalList from "../Metals/MetalList";


const MetalsPage = () => {
  const [metals, setMetals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCurrency, setSelectedCurrency] = useState("USD");
  const [exchangeRate, setExchangeRate] = useState(18.37); // tipo de cambio estático temporal

  const fetchMetals = async () => {
    try {
      const data = await getMetals();
      setMetals(data);
    } catch (error) {
      console.error("Error al obtener metales:", error);
      toast.error("❌ No se pudieron cargar los metales");
    } finally {
      setLoading(false);
    }
  };

  const updateExchangeRate = async () => {
  setUpdating(true);
  const randomVariation = (Math.random() * 0.2 - 0.1).toFixed(2);
  const newRate = Math.max(17.5, Math.min(19.5, exchangeRate + parseFloat(randomVariation)));
  setTimeout(() => {
    setExchangeRate(newRate);
    toast.success(`💹 Tipo de cambio actualizado: ${newRate.toFixed(2)} MXN/USD`);
    setUpdating(false);
  }, 1000);
};


  useEffect(() => {
    fetchMetals();
  }, []);

  const filteredMetals = metals.filter((m) =>
    `${m.name} ${m.symbol}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 🔁 Conversión temporal a euros (simulada)
  const convertToEUR = (usdValue) => {
    const EUR_RATE = 0.93; // solo para simulación
    return usdValue * EUR_RATE;
  };

  return (
    <PageContainer>
      {/* --- Título con ícono --- */}
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <MdOutlineAttachMoney className="h-8 w-8 text-emerald-600" />
        Metales y Divisas
      </h1>

      {/* --- Banner tipo de cambio --- */}
      <div className="flex items-center justify-between bg-emerald-700 text-white px-5 py-3 rounded-lg mb-6 shadow">
        <p className="text-sm sm:text-base font-semibold">
          💵 1 USD = {exchangeRate.toFixed(2)} MXN
        </p>
        <p className="text-xs sm:text-sm opacity-80">
          Fuente: tasa fija temporal (simulación)
        </p>
      </div>

      {/* --- Selector de divisa --- */}
      <div className="flex flex-wrap items-center justify-between mb-6">
        <div className="flex gap-4">
          {["USD", "MXN", "EUR"].map((currency) => (
            <button
              key={currency}
              onClick={() => setSelectedCurrency(currency)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCurrency === currency
                  ? "bg-emerald-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {currency === "USD" && "💲 USD"}
              {currency === "MXN" && "🇲🇽 MXN"}
              {currency === "EUR" && "💶 EUR"}
            </button>
          ))}
        </div>

        {/* Barra de búsqueda */}
        <div className="flex items-center gap-3 bg-green-900 rounded-lg px-3 py-2 mt-4 sm:mt-0">
          <input
            type="text"
            placeholder="🔍 Buscar metal o divisa..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 bg-transparent text-white placeholder-gray-300 outline-none px-2"
          />
        </div>
      </div>

      {/* --- Contenido --- */}
      {loading ? (
        <p className="text-gray-500 text-center mt-10">Cargando datos...</p>
      ) : (
        <MetalList
          metals={filteredMetals}
          selectedCurrency={selectedCurrency}
          exchangeRate={exchangeRate}
          convertToEUR={convertToEUR}
        />
      )}
    </PageContainer>
  );
};

export default MetalsPage;
