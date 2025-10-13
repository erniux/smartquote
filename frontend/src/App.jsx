import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout";
import QuotationsPage from "./pages/Quotations/QuotationPage";

function App() {
  const mockUser = {
    name: "Patricia Pérez",
    email: "patricia@esmeralda.mx",
  };

  return (
    <Layout user={mockUser}>
      <Routes>
        <Route path="/" element={<Navigate to="/quotations" />} />
        <Route path="/quotations" element={<QuotationsPage />} />
        <Route path="*" element={<p>Página no encontrada</p>} />
      </Routes>
    </Layout>
  );
}

export default App;
