# SEÑAL · Creator Intelligence

## Aplicación online

[Abre SEÑAL · Creator Intelligence](https://creator-roi-uv9vtywsvccrmajsujlhyg.streamlit.app/)

Explora el catálogo, compara candidatos y estima una tarifa por reel directamente desde el navegador.

**Encuentra la señal. Elige con criterio.**

SEÑAL es una aplicación de análisis de datos para explorar creadores de Instagram, comparar candidatos y obtener una referencia de tarifa por reel.

Creado por Salvador Cruz como proyecto final de Data Analytics en Ironhack. El proyecto comenzó como CreatorROI y evolucionó hacia SEÑAL como identidad de la aplicación.

## Pregunta de negocio

¿Cómo elegir creadores para una campaña con un presupuesto limitado y negociar sus tarifas con más contexto?

La aplicación combina análisis del catálogo, filtros de selección, comparación de perfiles y un modelo de estimación de tarifas.

## Datos

El conjunto original contiene 10.000 registros de creadores de distintas plataformas. La aplicación utiliza el subconjunto preparado de Instagram:

- 7.800 perfiles.
- 15 categorías.
- 39 ciudades.
- Datos del mercado indio.

Las tarifas originales se convierten de rupias a euros utilizando un tipo de cambio fijo de 1 EUR = 106,0395 INR. Esta conversión facilita la lectura, pero no convierte los precios en referencias del mercado español.

## Recorrido por la aplicación

1. **El proyecto:** problema de negocio, propósito y presentación de SEÑAL.
2. **Datos y metodología:** preparación de los datos, estructura SQL, evaluación del modelo y acceso a Tableau.
3. **Análisis del catálogo:** categorías, distribución de tarifas y tarifa mediana por grupos de seguidores.
4. **Diseña tu campaña:** búsqueda de candidatos, comparación de hasta tres perfiles y cálculo del presupuesto para un reel por creador.
5. **Estima una tarifa:** estimación para perfiles del catálogo o nuevos perfiles.
6. **Próximos pasos y cierre:** resultados, limitaciones y propuestas de evolución.

## Metodología

- Exploración y preparación de los datos con Python y pandas.
- Creación, validación y análisis de una base de datos SQL.
- Organización relacional de perfiles, categorías, ciudades e idiomas.
- Desarrollo de dashboards en Tableau.
- Comparación de modelos de regresión para estimar la tarifa por reel.
- Integración del análisis y del modelo en Streamlit.

## Modelo de estimación

La aplicación utiliza un modelo de Bagging de regresión.

Se separan los datos en entrenamiento, validación y prueba. La comparación de modelos se realiza con validación y la evaluación final con el conjunto de prueba.

La métrica principal es el MAE, expresado en euros: indica cuánto se alejan las predicciones de las tarifas registradas, en promedio.

El modelo utiliza 11 variables:

- Categoría, ciudad e idioma.
- Seguidores.
- Likes, comentarios, compartidos y guardados medios.
- Número de publicaciones analizadas.
- Visualizaciones medias por contenido.
- Engagement.

El archivo del modelo conserva las categorías, las columnas y el escalado necesarios para preparar nuevas entradas de la misma forma que durante el entrenamiento.

Los resultados de evaluación están documentados en el notebook y en el apartado «Datos y metodología» de la aplicación.

## Estructura del proyecto

- `app.py`: aplicación Streamlit.
- `funciones.py`: funciones reutilizables de preparación y predicción.
- `01_exploracion.ipynb`: exploración, preparación y modelado.
- `data/raw/`: datos originales.
- `data/processed/`: datos preparados para Streamlit y Tableau.
- `modelos/`: modelo entrenado y elementos de preparación.
- `sql/`: creación, validación, análisis y estructura relacional.
- `tableau/`: libro de trabajo de Tableau.
- `docs/`: documentación y diagrama relacional.
- `.streamlit/config.toml`: configuración visual.
- `requirements.txt`: dependencias de la aplicación.

## Ejecución local

Entorno de desarrollo utilizado: Python 3.14.6.

Desde la raíz del proyecto, instala las dependencias:

    python -m pip install -r requirements.txt

Inicia la aplicación:

    python -m streamlit run app.py

Para utilizar el catálogo y el estimador deben estar disponibles estos archivos:

- `data/processed/instagram_preparado.csv`
- `modelos/bagging_creatorroi.joblib`
- `funciones.py`

El modelo ya está entrenado; no es necesario ejecutar el notebook para abrir la aplicación.

## Limitaciones

- Es un proyecto académico basado en un catálogo del mercado indio.
- Las métricas históricas no garantizan resultados futuros.
- La tarifa estimada es una referencia, no un presupuesto ni una recomendación de contratación.
- El cálculo de presupuesto utiliza un reel por creador y las tarifas registradas.
- La ciudad corresponde al creador, no necesariamente a su audiencia.
- Antes de contratar hay que revisar afinidad, audiencia, disponibilidad, entregables y derechos de uso.
- La aplicación no calcula el ROI real: no dispone de costes completos, conversiones e ingresos atribuibles a campañas.

## Próximos pasos

- Publicar la aplicación y probar su utilidad con usuarios.
- Incorporar datos recientes y de otros mercados.
- Analizar el error del modelo por categoría y tramo de tarifa.
- Incorporar resultados de campañas reales para evaluar el impacto comercial.

## Autor

Salvador Cruz · Influencer Marketing & Data Analytics  
Proyecto final de Ironhack.