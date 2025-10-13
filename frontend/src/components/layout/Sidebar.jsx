import React from "react";
import { NavLink } from "react-router-dom";
import {
  FaClipboardList,
  FaShoppingCart,
  FaFileInvoiceDollar,
  FaBoxes,
  FaChartBar,
  FaTimes,
} from "react-icons/fa";

const Sidebar = ({ onClose }) => {
  const menu = [
    { name: "Cotizaciones", icon: <FaClipboardList />, path: "/quotations" },
    { name: "Ventas", icon: <FaShoppingCart />, path: "/sales" },
    { name: "Facturas", icon: <FaFileInvoiceDollar />, path: "/invoices" },
    { name: "Metales", icon: <FaBoxes />, path: "/metals" },
    { name: "Reportes", icon: <FaChartBar />, path: "/reports" },
  ];

  return (
    <aside className="flex flex-col h-full w-64 p-4">
      {/* Botón de cerrar (solo móvil) */}
      <div className="flex justify-between items-center md:hidden mb-4">
        <h2 className="text-lg font-semibold text-green-400">Menú</h2>
        <button onClick={onClose}>
          <FaTimes size={20} />
        </button>
      </div>

      <nav className="space-y-2">
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
    </aside>
  );
};

export default Sidebar;
