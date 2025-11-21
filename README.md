# 🏀 [PF - DATA ANALYSTS] Evaluación Predictiva de Rendimiento en Baloncesto (NBA)

# En este repositorio se guardarán las versiones del Proyecto Final del grupo 01. Grupo el cual pertenece a las cohorte 09 de Data Analyst de Henry

### Soporte Analítico para Apostadores Deportivos (TrueShot AnalitIQ)

![GitHub Workflow Status](https://img.shields.io/badge/Status-Completado-brightgreen)
![Python](https://img.shields.io/badge/Tecnología%20Principal-Python-blue)
![BigQuery](https://img.shields.io/badge/Data%20Warehouse-BigQuery-red)

---

## 1. 🎯 Visión General y Problema de Negocio

Este proyecto final de Data Analytics aborda el desafío de **reducir la incertidumbre** en las apuestas deportivas de la NBA mediante la identificación y el análisis de factores estadísticos clave. Desarrollamos un modelo analítico y **5 Features Propietarias** para predecir la probabilidad de victoria de un equipo, ofreciendo a los apostadores una base de datos más sólida que la intuición o las estadísticas superficiales.

### 🔑 Objetivos Clave

- **Objetivo Predictivo:** Evaluar y predecir el impacto de 5 factores clave en la **probabilidad de victoria (P)** mediante Regresión Logística.
- **Valor de Negocio:** Generar métricas y _insights_ accionables, especialmente en el factor de **Arbitraje y Lesiones de Estrellas**, para aumentar la precisión en la toma de decisiones.
- **KPI Central:** **Net Rating**, como el indicador de eficiencia más confiable y libre del sesgo del ritmo de juego (`Pace`).

---

## 2. 🛠️ Stack Tecnológico

La solución fue construida utilizando un pipeline _End-to-End_ que garantiza la **reproducibilidad** y el **manejo eficiente de Big Data** (dataset con más de 12 millones de filas).

| Categoría               | Herramientas                         | Uso y Propósito                                                                                                      |
| :---------------------- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------- |
| **Análisis, EDA y ETL** | `Python` (Pandas, NumPy, MatplotLib) | Limpieza de datos (EDA), **Ingeniería de Features Avanzadas** (Net Rating, Referee Effect) y Modelado Predictivo.    |
| **Base de Datos**       | `Big Query`                          | Almacenamiento, modelado relacional y gestión eficiente de los datos históricos. Fuente única para la visualización. |
| **Visualización**       | **`Looker` (Google Cloud)**          | Creación de un Dashboard interactivo (12 Pestañas) para _storytelling_ y presentación de resultados clave.           |
| **Modelado ML**         | **Regresión Logística**              | Algoritmo de clasificación para predecir la **probabilidad (0 a 1)** de victoria del equipo local.                   |
| **Versión**             | `Git / GitHub`                       | Control de versiones, colaboración en equipo.                                                                        |
| **Interfaz MVP**        | `tkinter` (Python)                   | Interfaz Mínima Viable para simular una predicción con `features` de entrada manuales.                               |

---

## 3. ⚙️ Pipeline del Proyecto (Data Workflow)

El proyecto enfatiza el proceso de **ETL** y **Feature Engineering** para crear las variables que alimentan el modelo predictivo.

1. **Ingesta y Extracción (Data Acquisition):**
   - Datos crudos obtenidos de Kaggle ("NBA Database").
   - Carga inicial en **Big Query** para aprovechamiento del escalamiento.
2. **Limpieza y Transformación (ETL - Python/Big Query):**
   - **Optimización:** Manejo de nulos, _outliers_ y estandarización de IDs (equipos, jugadores, árbitros).
   - **Feature Engineering Demostrable (ETL):** Cálculo de la **Influencia del Árbitro (`referee_effect`)** mediante la unión de la tabla de resultados (`clean_game.csv`) y la tabla de árbitros (`officials_clean.csv`) y el cálculo de la diferencia del Win Rate histórico.
3. **Análisis y Modelado:**
   - **EDA Avanzado:** Cálculo del **Net Rating** y **True Shooting %** a nivel de partido y temporada.
   - **Feature Engineering:** Creación de la **Matriz de Entrenamiento** con las 5 variables principales:
     1. **`diff_strength`** (Diferencial de fuerza/rating entre equipos)
     2. **`Localia`** (Ventaja de ser local)
     3. **`star_home_is_injured`** (Lesión de estrella local)
     4. **`star_away_is_injured`** (Lesión de estrella visitante)
     5. **`referee_effect`** (Influencia histórica del árbitro en el equipo)
   - **Modelado Predictivo:** Entrenamiento del modelo de **Regresión Logística**.
4. **Visualización y Storytelling:**
   - Dashboard de **Looker** (12 pestañas) conectado a Big Query para visualizar el comportamiento de las 5 _features_ y los KPIs de eficiencia.

---

## 4. 📈 Resultados Clave y Modelo Predictivo

### A. Modelo (Regresión Logística)

El modelo clasifica si el resultado será Victoria Local (1) o Derrota Local (0), entregando como valor clave la **probabilidad $P$**.

- **Justificación:** Se eligió la **Regresión Logística** por su alta **interpretabilidad**. Permite al apostador saber exactamente cuánto peso tiene cada factor (ej: el efecto del árbitro o la lesión de una estrella) en la probabilidad final, lo que es vital para la confianza en la toma de decisiones.

### B. KPIs de Eficiencia (Valor Agregado)

| KPI                       | Definición                                                                                        | Relevancia para Apuestas                                                                    |
| :------------------------ | :------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------ |
| **Net Rating**            | Diferencial de puntos por 100 posesiones (ORtg - DRtg).                                           | Mide la **eficiencia real** de un equipo, eliminando el sesgo del ritmo de juego (`Pace`).  |
| **True Shooting % (TS%)** | Eficiencia de tiro ajustada por 2P, 3P y Tiros Libres.                                            | Muestra la **eficiencia de anotación**, siendo una métrica más confiable que el simple FG%. |
| **Referee Effect**        | Diferencia del Win Rate histórico de un equipo con un árbitro específico vs. su Win Rate general. | Valida la hipótesis de sesgo de arbitraje, siendo un factor clave en partidos cerrados.     |

---

## 5. 🧑‍💻 Autores y Contacto

| Nombre | Rol | GitHub |

| Francisco Hillebrand | Lider y Data Analyst |

| Juan Sebastián Gonzalez | Director de Diseño y Data Analyst |

| Fernando Tettamanti | Director Comercial y Data Analyst |

| Valentina Menna | BI Developer y Data Analyst |

| Julio Lopez | Data Engineer y Data Analyst |
