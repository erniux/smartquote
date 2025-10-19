import React from "react";
import CountUp from "react-countup";
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from "@heroicons/react/24/solid";

const MetalList = ({ metals, selectedCurrency, exchangeRate, convertToEUR }) => {
  if (!metals || metals.length === 0) {
    return (
      <p className="text-gray-400 text-center mt-10">
        No hay metales registrados.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {metals.map((metal) => {
        const usdValue = Number(metal.price_usd);

        // 🔁 Conversión según moneda seleccionada
        let displayValue = usdValue;
        if (selectedCurrency === "MXN") displayValue = usdValue * exchangeRate;
        if (selectedCurrency === "EUR") displayValue = convertToEUR(usdValue);

        // 📈 Calcular si subió o bajó (solo referencia visual)
        const priceChange = displayValue - usdValue;
        const isUp = priceChange > 0.01;
        const isDown = priceChange < -0.01;

        return (
          <div
            key={metal.symbol}
            className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition"
          >
            {/* --- Encabezado --- */}
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-800">
                {metal.name || metal.symbol}
              </h2>
              <span className="text-gray-400 text-sm capitalize">
                {metal.type === "currency" ? "💵 Divisa" : "🪙 Metal"}
              </span>
            </div>

            {/* --- Precio animado con flechas --- */}
            <div className="flex items-center gap-2 mt-2">
              <p className="text-emerald-700 font-bold text-xl">
                💲
                <CountUp
                  end={displayValue}
                  decimals={2}
                  duration={0.8}
                  separator=","
                />
                <span className="text-gray-500 text-sm font-medium ml-1">
                  {selectedCurrency}
                </span>
              </p>

              {/* Indicadores de tendencia */}
              {isUp && (
                <ArrowTrendingUpIcon className="h-5 w-5 text-green-500 animate-bounce" />
              )}
              {isDown && (
                <ArrowTrendingDownIcon className="h-5 w-5 text-red-500 animate-pulse" />
              )}
            </div>

            {/* --- Cantidad base y unidad --- */}
            <p className="text-gray-600 font-medium text-sm mt-1">
              {metal.base_quantity || 1} {metal.measure_units || ""}
            </p>

            {/* --- Fecha de actualización --- */}
            <p className="text-xs text-gray-400 mt-1">
              Actualizado:{" "}
              {metal.last_updated
                ? new Date(metal.last_updated).toLocaleString("es-MX")
                : "—"}
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default MetalList;
