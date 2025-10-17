import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import { toast } from "react-toastify";
import { motion } from "framer-motion";

export default function LoginPage() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      toast.success("✅ Bienvenido de nuevo!");
      navigate("/quotations");
    } else {
      toast.error("❌ Usuario o contraseña incorrectos");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-900 via-emerald-800 to-emerald-900 text-white overflow-hidden">
      {/* Contenedor animado */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="bg-emerald-800 bg-opacity-90 p-10 rounded-3xl shadow-2xl w-[380px] border border-emerald-700"
      >
        {/* Encabezado */}
        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.7 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white tracking-wide">SmartQuote</h1>
          <p className="text-emerald-200 text-sm mt-2">
            Sistema de cotizaciones y ventas
          </p>
        </motion.div>

        {/* Formulario */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="space-y-5"
        >
          <div>
            <label className="block text-sm text-emerald-200 mb-1">Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 rounded-md bg-emerald-700 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 outline-none text-white placeholder-emerald-300"
              placeholder="Tu usuario"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-emerald-200 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-md bg-emerald-700 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 outline-none text-white placeholder-emerald-300"
              placeholder="••••••••"
              required
            />
          </div>

          <motion.button
            type="submit"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-emerald-900 font-semibold py-3 rounded-md transition-all duration-200"
          >
            Iniciar sesión
          </motion.button>
        </motion.form>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center mt-8 text-sm text-emerald-300"
        >
          <p>© {new Date().getFullYear()} SmartQuote</p>
        </motion.div>
      </motion.div>
    </div>
  );
}
