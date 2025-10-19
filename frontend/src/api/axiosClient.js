import axios from "axios";

// 🧱 Configuración base del cliente Axios
const axiosClient = axios.create({
  baseURL: "http://localhost:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
});

// 🧠 Interceptor: agrega el token JWT automáticamente a cada request
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ 1. Obtener precios actuales (sin actualizar BD)
export const getMetalPrices = async () => {
  try {
    const response = await axiosClient.get("get_yfinance_prices/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener precios:", error);
    throw error;
  }
};

// ✅ 2. Actualizar precios en la base de datos
export const updateMetalPrices = async () => {
  try {
    const response = await axiosClient.post("update_prices/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al actualizar precios:", error);
    throw error;
  }
};

// ✅ Obtener lista de productos
export const getProducts = async () => {
  const response = await axiosClient.get("products/");
  return response.data;
};

export default axiosClient;
