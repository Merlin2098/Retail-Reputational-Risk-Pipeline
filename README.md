# 📊 Retail Reputation Risk Pipeline  

Pipeline en **Python** para identificar y mapear riesgos reputacionales en el sector retail peruano, a partir del análisis de publicaciones en Facebook.  

Este proyecto transforma una muestra de **100 publicaciones** en clusters temáticos y genera un mapa de riesgos con insights estratégicos para comunicación corporativa y gestión de crisis.  

---

## ⚙️ Tecnologías utilizadas
- **Entorno:** VS Code  
- **Lenguaje:** Python  
  - pandas → manipulación y limpieza de datos  
  - sentence-transformers → embeddings semánticos  
  - scikit-learn → clustering con K-Means  
  - nltk (tokenizer + stopwords en español) → procesamiento de texto  
  - openpyxl → integración y merge en Excel  
  - matplotlib → visualizaciones básicas  
- **Apoyo:** ChatGPT (prompts offline, sin uso de API key)  
- **Visualización ejecutiva:** Power BI → gráficas exportadas a PowerPoint  

---

## 🔄 Pipeline propuesto
1. **Instalar librerías** → script para instalar automáticamente los paquetes.  
2. **Configurar NLTK** → descarga de recursos adicionales para texto en español.  
3. **Limpiar datos** → normalización, eliminación de ruido y enriquecimiento.  
4. **Extraer keywords por post** → términos más frecuentes en cada publicación.  
5. **Agrupar clusters** → embeddings + clustering con K-Means.  
6. **Extraer keywords por cluster** → palabras representativas por grupo temático.  
7. **Generar prompt** → archivo `.txt` para análisis asistido con LLM (sin API).  
8. **Unir resultados** → consolidación del output del LLM y exportación a Excel.  

📌 *(Ver el diagrama del pipeline en `/outputs/pipeline_diagram.png`)*  

---

## 📂 Estructura del repositorio
```
📦 Retail-Reputation-Risk-Pipeline
 ┣ 📂 data/               # dataset reducido (100 posts de ejemplo)
 ┣ 📂 Presentation/       # PowerPoint con presentación ejecutiva de insights
 ┣ 📂 Scripts/            # scripts Python numerados
 ┣ Pipeline.jpg           #Diagrama Pipeline del proceso
 ┣ requirements.txt       # librerias necesarias
 ┗ README.md              # este archivo
```

---

🔄 Flujo del Proyecto

El análisis sigue un pipeline secuencial que inicia en la limpieza de datos y culmina en la generación de resultados finales.

Cada script en scripts/ genera un output específico dentro de la carpeta outputs/ (los archivos resultantes no están incluidos en el repositorio, solo se listan como referencia).

📂 Scripts y Outputs esperados

00_1_instalar_librerias.py
Instalación de librerías necesarias. (No genera output directo)

00_2_configurar_nltk.py
Descarga y configuración de recursos NLTK. (No genera output directo)

01_limpiar_datos.py
→ Genera: 1_Dataset_Limpio.xlsx

02_extraer_keywords_post.py
→ Genera: 2_keywords_por_post.xlsx

03_agrupar_cluster.py
→ Genera: 3_Cluster_Indicadores.xlsx

04_extraer_keywords_cluster.py
→ Genera: 4_Top_Words_Cluster.xlsx

05_generar_prompts.py
→ Genera: 5_prompts.txt
(Archivo de texto que debe ser ingresado al LLM de su preferencia para continuar con el análisis de temáticas)

06_unir_resultados.py
→ Genera:

6_LLM_Respuestas.xlsx

7_Merge_Final.xlsx

---

## 📊 Principales insights obtenidos
El pipeline permitió identificar **5 clusters de conversacion** con riesgos reputacionales asociados:  

| Cluster | Temática                                | Riesgo Reputacional |
|---------|-----------------------------------------|----------------------|
| C1      | Inseguridad ciudadana y asaltos        | Asaltos a empresas, percepción de inseguridad, afectación a marcas mencionadas |
| C2      | Criminalidad urbana y conflictos sociales | Vínculo con crimen organizado, debilidad institucional, impacto en imagen de autoridades |
| C3      | Accidentes y tragedias familiares      | Sensacionalismo mediático, exposición de víctimas, demanda de justicia social |
| C4      | Emergencias urbanas y desastres        | Falta de prevención, cuestionamiento a la gestión pública, impacto mediático |
| C5      | Deficiencias en infraestructura y fiscalización | Riesgos de clausura, pérdida de confianza, sanciones regulatorias, accidentes evitables |  

---

## 📎 Recursos adicionales
- 📂 Dataset reducido (`/data/posts_100.xlsx`)  
- 📊 Presentación ejecutiva con insights (PowerPoint)  
- 📑 Código Python documentado en `/scripts/`  



