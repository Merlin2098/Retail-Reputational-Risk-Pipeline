import pandas as pd
import os
import platform
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# -----------------------------
# 🔊 Emite un sonido si estás en Windows
# Útil como alerta de éxito o error
# -----------------------------
def emitir_blip(tipo="ok"):
    if platform.system() == "Windows":
        import winsound
        if tipo == "error":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            winsound.MessageBeep()

# -----------------------------
# 🔧 Limpia y normaliza la ruta ingresada
# Reemplaza backslashes por slashes y elimina comillas
# -----------------------------
def formatear_ruta(ruta_original):
    return ruta_original.strip().replace('\\', '/').strip('"').strip("'")

# -----------------------------
# 📄 Evita sobrescribir archivos previos
# Genera un nombre nuevo si ya existe un archivo con el mismo nombre
# -----------------------------
def generar_nombre_unico(ruta_base):
    contador = 1
    nombre_final = ruta_base
    while os.path.exists(nombre_final):
        nombre_final = ruta_base.replace('.xlsx', f'_{contador}.xlsx')
        contador += 1
    return nombre_final

# -----------------------------
# 🧠 Función principal: une el archivo del pipeline con el archivo generado por el modelo de lenguaje (LLM)
# Añade columnas 'tematica' y 'riesgos_reputacionales' según el cluster
# -----------------------------
def insertar_columnas_y_merge():
    try:
        # 📥 Solicita ruta del archivo principal (.xlsx)
        ruta_pipeline = input("📂 Ingresa la ruta del archivo principal (.xlsx): ")
        ruta_pipeline = formatear_ruta(ruta_pipeline)

        # 📥 Solicita ruta del archivo generado por LLM
        ruta_llm = input("📂 Ingresa la ruta del archivo generado por LLM (.xlsx): ")
        ruta_llm = formatear_ruta(ruta_llm)

        # 📄 Carga el archivo principal (pipeline)
        df_pipeline = pd.read_excel(ruta_pipeline)
        if 'cluster' not in df_pipeline.columns:
            raise ValueError("❌ El archivo principal debe tener una columna llamada 'cluster'.")

        # --------------------------
        # 📄 Carga robusta del archivo del LLM (busca hoja llamada 'Resumen' o 'Tabla Resumen')
        # --------------------------
        nombres_hojas_preferidos = ["Resumen", "Tabla Resumen"]
        df_llm = pd.DataFrame()
        hoja_encontrada = False

        try:
            excel_file_obj = pd.ExcelFile(ruta_llm)
            nombres_hojas_excel = excel_file_obj.sheet_names

            for nombre_hoja in nombres_hojas_preferidos:
                if nombre_hoja in nombres_hojas_excel:
                    df_llm = pd.read_excel(excel_file_obj, sheet_name=nombre_hoja)
                    print(f"¡Hoja '{nombre_hoja}' del LLM cargada con éxito!")
                    hoja_encontrada = True
                    break

            if not hoja_encontrada:
                raise ValueError(f"Error: No se encontró ninguna de las hojas {nombres_hojas_preferidos} en el archivo '{ruta_llm}'.")

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: El archivo LLM no se encontró en la ruta especificada: '{ruta_llm}'.")
        except ValueError as ve:
            raise ValueError(f"Error al cargar el archivo LLM: {ve}. Asegúrate de que el archivo contiene una de las hojas esperadas.")
        except Exception as e:
            raise Exception(f"Ocurrió un error inesperado al procesar el archivo LLM: {e}")

        # --------------------------
        # 🧼 Limpieza y renombramiento de columnas del LLM
        # --------------------------
        if not df_llm.empty:
            df_llm.columns = [col.strip() for col in df_llm.columns]  # Elimina espacios

            # Se asume que:
            # - Primera columna es 'cluster'
            # - Segunda es 'tematica'
            # - Tercera es 'riesgos_reputacionales'
            if len(df_llm.columns) > 2:
                df_llm = df_llm.rename(columns={
                    df_llm.columns[0]: 'cluster',
                    df_llm.columns[1]: 'tematica',
                    df_llm.columns[2]: 'riesgos_reputacionales'
                })
            else:
                raise ValueError("Error: El archivo LLM no tiene al menos 3 columnas esperadas ('cluster', 'tematica', 'riesgos_reputacionales').")

        # --------------------------
        # 🔄 Emparejar valores por cluster
        # --------------------------
        df_pipeline['cluster'] = df_pipeline['cluster'].astype(str).str.strip()
        df_llm['cluster'] = df_llm['cluster'].astype(str).str.strip()

        # Crear diccionario estilo VLOOKUP: {cluster: {tematica: x, riesgos: y}}
        mapa = df_llm.set_index('cluster')[['tematica', 'riesgos_reputacionales']].to_dict(orient='index')

        # Insertar las columnas justo después de 'cluster'
        cluster_idx = df_pipeline.columns.get_loc('cluster')
        df_pipeline.insert(cluster_idx + 1, 'tematica', df_pipeline['cluster'].map(lambda x: mapa.get(x, {}).get('tematica', '')))
        df_pipeline.insert(cluster_idx + 2, 'riesgos_reputacionales', df_pipeline['cluster'].map(lambda x: mapa.get(x, {}).get('riesgos_reputacionales', '')))

        # --------------------------
        # 💾 Guardar resultado en un nuevo archivo Excel
        # --------------------------
        directorio = os.path.dirname(ruta_pipeline)
        ruta_base = os.path.join(directorio, "7_Merge_Final.xlsx")
        ruta_final = generar_nombre_unico(ruta_base)
        df_pipeline.to_excel(ruta_final, index=False)

        emitir_blip("ok")
        print(f"\n✅ Archivo generado con columnas de temática y riesgos:\n📁 {ruta_final}")

    except Exception as e:
        emitir_blip("error")
        print(f"\n❌ Error durante el proceso: {e}")

# -----------------------------
# ▶️ EJECUCIÓN DEL SCRIPT
# -----------------------------
if __name__ == "__main__":
    insertar_columnas_y_merge()