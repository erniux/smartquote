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
  const [loading, setLoading] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotMessage, setForgotMessage] = useState(null);
  const [forgotError, setForgotError] = useState(null);

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

    const PASSWORD_RESET_ENDPOINT = "http://localhost:8000/api/auth/password-reset/"; 
  // 🔁 Ajusta esta URL a tu endpoint real

  const handleForgotPassword = async (e) => {
    e.preventDefault();

    setForgotMessage(null);
    setForgotError(null);

    if (!forgotEmail) {
      setForgotError("Por favor ingresa tu correo.");
      return;
    }

    setForgotLoading(true);
    try {
      const response = await fetch(PASSWORD_RESET_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: forgotEmail }),
      });

      if (!response.ok) {
        throw new Error("Error en la solicitud");
      }

      setForgotMessage(
        "Si el correo existe en el sistema, recibirás un enlace para restablecer tu contraseña."
      );
      toast.success("📧 Revisa tu bandeja de correo.");
      setForgotEmail("");
    } catch (error) {
      console.error("Error al solicitar reset de contraseña:", error);
      setForgotError("Ocurrió un error al enviar la solicitud. Intenta de nuevo.");
      toast.error("❌ No se pudo enviar el correo de recuperación.");
    } finally {
      setForgotLoading(false);
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
                    <div className="mt-3 text-center">
            <button
              type="button"
              onClick={() => setShowForgot(!showForgot)}
              className="text-emerald-200 hover:text-emerald-100 text-xs underline"
            >
              {showForgot ? "Cerrar recuperación" : "¿Olvidaste tu contraseña?"}
            </button>
          </div>
                  {showForgot && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-6 p-4 rounded-2xl bg-emerald-900/60 border border-emerald-700"
          >
            <h2 className="text-sm font-semibold text-emerald-100">
              Recuperar contraseña
            </h2>
            <p className="text-xs text-emerald-200 mt-1">
              Ingresa tu correo y te enviaremos un enlace para restablecer tu contraseña.
            </p>

            <form onSubmit={handleForgotPassword} className="mt-3 space-y-3">
              <div>
                <label className="block text-xs text-emerald-200 mb-1">
                  Correo electrónico
                </label>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  className="w-full p-2.5 rounded-md bg-emerald-700 border border-emerald-600 focus:ring-2 focus:ring-emerald-400 outline-none text-white placeholder-emerald-300 text-sm"
                  placeholder="tu@correo.com"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full bg-emerald-500 hover:bg-emerald-400 text-emerald-900 font-semibold py-2.5 rounded-md transition-all duration-200 text-sm"
                disabled={forgotLoading}
              >
                {forgotLoading ? "Enviando..." : "Enviar enlace de recuperación"}
              </button>
            </form>

            {forgotMessage && (
              <p className="mt-2 text-xs text-emerald-200">{forgotMessage}</p>
            )}
            {forgotError && (
              <p className="mt-2 text-xs text-red-300">{forgotError}</p>
            )}
          </motion.div>
        )}

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
