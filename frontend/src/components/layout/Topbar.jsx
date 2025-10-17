import React, { useContext } from "react";
import { FaUserCircle, FaSignOutAlt } from "react-icons/fa";
import { AuthContext } from "../../context/AuthContext";
  


const Topbar = ({ user, logo }) => {
  const { logout } = useContext(AuthContext);

  return (
    <div className="w-full h-16 bg-white shadow-md flex items-center justify-between px-6 py-3 sticky top-0 z-40">
      {/* Logo o título */}
      <div className="flex items-center gap-2">
        {logo ? (
          <img src={logo} alt="Logo" className="h-10 w-auto object-contain" />
        ) : (
          <h1 className="text-xl font-bold text-green-700">SmartQuote</h1>
        )}
      </div>

      {/* Usuario + Logout */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <FaUserCircle className="text-2xl text-gray-600" />
          <div className="text-sm text-slate-600">
            <p className="font-medium">{user?.name || "Usuario"}</p>
            <p className="text-gray-400 text-xs">{user?.email || "sin correo"}</p>
          </div>
        </div>

        {/* Botón de logout */}
        <button
          onClick={logout}
          title="Cerrar sesión"
          className="text-gray-600 hover:text-green-700 transition-colors"
        >
          <FaSignOutAlt className="text-xl" />
        </button>
      </div>
    </div>
  );
};

export default Topbar;
