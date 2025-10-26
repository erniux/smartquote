#!/bin/sh
set -e

echo "🚀 Iniciando daemon de Ollama..."
ollama serve &

# Esperar a que el servicio esté disponible
echo "⏳ Esperando a que Ollama esté disponible..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "⏳ Aún no responde, reintentando..."
  sleep 3
done

# Descargar el modelo si no existe
#if ! ollama list | grep -q "llama3:latest"; then
#  echo "🧠 Descargando modelo llama3:latest..."
#  ollama pull llama3:latest
if ! ollama list | grep -q "mistral"; then
  echo "🧠 Descargando modelo mistral..."
  ollama pull mistral:latest 
else
  echo "✅ Modelo mistral:latest ya disponible."
fi

echo "🟢 Servidor Ollama iniciado y listo."
wait
