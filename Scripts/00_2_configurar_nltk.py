# -----------------------------------------------
# 00_2_descargar_recursos_nltk.py
# Script para descargar recursos adicionales de NLTK necesarios para el procesamiento de texto
# Uso: Ejecutar después de instalar las librerías, antes de usar funciones de limpieza de texto
# -----------------------------------------------

try:
    import nltk  # Natural Language Toolkit: Librería para procesamiento de lenguaje natural

    print("📚 Descargando recursos de NLTK...\n")

    # Descarga de las 'stopwords': palabras vacías como "el", "de", "y", que suelen eliminarse del texto
    nltk.download("stopwords")

    # Descarga del tokenizer 'punkt': necesario para dividir texto en frases o palabras
    nltk.download("punkt")

    print("\n✅ Recursos NLTK descargados correctamente.")
    print("🔁 Reinicie su entorno de código para aplicar los cambios.")

except ImportError:
    # Este bloque se ejecuta si no se puede importar la librería NLTK
    print("❌ No se pudo importar NLTK. Asegúrate de haber ejecutado primero 'instalar_librerias.py'.")