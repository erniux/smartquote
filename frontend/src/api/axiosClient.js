import axios from "axios";

// 🧱 Configuración base del cliente Axios
const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/",
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

// Crear producto
export const createProduct = async (productData) => {
  const response = await axiosClient.post("products/", productData);
  return response.data;
};

// Descargar layout CSV
export const downloadProductCSVLayout = async () => {
  const response = await axiosClient.get("products/csv_layout/", {
    responseType: "blob", // 👈 importante: descarga como archivo
  });

  // Crea un enlace temporal para forzar la descarga
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "productos_layout.csv");
  document.body.appendChild(link);
  link.click();
  link.remove();
};

// Subir CSV
export const uploadProductCSV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axiosClient.post("products/upload_csv/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;

};

// ✅ Obtener lista de metales
export const getMetals = async () => {
  try {
    const response = await axiosClient.get("metals/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener metales:", error);
    throw error;
  }
};

// 🔹 Obtener reporte de cotizaciones con filtros
export const getQuotationReport = async (params = {}) => {
  const response = await axiosClient.get("quotations/", { params });
  return response.data;
};

// 🔹 Obtener reporte de ventas con filtros
export const getSalesReport = async (params = {}) => {
  const response = await axiosClient.get("sales/", { params });
  return response.data;
};




export default axiosClient;
