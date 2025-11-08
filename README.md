# 🏀 [PF - DATA ANALYSTS] Evaluación Predictiva de Rendimiento en Baloncesto (NBA)


En este repositorio se guardarán las versiones del Proyecto Final del grupo 01. Grupo el cual pertenece a las cohorte 09 de Data Analyst de Henry
=======
### Soporte Analítico para Apostadores Deportivos

[BADGE: Añadir aquí un badge de tu estado de construcción]
[BADGE: Añadir aquí un badge de la tecnología principal]

---

## 1. 🎯 Visión General y Problema de Negocio

Este proyecto final de Data Analytics aborda el desafío de **reducir la incertidumbre** en las apuestas deportivas de la NBA mediante la identificación y el análisis de factores estadísticos clave. Desarrollamos un modelo analítico y un **KPI propietario** para predecir la probabilidad de victoria de un equipo, ofreciendo a los apostadores una base de datos más sólida que la intuición o las estadísticas superficiales.

### 🔑 Objetivos Clave

- **Objetivo Predictivo:** Evaluar y predecir el impacto del rendimiento de los equipos en la probabilidad de victoria.
- **Valor de Negocio:** Generar métricas y _insights_ accionables para aumentar la precisión en la toma de decisiones dentro de las apuestas deportivas.
- **KPI Central:** Definición de un Indicador Clave de Rendimiento (KPI) asociado a la probabilidad de victoria basado en eficiencia avanzada.

---

## 2. 🛠️ Stack Tecnológico

La solución fue construida utilizando un pipeline _End-to-End_ que garantiza la **reproducibilidad** y el **manejo eficiente de Big Data** (dataset con más de 12 millones de filas).

| Categoría               | Herramientas                         | Uso y Propósito                                                                              |
| :---------------------- | :----------------------------------- | :------------------------------------------------------------------------------------------- |
| **Análisis, EDA y ETL** | `Python` (Pandas, NumPy, MatplotLib) | Limpieza de datos (EDA), Ingeniería de Features y Modelado Predictivo.                       |
| **Base de Datos**       | `Big Query`                          | Almacenamiento, modelado relacional y gestión eficiente de los datos históricos.             |
| **Visualización**       | `Power BI`                           | Creación de un Dashboard interactivo para _storytelling_ y presentación de resultados clave. |
| **Versión**             | `Git / GitHub`                       | Control de versiones, colaboración en equipo y gestión de archivos grandes (Git LFS).        |
| **Diseño**              | `Canva, Figma`                       | Mockup inicial para la visualización (Dashboard) y DEMO 1                                    |

---

## 3. ⚙️ Pipeline del Proyecto (Data Workflow)

El proyecto sigue una estructura de Ingeniería de Datos y Análisis estándar:

1.  **Ingesta y Extracción (Data Acquisition):**
    - Datos crudos obtenidos de **Kaggle** (Dataset "NBA Database").
    - Manejo de archivos grandes (`play_by_play.csv`) mediante **Git LFS** o exclusión vía `.gitignore` y gestión directa en Cloud/BigQuery.
2.  **Limpieza y Transformación (ETL):**
    - Optimización de _datasets_ con **Python/Pandas** (manejo de nulos, tipado, _outliers_).
    - Modelado de los datos en un esquema relacional (Star Schema conceptual) en **Big Query**.
3.  **Análisis y Modelado:**
    - **EDA:** Identificación de patrones de rendimiento ofensivo/defensivo y dependencia de la cancha.
    - **Feature Engineering:** Cálculo de métricas avanzadas (ej: **Net Rating, True Shooting %**) para el modelo.
    - **Modelado Predictivo:** Uso de [Mencionar aquí tu modelo: Regresión Logística, Random Forest, etc.] para calcular la probabilidad de victoria.
4.  **Visualización y Storytelling:**
    - Conexión de Power BI al origen de datos (Big Query y Python).
    - Creación del Dashboard final para la presentación de los resultados y la interpretación del KPI.
5.  **Automatización:**
    - Script en Python para la ingesta incremental de nuevos datos de la NBA.

---

## 4. 📈 Resultados Clave y KPIs Desarrollados

[Esta sección la llenarás al final, pero sirve como gancho ahora.]

- **KPI Principal:** El **[Nombre del KPI]** demostró ser el factor predictivo más fuerte, con una correlación de [Valor]% con la probabilidad de victoria.
- **Insights:** [Aquí iría un ejemplo de tu hallazgo: "Los equipos con un alto True Shooting % mostraron una varianza de victoria significativamente menor, indicando una confiabilidad clave para las apuestas."]

---

## 5. 📁 Estructura del Repositorio

## 6. 🧑‍💻 Autores y Contacto

| Nombre | Rol | GitHub |
| Francisco Hillebrand | Lider y Data Analyst | [Enlace de GitHub] |
| Juan Sebastián Gonzalez | Director de Diseño y Data Analyst | [Enlace de GitHub] |
| Fernando Tettamanti | Director Comercial y Data Analyst | [Enlace de GitHub] |
| Valentina Menna | BI Developer y Data Analyst | [Enlace de GitHub] |
| Julio Lopez | Data Engineer y Data Analyst | [Enlace de GitHub] |

