import React from "react";

/**
 * Contenedor base reutilizable para páginas del panel.
 * Aplica márgenes, paddings, fondo blanco y zona superior para acciones.
 *
 * Ejemplo de uso:
 * <PageContainer actions={<button>Nuevo</button>}>
 *   <h1>Mi título</h1>
 *   <Contenido />
 * </PageContainer>
 */
const PageContainer = ({ children, actions }) => {
  return (
    <div className="p-6">
      {/* Encabezado superior: acciones (botones) */}
      {actions && (
        <div className="flex justify-end items-center mb-6 gap-3">
          {actions}
        </div>
      )}

      {/* Contenedor principal de contenido */}
      <div className="bg-white shadow-md rounded-lg p-6">{children}</div>
    </div>
  );
};

export default PageContainer;
