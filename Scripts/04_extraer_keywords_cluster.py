import pandas as pd
import nltk
import os
import platform
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# -----------------------------
# 🔊 Función para emitir sonido como retroalimentación
# -----------------------------
def reproducir_blip(tipo="exito"):
    if platform.system() == "Windows":
        import winsound
        if tipo == "error":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            winsound.MessageBeep(winsound.MB_OK)

# -----------------------------
# 📚 Verifica y descarga recursos de NLTK si no están disponibles
# -----------------------------
def descargar_recursos_nltk():
    for recurso in ['stopwords']:
        try:
            nltk.data.find(f'corpora/{recurso}')
        except LookupError:
            nltk.download(recurso, quiet=True)

descargar_recursos_nltk()

# -----------------------------
# 🔧 Funciones auxiliares para carga de datos
# -----------------------------

# Limpia y estandariza la ruta ingresada
def formatear_ruta(ruta_original):
    return ruta_original.strip().replace('\\', '/').strip('"').strip("'")

# Carga archivo Excel y valida columnas necesarias
def cargar_archivo(ruta):
    try:
        df = pd.read_excel(ruta)
        df.columns = [col.strip().lower() for col in df.columns]

        # Validación: se requieren columnas 'post_limpio' y 'cluster'
        if 'post_limpio' not in df.columns or 'cluster' not in df.columns:
            raise ValueError("❌ El archivo debe contener 'post_limpio' y 'cluster'.")

        # Rellena valores nulos
        df['post_limpio'] = df['post_limpio'].fillna('')
        return df
    except Exception as e:
        reproducir_blip("error")
        print(f"❌ Error al cargar el archivo: {e}")
        return None

# -----------------------------
# 🔠 Análisis de frecuencia de palabras por cluster
# -----------------------------
def analizar_frecuencia_por_cluster(df, top_n=30):
    # Obtiene stopwords en español y prepara el tokenizador
    stopwords_es = set(stopwords.words('spanish'))
    tokenizer = RegexpTokenizer(r'\w+')
    resultados = []

    # Agrupa los textos por cluster y analiza las palabras más frecuentes
    for cluster_label, grupo in df.groupby("cluster"):
        textos = grupo['post_limpio'].dropna().tolist()
        palabras = []

        for texto in textos:
            tokens = tokenizer.tokenize(texto.lower())
            tokens_filtrados = [w for w in tokens if w not in stopwords_es and len(w) > 2]
            palabras.extend(tokens_filtrados)

        # Extrae el top de palabras más comunes por cluster
        for palabra, freq in Counter(palabras).most_common(top_n):
            resultados.append({
                'cluster': cluster_label,
                'palabra': palabra,
                'frecuencia': freq
            })

    return pd.DataFrame(resultados)

# -----------------------------
# 💾 Exportación de resultados en varios formatos
# -----------------------------
def exportar_resultados(df_frecuencia, ruta_base, formato):
    base_dir = os.path.dirname(ruta_base) or '.'

    try:
        if formato == "excel":
            nombre_archivo = os.path.join(base_dir, "4_Top_Words_Cluster.xlsx")
            df_frecuencia.to_excel(nombre_archivo, index=False)

        elif formato == "csv":
            df_frecuencia.to_csv(os.path.join(base_dir, "4_Top_Words_Cluster.csv"), index=False, encoding="utf-8-sig")

        elif formato == "json":
            df_frecuencia.to_json(os.path.join(base_dir, "4_Top_Words_Cluster.json"), orient="records", force_ascii=False)

        reproducir_blip("exito")
        print("\n✅ Archivo exportado correctamente.")
    except Exception as e:
        reproducir_blip("error")
        print(f"❌ Error al exportar archivo: {e}")

# -----------------------------
# MAIN: Flujo principal del programa
# -----------------------------
if __name__ == "__main__":
    # Solicita la ruta del archivo Excel con datos procesados
    ruta_input = input("📂 Ingrese la ruta del archivo Excel limpio (.xlsx): ")
    ruta = formatear_ruta(ruta_input)
    df = cargar_archivo(ruta)

    if df is not None:
        print("\n✅ Archivo cargado. Realizando análisis de frecuencia...")

        # Ejecuta análisis de frecuencia por cluster
        df_frec = analizar_frecuencia_por_cluster(df)

        # Ofrece opciones de exportación al usuario
        print("\n💾 ¿En qué formato deseas exportar los resultados?")
        print("   1. Excel (.xlsx)")
        print("   2. CSV (.csv)")
        print("   3. JSON (.json)")
        print("   4. No exportar (solo visualizar en consola)")

        opcion = input("👉 Escribe el número de tu opción: ").strip()
        formatos_validos = {"1": "excel", "2": "csv", "3": "json", "4": "none"}

        while opcion not in formatos_validos:
            opcion = input("❌ Opción inválida. Elige 1, 2, 3 o 4: ").strip()

        formato = formatos_validos[opcion]

        # Visualiza en consola si el usuario así lo elige
        if formato == "none":
            print("\n📊 RESULTADOS DE FRECUENCIA (TOP PALABRAS POR CLUSTER)")
            print(df_frec.head(10))
            reproducir_blip("exito")
        else:
            # En algunos sistemas, Excel puede no estar disponible
            if formato == "excel" and platform.system() != "Windows":
                print("⚠️ Excel no está disponible fuera de entornos Windows. Usando CSV como alternativa.")
                formato = "csv"
            exportar_resultados(df_frec, ruta, formato)

    input("\nPresiona ENTER para salir...")
