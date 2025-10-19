import React, { useContext, useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  FaClipboardList,
  FaShoppingCart,
  FaBoxes,
  FaChartBar,
  FaTimes,
  FaSignOutAlt,
  FaBoxOpen,
  FaChevronDown,
  FaChevronUp,
  FaFileInvoiceDollar,
  FaFileAlt,
} from "react-icons/fa";
import { AuthContext } from "../../context/AuthContext";

const Sidebar = ({ onClose }) => {
  const { logout } = useContext(AuthContext);
  const location = useLocation();

  // Estado del submenú Reportes
  const [openReports, setOpenReports] = useState(false);

  // 🔁 Detectar si la ruta actual pertenece a /reports/
  useEffect(() => {
    if (location.pathname.startsWith("/reports")) {
      setOpenReports(true);
    }
  }, [location.pathname]);

  const menu = [
    { name: "Cotizaciones", icon: <FaClipboardList />, path: "/quotations" },
    { name: "Ventas", icon: <FaShoppingCart />, path: "/sales" },
    { name: "Metales", icon: <FaBoxes />, path: "/metals" },
    { name: "Productos", icon: <FaBoxOpen />, path: "/products" },
  ];

  return (
    <aside className="flex flex-col h-full w-64 p-4 bg-gray-900 text-white">
      {/* Header móvil */}
      <div className="flex justify-between items-center md:hidden mb-4">
        <h2 className="text-lg font-semibold text-green-400">Menú</h2>
        <button onClick={onClose}>
          <FaTimes size={20} />
        </button>
      </div>

      {/* Navegación principal */}
      <nav className="flex-1 space-y-2">
        {menu.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg transition-colors duration-200 ${
                isActive
                  ? "bg-green-600 text-white"
                  : "text-gray-200 hover:bg-gray-700 hover:text-white"
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.name}</span>
          </NavLink>
        ))}

        {/* Sección Reportes con submenú */}
        <div className="space-y-1">
          <button
            onClick={() => setOpenReports(!openReports)}
            className="flex items-center justify-between w-full px-4 py-2 rounded-lg text-gray-200 hover:bg-gray-700 hover:text-white transition-colors"
          >
            <span className="flex items-center gap-3">
              <FaChartBar className="text-lg" />
              <span>Reportes</span>
            </span>
            {openReports ? (
              <FaChevronUp className="text-sm" />
            ) : (
              <FaChevronDown className="text-sm" />
            )}
          </button>

          {/* Submenú desplegable con animación */}
          <div
            className={`ml-8 mt-1 space-y-1 overflow-hidden transition-all duration-300 ease-in-out ${
              openReports ? "max-h-32 opacity-100" : "max-h-0 opacity-0"
            }`}
          >
            <NavLink
              to="/reports/quotations"
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-1 rounded-lg transition-colors duration-200 ${
                  isActive
                    ? "bg-green-600 text-white"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white"
                }`
              }
            >
              <FaFileAlt className="text-sm" />
              <span>Cotizaciones</span>
            </NavLink>
            
            <NavLink
              to="/reports/sales"
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-1 rounded-lg transition-colors duration-200 ${
                  isActive
                    ? "bg-green-600 text-white"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white"
                }`
              }
            >
              <FaFileInvoiceDollar className="text-sm" />
              <span>Ventas</span>
            </NavLink>

            
          </div>
        </div>
      </nav>

      {/* Botón de logout */}
      <div className="border-t border-gray-700 pt-4 mt-4">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-4 py-2 rounded-lg text-gray-300 hover:bg-red-600 hover:text-white transition-colors"
        >
          <FaSignOutAlt className="text-lg" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
