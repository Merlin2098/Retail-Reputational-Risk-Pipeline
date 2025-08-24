import pandas as pd
import os
import platform

# -----------------------------------
# 🔊 Función para emitir sonidos en Windows
# Proporciona retroalimentación auditiva si hay error o éxito.
# -----------------------------------
def reproducir_blip(tipo="ok"):
    if platform.system() == "Windows":
        import winsound
        winsound.MessageBeep(winsound.MB_ICONHAND if tipo == "error" else winsound.MB_OK)

# -----------------------------------
# 🔧 Limpia y estandariza la ruta ingresada por el usuario
# -----------------------------------
def formatear_ruta(ruta_original):
    return ruta_original.strip().replace("\\", "/").strip('"').strip("'")

# -----------------------------------
# 📂 Carga archivos en formato Excel, CSV o JSON
# Valida que contengan las columnas 'cluster' y 'palabra'
# -----------------------------------
def cargar_archivo(ruta):
    try:
        ext = os.path.splitext(ruta)[1].lower()

        # Carga según extensión
        if ext == ".xlsx":
            df = pd.read_excel(ruta)
        elif ext == ".csv":
            df = pd.read_csv(ruta)
        elif ext == ".json":
            df = pd.read_json(ruta)
        else:
            raise ValueError("Formato no soportado. Usa .xlsx, .csv o .json.")

        # Estandariza nombres de columnas
        df.columns = [col.strip().lower() for col in df.columns]

        # Validación mínima
        if "cluster" not in df.columns or "palabra" not in df.columns:
            raise ValueError("El archivo debe contener las columnas 'cluster' y 'palabra'.")

        return df

    except Exception as e:
        reproducir_blip("error")
        print(f"❌ Error al cargar el archivo: {e}")
        return None

# -----------------------------------
# ✏️ Genera el texto (prompt) para enviar a un modelo de lenguaje (LLM)
# Se construye agrupando palabras clave por cluster y dando instrucciones específicas
# -----------------------------------
def generar_prompt(df):
    instrucciones = (
        "Eres un analista de datos experto en comunicación corporativa. Analiza las siguientes listas de palabras clave "
        "y genera una tabla que asigne una temática dominante y los riesgos reputacionales asociados por cada cluster.\n\n"
        "Los resultados esperados son:\n"
        "1) Tabla con columnas: Cluster | Temática | Riesgos reputacionales\n"
        "2) Tabla de resumen (omite cualquier explicación detallada. Usa solo frases breves o palabras clave por riesgo reputacional): "
        "Cluster | Temática | Riesgos reputacionales (tópicos generales)\n"
        "3) Exporta ambas tablas en un archivo de Excel, el cual tendra por nombre 6_LLM_Respuestas, usando una hoja por tabla.\n\n"
        "A continuación, las palabras clave agrupadas por cluster:\n"
    )

    bloques = []
    # Agrupa las palabras por cluster para construir el cuerpo del prompt
    for cluster, grupo in df.groupby("cluster"):
        palabras = grupo["palabra"].dropna().tolist()
        linea = f"{cluster}:\n{', '.join(palabras)}"
        bloques.append(linea)

    # Une instrucciones + bloques de palabras agrupadas
    prompt_final = instrucciones + "\n\n" + "\n\n--------------\n\n".join(bloques)
    return prompt_final

# -----------------------------------
# 💾 Guarda el prompt como archivo .txt sin sobrescribir versiones anteriores
# -----------------------------------
def guardar_prompt(prompt, ruta_origen):
    base_dir = os.path.dirname(ruta_origen) or "."
    base_name = "5_prompt_tematicas.txt"
    ruta_salida = os.path.join(base_dir, base_name)

    # Si ya existe, crea una versión con número incremental
    contador = 1
    while os.path.exists(ruta_salida):
        ruta_salida = os.path.join(base_dir, f"prompt_tematicas_{contador}.txt")
        contador += 1

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(prompt)

    return ruta_salida

# -----------------------------------
# ▶️ MAIN: Flujo principal de ejecución
# -----------------------------------
if __name__ == "__main__":
    # Solicita al usuario la ruta del archivo con palabras agrupadas por cluster
    ruta_input = input("📂 Ingresa la ruta del archivo con palabras por cluster: ")
    ruta = formatear_ruta(ruta_input)
    df = cargar_archivo(ruta)

    if df is not None:
        # Genera el prompt a partir del contenido del archivo
        prompt = generar_prompt(df)

        # Ofrece al usuario cómo desea visualizar el resultado
        print("\n📝 ¿Cómo deseas visualizar el prompt?")
        print("1. Consola")
        print("2. Exportar a archivo .txt")
        opcion = input("👉 Elige una opción (1 o 2): ").strip()

        if opcion == "1":
            print("\n📋 PROMPT GENERADO:\n")
            print(prompt)
        elif opcion == "2":
            salida = guardar_prompt(prompt, ruta)
            print(f"\n✅ Prompt guardado exitosamente en:\n{salida}")
        else:
            print("⚠️ Opción no válida. Mostrando en consola por defecto:\n")
            print(prompt)

        reproducir_blip("ok")
    else:
        print("❌ No se pudo generar el prompt.")