import React from "react";

const PageContainer = ({ title, icon, children, actions }) => {
  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          {icon && <span className="h-8 w-8 text-emerald-600">{icon}</span>}
          <h1 className="text-3xl font-bold text-slate-800 mb-8 flex items-center gap-2">{title}</h1>
        </div>

        <div className="flex gap-3">{actions}</div>
      </div>

      {/* Contenido */}
      <div className="bg-white shadow-md rounded-lg p-4">{children}</div>
    </div>
  );
};

export default PageContainer;


