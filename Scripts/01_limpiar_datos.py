# -----------------------------------------------
# 01_procesamiento_dataset.py
# Script para limpiar, transformar y enriquecer un archivo Excel con publicaciones
# Uso: Ejecutar después de descargar los recursos NLTK
# -----------------------------------------------

import pandas as pd
import re
import os
import unicodedata
import platform

# Función para emitir sonidos de notificación (solo en Windows)
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

# Lista de palabras que deben mantenerse aunque no tengan más de 3 letras
excepciones_validas = {
    "sjl", "sjm", "vmt", "vla", "lpp", "ess", "mml", "mtc", "onp", "afp", "sun", "sbn",
    "idu", "pj", "mp", "csj", "osce", "pnp", "sat", "apc", "ugp", "psc", "jna", "san"
}

# Lista personalizada de palabras vacías irrelevantes
stopwords_es_custom = set("""de la que el en y a los del se las por un para con no una su al lo como más pero sus le ya o este sí porque esta entre cuando muy sin sobre también me hasta hay donde quien desde todo nos durante todos uno les ni contra otros ese eso ante ellos e esto mí antes algunos qué unos yo otro otras otra él tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas algo nosotros mi mis tú te ti tu tus ellas nosotras vosotras vos ellos ellas uno mismo mismos misma mismas sea somos sois están""".split())

# Palabras adicionales a eliminar por no aportar valor semántico
palabras_a_eliminar = {
    "plaza", "plazas", "comercial", "centro", "soles", "ripley", "tienda", "tiendas",
    "mall", "anos", "real", "persona", "personas", "personal", "exitosanoticias",
    "trabajador", "trabajadores", "fecha", "exitosa", "radioexitosa", "exitosatv", "senal", "abierta",
    "tras", "segun", "contra", "durante", "mediante", "acerca", "respecto",
    "conforme", "alrededor", "cerca", "lejos", "junto", "frente", "aqui",
    "debido", "gracias", "incluso", "excepto", "salvo", "aunque",
    "ademas", "luego", "entonces", "mientras", "finalmente", "actualmente",
    "recientemente", "anteriormente", "posteriormente", "patio", "comida", "comidas",
    "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo",
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "setiembre", "septiembre", "octubre", "noviembre", "diciembre",
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
    "once", "doce", "trece", "catorce", "quince", "dieciseis", "diecisiete", "dieciocho", "diecinueve", "veinte"
}
palabras_a_eliminar = set(p.lower() for p in palabras_a_eliminar)

# Función para eliminar tildes del texto
def remover_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn' or c == 'ñ'
    )

# Función principal de limpieza de texto
def limpiar_texto_avanzado(texto):
    if pd.isnull(texto):
        return ""
    texto = str(texto).lower()
    texto = remover_tildes(texto)
    texto = re.sub(r"http\S+|www\.\S+|bit\.ly\S+", " ", texto)  # elimina URLs
    texto = re.sub(r"[^\w\sñ]", " ", texto)  # elimina signos de puntuación

    palabras = texto.split()
    palabras_filtradas = [
        palabra for palabra in palabras
        if palabra not in stopwords_es_custom
        and palabra not in palabras_a_eliminar
        and (len(palabra) > 3 or palabra in excepciones_validas)
        and not palabra.isdigit()
        and not re.search(r'\d', palabra)
    ]
    return " ".join(palabras_filtradas)

# Limpia rutas copiadas desde el explorador (remueve comillas y normaliza separadores)
def formatear_ruta(ruta_original):
    return os.path.normpath(ruta_original.strip().strip('"').strip("'"))

# Categorización de horas en rangos temporales para análisis
def obtener_rango_horario(hora):
    if pd.isnull(hora):
        return "0_Desconocido"
    if 0 <= hora <= 5:
        return "1_12am a 6am"
    elif 6 <= hora <= 11:
        return "2_6am a 12pm"
    elif 12 <= hora <= 17:
        return "3_12pm a 6pm"
    elif 18 <= hora <= 23:
        return "4_6pm a 12am"
    else:
        return "0_Desconocido"

