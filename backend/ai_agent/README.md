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
| `--export` | Copia el resultado a `/app/outputs/tests/` |
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

- 📅 **Fecha:** `2025-10-21 01:54:19`  
- 🤖 **Modelo usado:** `deepseek-r1:14b`  
- 🧩 **App procesada:** `sales`  
- ⚙️ **Parámetros:** `--export`  
- ⏱️ **Duración:** `0:00:00.071697`

---

## 🛠️ Problemas resueltos

❌ Conexión rechazada entre contenedor y Ollama → **Solución:** usar `host.docker.internal`  
❌ Modelos que requerían >30 GB RAM → **Cambio:** `deepseek-r1:14b`  
❌ Errores por versiones de LangChain → **Compatibilidad ajustada**  
⚙️ Docker sin `curl` → agregado en el Dockerfile  
⚡ Mejora en rendimiento, logs y creación automática de documentación

---

## 💡 Ejemplos de ejecución

Procesar solo una app:
```bash
python -m ai_agent.run_agent --app sales --export
```

Modo rápido y exportar:
```bash
python -m ai_agent.run_agent --app sales --fast --export
```

Procesar todo el proyecto y generar logs con README autoactualizado:
```bash
python -m ai_agent.run_agent --export --fallback
```

---

## ✨ Autor

**Erna Tercero Rodríguez**  
🧩 QA Engineer & Automation Developer  
📍 Querétaro, México  
📧 [eterceror@hotmail.com](mailto:eterceror@hotmail.com)  
🌐 [GitHub: erniux](https://github.com/erniux)
