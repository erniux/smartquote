import React, { useEffect, useState } from "react";
import {
  getProducts,
  uploadProductCSV,
  downloadProductCSVLayout,
} from "../../api/axiosClient";
import ProductModal from "../../components/modals/ProductModal";
import { toast } from "react-toastify";
import PageContainer from "../../components/layout/PageContainer";
import { FaBoxOpen } from "react-icons/fa";


const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const fetchProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (error) {
      console.error("Error al obtener productos:", error);
      toast.error("❌ No se pudieron cargar los productos");
    } finally {
      setLoading(false);
    }
  };

  const handleCSVUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const result = await uploadProductCSV(file);
      toast.success(result.message);
      fetchProducts();
    } catch (error) {
      toast.error("❌ Error al cargar CSV");
    }
  };

  const handleDownloadLayout = async () => {
    try {
      await downloadProductCSVLayout();
      toast.success("📥 Layout descargado correctamente");
    } catch (error) {
      toast.error("❌ No se pudo descargar el layout");
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const filteredProducts = products.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
<PageContainer
actions={
    <>
      <button
        onClick={handleDownloadLayout}
        className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded-lg"
      >
        📥 Descargar Layout
      </button>

      <label className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg cursor-pointer">
        📤 Cargar CSV
        <input
          type="file"
          accept=".csv"
          onChange={handleCSVUpload}
          className="hidden"
        />
      </label>

      <button
        onClick={() => setShowModal(true)}
        className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg"
      >
        ➕ Nuevo Producto
      </button>
    </>
  }
>
      {/* Título */}
      <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">
        <FaBoxOpen className="h-8 w-8 text-emerald-600" />
        Productos
      </h1>


      {/* Lista de productos */}
      {filteredProducts.length === 0 ? (
        <p className="text-gray-400 text-center py-10">
          No hay productos registrados.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {/* Cards de productos */}
        </div>
      )}



      {/* --- Barra de búsqueda --- */}
      <div className="flex items-center gap-3 mb-6 bg-green-900 rounded-lg px-3 py-2">
        <input
          type="text"
          placeholder="🔍 Buscar producto o metal..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 bg-transparent text-white placeholder-gray-300 outline-none px-2"
        />
      </div>

      {/* --- Contenido --- */}
      {loading ? (
        <p className="text-gray-500 text-center mt-10">Cargando productos...</p>
      ) : filteredProducts.length === 0 ? (
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-400 text-lg">
            No hay productos registrados.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white border border-gray-200 shadow-sm rounded-lg overflow-hidden hover:shadow-md transition-shadow"
            >
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-40 object-cover"
                />
              ) : (
                <div className="w-full h-40 bg-gray-100 flex items-center justify-center text-gray-500 text-sm">
                  Sin imagen
                </div>
              )}

              <div className="p-4">
                <h2 className="text-lg font-semibold text-gray-800">
                  {product.name}
                </h2>
                <p className="text-sm text-gray-500 truncate">
                  {product.description || "Sin descripción"}
                </p>
                <p className="text-green-700 font-semibold mt-2">
                  💲{product.price} USD
                </p>
                <p className="text-xs text-gray-400">
                  Unidad: {product.unit || "-"} | Metal:{" "}
                  {product.metal_symbol || "-"}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* --- Modal de nuevo producto --- */}
      {showModal && (
        <ProductModal
          onClose={() => setShowModal(false)}
          onSuccess={fetchProducts}
        />
      )}
    </PageContainer>
  );
};

export default ProductsPage;
