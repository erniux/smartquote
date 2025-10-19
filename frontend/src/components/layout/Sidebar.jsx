import React, { useContext } from "react";
import { NavLink } from "react-router-dom";
import {
  FaClipboardList,
  FaShoppingCart,
  FaFileInvoiceDollar,
  FaBoxes,
  FaChartBar,
  FaTimes,
  FaSignOutAlt,
  FaBoxOpen,
} from "react-icons/fa";
import { AuthContext } from "../../context/AuthContext";

const Sidebar = ({ onClose }) => {
  const { logout } = useContext(AuthContext);

  const menu = [
    { name: "Cotizaciones", icon: <FaClipboardList />, path: "/quotations" },
    { name: "Ventas", icon: <FaShoppingCart />, path: "/sales" },
    { name: "Metales", icon: <FaBoxes />, path: "/metals" },
    { name: "Productos", icon: <FaBoxOpen />, path: "/products" },
    { name: "Reportes", icon: <FaChartBar />, path: "/reports" },
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
