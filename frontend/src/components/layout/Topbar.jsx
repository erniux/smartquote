import React, { useContext, useEffect, useState } from "react";
import { FaUserCircle, FaSignOutAlt } from "react-icons/fa";
import { AuthContext } from "../../context/AuthContext";
import { getMetalPrices, updateMetalPrices } from "../../api/axiosClient";
import { ArrowPathIcon } from "@heroicons/react/24/outline";
import { toast } from "react-toastify";

// ✨ Para animaciones suaves de cambio de valor
import { motion, AnimatePresence } from "framer-motion";

const Topbar = ({ user, logo }) => {
  const { logout } = useContext(AuthContext);
  const [prices, setPrices] = useState({});
  const [timestamp, setTimestamp] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPrices = async (updateDB = false) => {
  try {
    setLoading(true);

    const data = await getMetalPrices();

    // 🧠 Guardamos los precios anteriores para detectar subidas/bajadas
    setPrices((prev) => {
      const next = { ...data.prices, _previous: prev };
      return next;
    });

    setTimestamp(data.timestamp || null);
    toast.success("✅ Precios obtenidos correctamente");

    if (updateDB) {
      await updateMetalPrices();
      toast.info("📦 Base de datos actualizada con nuevos precios");
    }
  } catch (error) {
    console.error("Error al obtener precios:", error);
    toast.error("❌ Error al actualizar precios");
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    fetchPrices();
  }, []);

  return (
    <div className="w-full bg-white shadow-md sticky top-0 z-40">
      {/* --- Sección superior: logo y usuario --- */}
      <div className="flex items-center justify-between px-6 py-3 border-b">
        <div className="flex items-center gap-2">
          {logo ? (
            <img src={logo} alt="Logo" className="h-10 w-auto object-contain" />
          ) : (
            <h1 className="text-xl font-bold text-green-700">SmartQuote</h1>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <FaUserCircle className="text-2xl text-gray-600" />
            <div className="text-sm text-slate-600">
              <p className="font-medium">{user?.name || "Usuario"}</p>
              <p className="text-gray-400 text-xs">
                {user?.email || "sin correo"}
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            title="Cerrar sesión"
            className="text-gray-600 hover:text-green-700 transition-colors"
          >
            <FaSignOutAlt className="text-xl" />
          </button>
        </div>
      </div>

      {/* --- Sección inferior: precios y botón --- */}
      <div className="flex flex-col md:flex-row items-center justify-between px-6 py-2 bg-gray-800 text-white shadow-inner overflow-hidden relative">

        {/* 🪙 Cinta de precios tipo carrusel */}
        <div className="relative flex-1 overflow-hidden">
          {/* Gradientes a los lados */}
          <div className="absolute left-0 top-0 h-full w-10 bg-gradient-to-r from-gray-800 to-transparent z-10" />
          <div className="absolute right-0 top-0 h-full w-10 bg-gradient-to-l from-gray-800 to-transparent z-10" />

          {/* Carrusel infinito */}
          <motion.div
            className="flex gap-8 whitespace-nowrap"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 40, ease: "linear", repeat: Infinity }}
          >
            {[...Array(2)].map((_, i) => (
              <div key={i} className="flex gap-8 px-2">
                {Object.entries(prices).map(([metal, value]) => {
                  const previousValue = prices._previous?.[metal];
                  const displayValue =
                  typeof value === "number" && !isNaN(value)
                    ? value.toFixed(2)
                    : "—";
                  let color = "#ffffff";

                  if (previousValue !== undefined) {
                    if (value > previousValue) color = "#22c55e"; // verde
                    else if (value < previousValue) color = "#ef4444"; // rojo
                  }

                  return (
                    <motion.span
                      key={metal + i}
                      className="text-sm min-w-[90px] text-center"
                      style={{ color }}
                      initial={{ opacity: 0.5 }}
                      animate={{ opacity: 1, color: "#ffffff" }}
                      transition={{ duration: 1.5, delay: 1 }}
                    >
                       <strong>{metal}:</strong> {displayValue}
                    </motion.span>
                  );
                })}
              </div>
            ))}
          </motion.div>
        </div>

        {/* 🔄 Sección del botón y la fecha */}
        <div className="flex items-center gap-4 mt-2 md:mt-0 ml-4">
          {timestamp && (
            <p className="text-xs text-gray-300 italic">
              Última actualización:{" "}
              {new Date(timestamp).toLocaleString("es-MX")}
            </p>
          )}

          <button
            onClick={() => fetchPrices(true)}
            disabled={loading}
            className={`flex items-center px-3 py-1 rounded-lg ${
              loading ? "bg-gray-500" : "bg-green-600 hover:bg-green-700"
            } transition-colors`}
          >
            <ArrowPathIcon
              className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
            />
            {loading ? "Actualizando..." : "Actualizar precios"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