# Diccionarios de mapeo de fechas para enriquecer el dataset
estaciones_dict = {
    12: "Verano", 1: "Verano", 2: "Verano",
    3: "Otoño", 4: "Otoño", 5: "Otoño",
    6: "Invierno", 7: "Invierno", 8: "Invierno",
    9: "Primavera", 10: "Primavera", 11: "Primavera"
}

temporadas_dict = {
    1: "Rebajas de Verano / Liquidación",
    2: "Back to School / Regreso a Clases",
    3: "Back to School / Regreso a Clases",
    5: "Día de la Madre",
    6: "Día del Padre",
    7: "Fiestas Patrias / Gratificación",
    10: "Cyber / Black Friday / Cyber Monday",
    11: "Navidad y Año Nuevo",
    12: "Navidad y Año Nuevo / Gratificación"
}

dias_dict_con_numero = {
    0: '1_Lunes', 1: '2_Martes', 2: '3_Miércoles', 3: '4_Jueves',
    4: '5_Viernes', 5: '6_Sábado', 6: '7_Domingo'
}

tipo_dia_dict = {
    0: "Día de semana", 1: "Día de semana", 2: "Día de semana",
    3: "Día de semana", 4: "Día de semana", 5: "Fin de semana", 6: "Fin de semana"
}

# Función completa para cargar, limpiar y enriquecer el archivo
def procesar_archivo_avanzado(ruta_archivo):
    try:
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError("❌ Archivo no encontrado.")

        df = pd.read_excel(ruta_archivo)
        df.columns = [col.strip().lower() for col in df.columns]

        if 'post' not in df.columns:
            raise ValueError("❌ La columna 'post' no está presente en el archivo.")

        # Limpieza de texto
        df['post_limpio'] = df['post'].apply(limpiar_texto_avanzado)

        # Enriquecimiento por fecha de publicación
        if 'published' in df.columns:
            df['published'] = pd.to_datetime(df['published'], errors='coerce')
            df['estacion'] = df['published'].dt.month.map(estaciones_dict).fillna("Desconocido")
            df['temporada_comercial'] = df['published'].dt.month.map(temporadas_dict).fillna("Sin campaña")
            df['día_semana'] = df['published'].dt.dayofweek.map(dias_dict_con_numero)
            df['tipo_dia'] = df['published'].dt.dayofweek.map(tipo_dia_dict)
            df['hora'] = df['published'].dt.strftime('%H:%M:%S')
            df['hora_12h'] = df['published'].dt.strftime('%I %p').str.lstrip('0')
            df['rango_horario'] = df['published'].dt.hour.apply(obtener_rango_horario)
            print("✅ Columna 'published' procesada, desglosada y enriquecida.")
        else:
            print("⚠️  No se encontró la columna 'published' en el DataFrame.")

        # Eliminación de columnas innecesarias si están presentes
        columnas_a_eliminar = [col for col in ['post', 'link', 'id', 'año', 'mes_num', 'fecha'] if col in df.columns]
        df.drop(columns=columnas_a_eliminar, inplace=True)

        # Guardar con nombre no duplicado
        directorio_salida = os.path.dirname(ruta_archivo)
        nombre_base = "1_Dataset_Limpio"
        contador = 1
        nombre_salida = os.path.join(directorio_salida, f"{nombre_base}.xlsx")

        while os.path.exists(nombre_salida):
            nombre_salida = os.path.join(directorio_salida, f"{nombre_base}_{contador}.xlsx")
            contador += 1

        df.to_excel(nombre_salida, index=False)

        print("\n✅ Archivo exportado exitosamente:")
        print(f"{nombre_salida}")
        print("\n🧾 Vista previa de columnas procesadas:\n")
        print(df[['post_limpio', 'published', 'hora_12h', 'rango_horario', 'día_semana', 'estacion', 'temporada_comercial', 'tipo_dia']].head(10))

        reproducir_blip("ok")

    except Exception as e:
        reproducir_blip("error")
        print(f"\n🚨 Error al procesar el archivo: {e}")

# Punto de entrada al ejecutar el script
if __name__ == "__main__":
    entrada_usuario = input("Ingrese la ruta del archivo Excel (.xlsx): ")
    reproducir_blip("ok")
    ruta = formatear_ruta(entrada_usuario)
    procesar_archivo_avanzado(ruta)
    input("\nPresione ENTER para salir...")