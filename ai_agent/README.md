# 🤖 AI Agent for Automated Test Generation

Este agente genera **pruebas automatizadas inteligentes** para proyectos **Django REST Framework**, analizando los archivos:

- `models.py`
- `views.py`
- `serializers.py`
- `utils.py`

Además, **actualiza automáticamente este README.md** con la fecha y el modelo usados en la última ejecución del agente, manteniendo un registro vivo de las corridas.

---

## 🚀 Características principales

✅ Genera pruebas unitarias y de integración con `pytest`  
✅ Detección automática del tipo de archivo (Model, View, Serializer, Utils)  
✅ Compatible con modelos Ollama (`deepseek-r1`, `llama3`, etc.)  
✅ Funciona dentro de Docker  
✅ Exporta automáticamente los tests generados  
✅ Crea logs históricos con tiempos y resultados  
✅ Permite filtrar por app específica  
✅ Incluye modo rápido y fallback inteligente  
✅ **Actualiza este README.md en cada ejecución con el modelo y la fecha más recientes**

---

## 🧩 Parámetros disponibles

| Opción | Descripción |
|--------|-------------|
| `--app <nombre>` | Procesa solo la app indicada |
| `--fast` | Analiza solo los primeros 3 archivos |
| `--export` | Copia el resultado a `/app/outputs/features/` |
| `--fallback` | Si no hay archivos en la app, analiza todo el proyecto |

---

## 🧠 Ejemplos de uso

```bash
# Generar tests para toda la app quotations
python -m ai_agent.run_agent --app quotations --export

# Modo rápido con fallback
python -m ai_agent.run_agent --app sales --fast --fallback

# Procesar todo el proyecto y exportar
python -m ai_agent.run_agent --export
```

---

## 📜 Logs y auditoría

Cada ejecución genera un log en:

```bash
/app/outputs/logs/ai_agent_report_YYYYMMDD_HHMMSS.txt
```

El log incluye:

- Fecha y hora de inicio y fin  
- Modelo usado  
- App objetivo  
- Duración total  
- Resultados por archivo (✅ ⚠️ ❌)

---

## 🧩 Historial de mejoras

| Fecha | Cambio |
|--------|---------|
| 2025-10-19 | Conexión inicial con Ollama dentro de contenedor |
| 2025-10-20 | Soporte `--fast` y `--export` |
| 2025-10-21 | Soporte `--app` y `--fallback` |
| 2025-10-21 | Reporte visual y logs con resumen detallado |
| 2025-10-22 | Generación automática de README.md ✨ |
| 2025-10-23 | Autoactualización del README.md con modelo y fecha de ejecución |

---

## ⚙️ Autoactualización del README

Al final de cada ejecución, el agente actualiza la siguiente sección con la información más reciente 👇

---


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        





























### 🧾 Última ejecución registrada
- 📅 Fecha: `2025-10-26 08:50:09`
- 🤖 Modelo usado: `mistral`
- 🧩 App procesada: `quotations`
- ⚙️ Parámetros:   
- ⏱️ Duración: `0:09:36.292527`
