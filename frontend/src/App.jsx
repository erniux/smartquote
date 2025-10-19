import React, { useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { AuthProvider, AuthContext } from "./context/AuthContext";
import Layout from "./components/layout/Layout";
import LoginPage from "./pages/Login/LoginPage";
import QuotationPage from "./pages/Quotations/QuotationPage";
import SalesPage from "./pages/Sales/SalesPage";
import ProtectedRoute from "./components/ProtectedRoute";
import ProductsPage from "./pages/Products/ProductsPage";





function AppContent() {
  const { user } = useContext(AuthContext);

  return (
    <>
      {user ? (
        // ✅ Usuario autenticado → mostrar Layout completo
        <Layout>
          <Routes>
            <Route
              path="/quotations"
              element={
                <ProtectedRoute>
                  <QuotationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sales"
              element={
                <ProtectedRoute>
                  <SalesPage />
                </ProtectedRoute>
              }
            />
            <Route 
               path="/products" 
               element={<ProductsPage />} />
            <Route path="*" element={<Navigate to="/quotations" />} />
          </Routes>
        </Layout>
      ) : (
        // 🚪 Usuario no autenticado → mostrar Login a pantalla completa
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
        <ToastContainer position="bottom-right" autoClose={2500} theme="colored" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
