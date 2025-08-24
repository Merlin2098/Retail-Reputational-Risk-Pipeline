import pandas as pd
import nltk
import platform
import os
import json
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# -----------------------------------
# Función para emitir un sonido (solo en Windows)
# Útil para dar feedback auditivo al usuario cuando algo sale bien o mal
# -----------------------------------
def reproducir_blip(tipo="ok"):
    if platform.system() == "Windows":
        try:
            import winsound
            if tipo == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            else:
                winsound.MessageBeep()
        except Exception:
            pass

# -----------------------------------
# Función para descargar los recursos necesarios de NLTK si no están presentes
# En este caso, las stopwords (palabras vacías comunes del español)
# -----------------------------------
def descargar_recursos_nltk():
    recursos = ['stopwords']
    for recurso in recursos:
        try:
            nltk.data.find(f'corpora/{recurso}')
        except LookupError:
            nltk.download(recurso, quiet=True)

descargar_recursos_nltk()

# -----------------------------------
# Normaliza y limpia la ruta ingresada por el usuario
# Elimina comillas, espacios extra y reemplaza backslashes por slashes
# -----------------------------------
def formatear_ruta(ruta_original):
    ruta = ruta_original.strip().replace('\\', '/').strip('"').strip("'")
    return ruta

# -----------------------------------
# Carga el archivo Excel con los textos ya procesados ('post_limpio')
# Valida que la columna necesaria exista y completa valores nulos con cadenas vacías
# -----------------------------------
def cargar_archivo(ruta):
    try:
        df = pd.read_excel(ruta)
        df.columns = [col.strip().lower() for col in df.columns]

        if 'post_limpio' not in df.columns:
            raise ValueError("❌ El archivo debe contener una columna llamada 'post_limpio'.")
        
        df['post_limpio'] = df['post_limpio'].fillna('')
        return df
    except Exception as e:
        reproducir_blip("error")
        print(f"❌ Error al cargar el archivo: {e}")
        return None

# -----------------------------------
# Procesa todos los textos de la columna 'post_limpio' y extrae las palabras más frecuentes
# Elimina las palabras vacías (stopwords) y filtra palabras muy cortas
# Devuelve una lista con las palabras más comunes y su frecuencia
# -----------------------------------
def contar_palabras(df, top_n=15):
    stopwords_es = set(stopwords.words('spanish'))
    tokenizer = RegexpTokenizer(r'\w+')
    palabras = []

    textos = df['post_limpio'].tolist()

    for texto in textos:
        tokens = tokenizer.tokenize(texto.lower())
        tokens_filtrados = [w for w in tokens if w not in stopwords_es and len(w) > 2]
        palabras.extend(tokens_filtrados)

    contador = Counter(palabras)
    return contador.most_common(top_n)

# -----------------------------------
# Exporta los resultados del análisis a un archivo (Excel, CSV o JSON)
# El nombre del archivo se adapta automáticamente para evitar sobreescribir
# -----------------------------------
def exportar_resultados(resultados, ruta_origen, formato="excel"):
    carpeta_destino = os.path.dirname(ruta_origen)  # Carpeta del archivo original
    nombre_base = "2_keywords_por_post"
    contador = 1
    extension = {"excel": ".xlsx", "csv": ".csv", "json": ".json"}[formato]
    nombre_salida = os.path.join(carpeta_destino, f"{nombre_base}{extension}")

    # Si ya existe un archivo con el mismo nombre, agrega un sufijo incremental
    while os.path.exists(nombre_salida):
        nombre_salida = os.path.join(carpeta_destino, f"{nombre_base}_{contador}{extension}")
        contador += 1

    # Convierte el resultado a un DataFrame
    df_export = pd.DataFrame(resultados, columns=["Keyword", "Frecuencia"])

    # Exporta al formato deseado
    if formato == "excel":
        df_export.to_excel(nombre_salida, index=False)
    elif formato == "csv":
        df_export.to_csv(nombre_salida, index=False)
    elif formato == "json":
        with open(nombre_salida, "w", encoding="utf-8") as f:
            json.dump(dict(resultados), f, ensure_ascii=False, indent=2)

    return nombre_salida

# -----------------------------------
# Bloque principal que ejecuta todo el proceso
# Carga el archivo, realiza el análisis y pregunta al usuario cómo quiere ver/exportar los resultados
# -----------------------------------
if __name__ == "__main__":
    ruta_input = input("📂 Ingresa la ruta del archivo Excel limpio (.xlsx): ")
    ruta = formatear_ruta(ruta_input)

    df = cargar_archivo(ruta)
    if df is not None:
        print("\n✅ Archivo cargado correctamente. Procesando texto...\n")
        resultados = contar_palabras(df, top_n=50)

        print("📤 ¿Cómo deseas visualizar los resultados?")
        print("1. Consola")
        print("2. Exportar a Excel")
        print("3. Exportar a CSV")
        print("4. Exportar a JSON")

        opcion = input("👉 Elige una opción (1-4): ").strip()

        salida = None
        if opcion == "1":
            print("\n🔝 Palabras más frecuentes:\n")
            for palabra, frecuencia in resultados:
                print(f"{palabra:>15}: {frecuencia}")
        elif opcion in {"2", "3", "4"}:
            formatos = {"2": "excel", "3": "csv", "4": "json"}
            salida = exportar_resultados(resultados, ruta, formatos[opcion])
            if salida:
                print(f"\n✅ Resultados exportados exitosamente a:\n{salida}")
        else:
            print("⚠️  Opción no válida. Mostrando en consola por defecto:")
            for palabra, frecuencia in resultados:
                print(f"{palabra:>15}: {frecuencia}")

        reproducir_blip("ok")
    else:
        print("❌ No se pudo procesar el archivo.")

    input("\nPresiona ENTER para salir...")