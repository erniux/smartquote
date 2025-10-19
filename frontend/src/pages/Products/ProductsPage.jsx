import React, { useEffect, useState } from "react";
import { getProducts } from "../../api/axiosClient";
import { toast } from "react-toastify";

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <p className="text-gray-500 text-center mt-10">Cargando productos...</p>
    );
  }

  if (products.length === 0) {
    return (
      <p className="text-gray-400 text-center mt-10">
        No hay productos registrados.
      </p>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-green-700 mb-6">Productos</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <div
            key={product.id}
            className="bg-white shadow-md rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
          >
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-40 object-cover"
              />
            ) : (
              <div className="w-full h-40 bg-gray-200 flex items-center justify-center text-gray-500 text-sm">
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
                Unidad: {product.unit || "-"} | Metal: {product.metal_symbol || "-"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductsPage;
