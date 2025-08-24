# -----------------------------------------------
# 00_1_instalar_librerias.py
# Script para instalar automáticamente las librerías necesarias del proyecto
# Uso: Ejecutar una sola vez al inicio del proyecto
# -----------------------------------------------

import subprocess  # Permite ejecutar comandos del sistema (como pip)
import sys         # Permite acceder a variables del sistema, como la ruta de Python

# Lista de paquetes requeridos para que el proyecto funcione correctamente
paquetes = [
    "pandas",                # Manipulación y análisis de datos en tablas
    "nltk",                  # Procesamiento de lenguaje natural (limpieza de texto)
    "sentence-transformers", # Generación de vectores semánticos a partir de texto
    "scikit-learn",          # Herramientas de machine learning (clustering, métricas, etc.)
    "openpyxl"               # Lectura y escritura de archivos Excel (.xlsx)
]

def instalar_paquetes():
    """
    Recorre la lista de paquetes e intenta instalarlos uno por uno usando pip.
    Muestra un mensaje de confirmación o error por cada paquete.
    """
    for paquete in paquetes:
        print(f"📦 Instalando {paquete}...")
        try:
            # Ejecuta el comando: python -m pip install <paquete>
            subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
            print(f"✅ {paquete} instalado correctamente.\n")
        except subprocess.CalledProcessError:
            print(f"❌ Error al instalar {paquete}.\n")

# Este bloque se ejecuta solo si corres este script directamente
if __name__ == "__main__":
    print("🚀 Iniciando instalación de librerías...\n")
    instalar_paquetes()
    print("🎉 Instalación de librerías completada.")

