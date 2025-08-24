import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import os
import platform

# -------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------

# Número de grupos (clusters) que se desea generar para clasificar los textos
N_CLUSTERS = 5

# -------------------------------
# FUNCIONES
# -------------------------------

# Función para emitir sonidos en Windows como retroalimentación al usuario
def emitir_blip(tipo="info"):
    if platform.system() == "Windows":
        import winsound
        if tipo == "error":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            winsound.MessageBeep()

# Limpia y normaliza una ruta ingresada por el usuario
def formatear_ruta(ruta_original):
    return ruta_original.strip().replace('\\', '/').strip('"').strip("'")

# Carga un archivo Excel y valida que exista una columna llamada 'post_limpio'
def cargar_excel(ruta):
    try:
        df = pd.read_excel(ruta)
        # Limpia nombres de columnas para estandarizar
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        if 'post_limpio' not in df.columns:
            raise ValueError("❌ El archivo debe contener la columna 'post_limpio'.")
        
        return df
    except Exception as e:
        emitir_blip("error")
        print(f"❌ Error al cargar archivo: {e}")
        return None

# Genera embeddings semánticos para cada texto y los agrupa usando K-Means
def generar_clusters(df, n_clusters=N_CLUSTERS):
    print("🔄 Generando embeddings semánticos...")

    # Modelo multilingüe para transformar los textos en vectores numéricos
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    textos = df['post_limpio'].fillna('').tolist()
    embeddings = modelo.encode(textos, show_progress_bar=True)

    print("🔍 Agrupando en clusters...")

    # Agrupamiento usando K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    etiquetas_numericas = kmeans.fit_predict(embeddings)

    # Asigna etiquetas legibles (C1, C2, ...) a cada registro
    etiquetas_alfanumericas = [f"C{i+1}" for i in etiquetas_numericas]
    df['cluster'] = etiquetas_alfanumericas

    return df

# Calcula métricas de engagement a partir de las columnas de redes sociales
def calcular_metricas_engagement(df):
    print("📊 Calculando métricas de engagement...")

    columnas_necesarias = ['facebook_reactions', 'facebook_shares', 'facebook_comments', 'total_interactions']
    
    # Si alguna columna no existe, se agrega con valor cero
    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = 0

    # Se calcula una nueva columna auxiliar para totalizar interacciones
    df['total_interacciones_calc'] = df['facebook_reactions'] + df['facebook_shares'] + df['facebook_comments']

    # Se calculan proporciones para cada tipo de interacción
    with pd.option_context('mode.chained_assignment', None):
        df['ratio_reacciones'] = df['facebook_reactions'] / df['total_interacciones_calc'].replace(0, 1)
        df['ratio_comentarios'] = df['facebook_comments'] / df['total_interacciones_calc'].replace(0, 1)
        df['ratio_shares'] = df['facebook_shares'] / df['total_interacciones_calc'].replace(0, 1)

    # Se elimina la columna auxiliar
    df.drop(columns=['total_interacciones_calc'], inplace=True)

    return df

# Genera un nombre de archivo que no sobrescriba uno existente
def generar_nombre_unico(ruta_base):
    contador = 1
    nombre_final = ruta_base
    while os.path.exists(nombre_final):
        nombre_final = ruta_base.replace('.xlsx', f'_{contador}.xlsx')
        contador += 1
    return nombre_final

# -------------------------------
# MAIN (bloque principal del programa)
# -------------------------------
if __name__ == "__main__":
    try:
        # Solicita al usuario la ruta del archivo Excel con los textos limpios
        ruta_input = input("📂 Ingresa la ruta del archivo Excel limpio (.xlsx): ")
        ruta = formatear_ruta(ruta_input)

        # Carga el archivo y valida que se haya realizado correctamente
        df = cargar_excel(ruta)
        if df is not None:
            print(f"✅ {len(df)} registros cargados. Procesando...")

            # Agrupa los textos en clusters y calcula métricas de engagement
            df = generar_clusters(df)
            df = calcular_metricas_engagement(df)

            # Define la ruta de salida sin sobrescribir archivos existentes
            directorio = os.path.dirname(ruta)
            salida_base = os.path.join(directorio, "3_Cluster_Indicadores.xlsx")
            salida_final = generar_nombre_unico(salida_base)

            # Guarda el archivo resultante con los clusters y métricas
            df.to_excel(salida_final, index=False)

            emitir_blip("info")
            print(f"\n✅ Archivo exportado con clusters y métricas de engagement:")
            print(f"📁 {salida_final}")
        else:
            emitir_blip("error")

    except Exception as e:
        emitir_blip("error")
        print(f"\n🚨 Error inesperado: {e}")

