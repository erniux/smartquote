import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AuthContext);

  if (loading) return <p className="text-center mt-10">Cargando sesión...</p>;

  return user ? children : <Navigate to="/login" replace />;
}
