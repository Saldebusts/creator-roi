import streamlit as st
from pathlib import Path
import pandas as pd
import joblib
from funciones import predecir_tarifas



def formato_numero(valor, decimales=0):
    """Formato español, solo para la presentación de cifras."""
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def cargar_catalogo(ruta, modificacion):
    """Lee los datos de nuevo cuando cambia el archivo."""
    return pd.read_csv(ruta, dtype={"Influencer_ID": str})


@st.cache_resource
def cargar_paquete(ruta, modificacion):
    """Conserva el modelo en memoria mientras no cambie el archivo."""
    return joblib.load(ruta)


def construir_entrada(valores, variables):
    """Reconstruye una fila con los mismos tipos que recoge el formulario."""
    enteros = [
        "Followers", "Average_Likes", "Average_Comments", "Average_Shares",
        "Average_Saves", "Number_of_Posts_Analyzed", "Average_Views_Per_Content"
    ]
    fila = {}
    for variable in variables:
        valor = valores[variable]
        if variable in enteros:
            fila[variable] = int(valor)
        elif variable == "Engagement_Rate_Percent":
            fila[variable] = float(valor)
        else:
            fila[variable] = str(valor)
    return pd.DataFrame([fila], columns=variables)


st.set_page_config(
    page_title="CreatorROI",
    page_icon="🎯",
    layout="wide"
)

st.caption("CREATORROI · INTELIGENCIA PARA INFLUENCER MARKETING")

st.title("Encuentra creadores. Compara opciones. Negocia con datos.")

st.write(
    "Una herramienta para agencias que necesitan seleccionar perfiles "
    "para una campaña y disponer de una referencia de tarifa por reel."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**01 · Encuentra**")
    st.write("Filtra el catálogo según la temática, los seguidores y tu presupuesto.")

with col2:
    st.markdown("**02 · Compara**")
    st.write("Consulta las métricas y tarifas de hasta tres candidatos juntos.")

with col3:
    st.markdown("**03 · Estima**")
    st.write("Introduce las características de un perfil y obtén una tarifa orientativa.")

st.caption(
    "Prototipo académico · Instagram · Mercado indio · Importes convertidos a euros"
)

# Localizamos los datos desde la carpeta del proyecto
carpeta_proyecto = Path(__file__).resolve().parent
ruta_datos = carpeta_proyecto / "data" / "processed" / "instagram_preparado.csv"

# Cargamos el catálogo
if not ruta_datos.exists():
    st.error("No se encuentra data/processed/instagram_preparado.csv. Comprueba la carpeta del proyecto.")
    st.stop()
instagram = cargar_catalogo(ruta_datos, ruta_datos.stat().st_mtime_ns)

ruta_modelo = carpeta_proyecto / "modelos" / "bagging_creatorroi.joblib"
if not ruta_modelo.exists():
    st.error("No se encuentra modelos/bagging_creatorroi.joblib. Conserva el modelo en su carpeta original.")
    st.stop()
paquete_modelo = cargar_paquete(ruta_modelo, ruta_modelo.stat().st_mtime_ns)


inicio, explorador, comparador, estimador = st.tabs([
    "Inicio",
    "Encuentra creadores",
    "Compara candidatos",
    "Estima una tarifa"
])

with inicio:
    st.divider()
    st.subheader("El reto de una agencia")

    st.write(
        "Una marca de belleza busca creadores para una campaña. "
        "La agencia necesita encontrar perfiles que encajen con el presupuesto, "
        "comparar sus métricas y disponer de una referencia para negociar."
    )

    st.write(
        "CreatorROI reúne esas decisiones en un mismo recorrido: "
        "explorar el catálogo, comparar candidatos y consultar el estimador."
    )
    st.subheader("Nuestro catálogo de creadores")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Perfiles de Instagram",
        f"{instagram['Influencer_ID'].nunique():,}".replace(",", ".")
    )

    col2.metric(
        "Categorías",
        instagram["Category"].nunique()
    )

    col3.metric(
        "Ciudades",
        instagram["City"].nunique()
    )

    tarifa_mediana = instagram["Price_Per_Reel_EUR"].median()

    col4.metric(
        "Tarifa mediana por reel",
        f"{tarifa_mediana:.2f} €".replace(".", ",")
    )

with explorador:
    st.divider()
    st.subheader("Encuentra creadores para tu campaña")

    col_categoria, col_presupuesto = st.columns(2)

    categorias = sorted(instagram["Category"].dropna().unique())

    categoria = col_categoria.selectbox(
        "Categoría de contenido",
        options=categorias,
        index=categorias.index("Beauty")
    )

    presupuesto_maximo = col_presupuesto.number_input(
        "Presupuesto máximo por reel (€)",
        min_value=0.0,
        value=300.0,
        step=50.0
    )

    col_minimo, col_maximo = st.columns(2)

    seguidores_minimos = col_minimo.number_input(
        "Seguidores mínimos",
        min_value=0,
        value=10000,
        step=1000
    )

    seguidores_maximos = col_maximo.number_input(
        "Seguidores máximos",
        min_value=0,
        value=100000,
        step=1000
    )

    candidatos = instagram.iloc[0:0].copy()

    if seguidores_minimos > seguidores_maximos:
        st.warning(
            "Los seguidores mínimos no pueden superar a los máximos."
        )

    else:
        candidatos = instagram[
            (instagram["Category"] == categoria)
            & (instagram["Followers"] >= seguidores_minimos)
            & (instagram["Followers"] <= seguidores_maximos)
            & (instagram["Price_Per_Reel_EUR"] <= presupuesto_maximo)
        ].copy()

        numero_candidatos = candidatos["Influencer_ID"].nunique()

        st.metric("Perfiles que cumplen tu búsqueda", numero_candidatos)

        if candidatos.empty:
            st.info(
                "No hay perfiles con estos criterios. "
                "Prueba a ampliar el presupuesto o el rango de seguidores."
            )

    if seguidores_minimos <= seguidores_maximos and not candidatos.empty:

        columnas_catalogo = {
            "Influencer_Name": "Creador",
            "City": "Ciudad",
            "Language": "Idioma",
            "Followers": "Seguidores",
            "Average_Views_Per_Content": "Visualizaciones medias",
            "Engagement_Rate_Percent": "Engagement (%)",
            "Price_Per_Reel_EUR": "Tarifa por reel (€)"
        }

        tabla_candidatos = (
            candidatos
            .sort_values("Average_Views_Per_Content", ascending=False)
            [list(columnas_catalogo)]
            .rename(columns=columnas_catalogo)
        )

        st.dataframe(
            tabla_candidatos.style.format({
                "Seguidores": lambda x: formato_numero(x),
                "Visualizaciones medias": lambda x: formato_numero(x),
                "Engagement (%)": lambda x: formato_numero(x, 2) + " %",
                "Tarifa por reel (€)": lambda x: formato_numero(x, 2) + " €"
            }),
            hide_index=True
        )

        st.caption(
            "Orden inicial: mayor número de visualizaciones medias. "
            "Son datos históricos, no resultados garantizados de una campaña."
        )

with comparador:
    st.divider()
    st.subheader("Compara tus candidatos")

    if seguidores_minimos <= seguidores_maximos and not candidatos.empty:

        nombres_creadores = candidatos.set_index(
            "Influencer_ID"
        )["Influencer_Name"].to_dict()

        seleccionados = st.multiselect(
            "Selecciona hasta tres perfiles",
            options=candidatos["Influencer_ID"].tolist(),
            max_selections=3,
            format_func=lambda identificador: (
                f"{nombres_creadores[identificador]} · {identificador}"
            )
        )

        if len(seleccionados) > 3:
            st.warning("Selecciona un máximo de tres perfiles.")

        elif seleccionados:
            comparacion = (
                candidatos
                .set_index("Influencer_ID")
                .loc[seleccionados, list(columnas_catalogo)]
                .rename(columns=columnas_catalogo)
            )

            # Creamos una copia para dar formato sin cambiar los datos numéricos
            comparacion_visual = comparacion.copy()

            for columna in ["Seguidores", "Visualizaciones medias"]:
                comparacion_visual[columna] = comparacion_visual[columna].map(
                    lambda valor: f"{valor:,.0f}".replace(",", ".")
                )

            comparacion_visual["Engagement (%)"] = (
                comparacion_visual["Engagement (%)"].map(
                    lambda valor: f"{valor:.2f}".replace(".", ",") + " %"
                )
            )

            comparacion_visual["Tarifa por reel (€)"] = (
                comparacion_visual["Tarifa por reel (€)"].map(
                    lambda valor: (
                        f"{valor:,.2f}"
                        .replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                        + " €"
                    )
                )
            )

            st.dataframe(
                comparacion_visual.assign(
                    Creador=(
                        comparacion_visual["Creador"]
                        + " · "
                        + comparacion_visual.index.astype(str)
                    )
                ).set_index("Creador").T
            )

            st.subheader("Coste de esta selección")

            coste_seleccion = comparacion["Tarifa por reel (€)"].sum()

            presupuesto_campana = st.number_input(
                "Presupuesto total para honorarios de creadores (€)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="presupuesto_campana"
            )

            saldo = presupuesto_campana - coste_seleccion

            col_coste, col_saldo = st.columns(2)

            col_coste.metric(
                "Un reel por creador",
                formato_numero(coste_seleccion, 2) + " €"
            )

            col_saldo.metric(
                "Presupuesto restante" if saldo >= 0 else "Importe excedido",
                formato_numero(abs(saldo), 2) + " €"
            )

            if saldo >= 0:
                st.success("La selección encaja en el presupuesto indicado.")
            else:
                st.warning(
                    "La selección supera el presupuesto. "
                    "Revisa los candidatos o ajusta el importe."
                )

            st.caption(
                "Cálculo basado en las tarifas registradas: un reel por creador. "
                "No contempla costes adicionales ni condiciones que no figuran "
                "en el catálogo. Seleccionar un perfil no confirma su disponibilidad."
            )

        else:
            st.info("Elige dos o tres perfiles para compararlos.")

    else:
        st.info("Ajusta los filtros para encontrar candidatos que comparar.")

with estimador:
    st.divider()
    st.subheader("Estimador de tarifas")

    st.write(
        "Obtén una referencia de tarifa basada en las características "
        "del perfil. La estimación sirve como apoyo para la negociación."
    )


    nombres_catalogo = instagram.set_index(
        "Influencer_ID"
    )["Influencer_Name"].to_dict()

    perfil_estimador = st.selectbox(
        "Elige un perfil para probar el estimador",
        options=instagram["Influencer_ID"].tolist(),
        format_func=lambda identificador: (
            f"{nombres_catalogo[identificador]} · {identificador}"
        ),
        key="perfil_estimador"
    )

    if st.button("Estimar tarifa"):
        datos_perfil = instagram[
            instagram["Influencer_ID"] == perfil_estimador
        ].copy()

        try:
            tarifa_estimada = predecir_tarifas(
                datos_perfil,
                paquete_modelo
            )[0]

            tarifa_registrada = datos_perfil[
                "Price_Per_Reel_EUR"
            ].iloc[0]

            col_registrada, col_estimada = st.columns(2)

            col_registrada.metric(
                "Tarifa registrada",
                f"{tarifa_registrada:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".") + " €"
            )

            col_estimada.metric(
                "Tarifa estimada",
                f"{tarifa_estimada:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".") + " €"
            )

            st.caption(
                "La diferencia no demuestra que un perfil sea caro o barato. "
                "El modelo no contempla todas las condiciones de una colaboración."
            )

        except ValueError as error:
            st.error(f"No se ha podido calcular la estimación: {error}")

    st.caption("Un perfil del catálogo puede haber formado parte del entrenamiento. Esta consulta no sustituye la evaluación de prueba.")

    with st.expander("Comprobación de consistencia · revisión del proyecto"):
        st.write(
            "Comprueba el perfil elegido arriba. Primero conserva sus 11 valores exactos; "
            "después recalcula el engagement como hace el formulario. "
            "Esta comprobación verifica la preparación, no mide la precisión del modelo."
        )
        if st.button("Comprobar ambas entradas", key="comprobar_consistencia"):
            origen = instagram.loc[
                instagram["Influencer_ID"] == perfil_estimador,
                paquete_modelo["variables"]
            ].copy()
            valores = origen.iloc[0].to_dict()
            reconstruida = construir_entrada(valores, paquete_modelo["variables"])
            diferencias = [
                columna for columna in paquete_modelo["variables"]
                if origen.iloc[0][columna] != reconstruida.iloc[0][columna]
            ]
            try:
                pred_original = float(predecir_tarifas(origen, paquete_modelo)[0])
                pred_reconstruida = float(predecir_tarifas(reconstruida, paquete_modelo)[0])
                diferencia = abs(pred_original - pred_reconstruida)
                if not diferencias and diferencia <= 0.000001:
                    st.success("Mismos 11 valores: misma estimación. Preparación consistente.")
                else:
                    st.warning("Hay diferencias que revisar entre las entradas.")
                    st.write("Variables diferentes:", diferencias)
                st.write("Estimación original:", formato_numero(pred_original, 2) + " €")
                st.write("Estimación reconstruida:", formato_numero(pred_reconstruida, 2) + " €")
                st.write("Diferencia absoluta:", formato_numero(diferencia, 6) + " €")

                engagement_calculado = round(
                    (float(valores["Average_Likes"]) + float(valores["Average_Comments"]))
                    / float(valores["Followers"]) * 100, 2
                )
                valores["Engagement_Rate_Percent"] = engagement_calculado
                entrada_calculada = construir_entrada(valores, paquete_modelo["variables"])
                pred_calculada = float(predecir_tarifas(entrada_calculada, paquete_modelo)[0])
                st.write("Engagement registrado:", formato_numero(origen.iloc[0]["Engagement_Rate_Percent"], 2) + " %")
                st.write("Engagement calculado:", formato_numero(engagement_calculado, 2) + " %")
                st.write("Estimación con engagement calculado:", formato_numero(pred_calculada, 2) + " €")
                st.caption("Si cambia el engagement, las entradas ya no son idénticas y la predicción puede cambiar.")
            except ValueError as error:
                st.error(f"No se ha podido completar la comprobación: {error}")
    st.divider()
    st.subheader("Estima la tarifa de un perfil nuevo")

    st.write(
        "Introduce las métricas del creador usando el mismo conjunto "
        "de publicaciones para calcular todas las medias."
    )

    with st.form("formulario_nuevo_perfil"):

        col1, col2, col3 = st.columns(3)

        nueva_categoria = col1.selectbox(
            "Categoría",
            options=paquete_modelo["categorias"]["Category"]
        )

        nueva_ciudad = col2.selectbox(
            "Ciudad del creador",
            options=paquete_modelo["categorias"]["City"]
        )

        nuevo_idioma = col3.selectbox(
            "Idioma",
            options=paquete_modelo["categorias"]["Language"]
        )

        col1, col2 = st.columns(2)

        nuevos_seguidores = col1.number_input(
            "Seguidores",
            min_value=1,
            value=30000,
            step=1000
        )

        nuevas_visualizaciones = col2.number_input(
            "Visualizaciones medias por contenido",
            min_value=0,
            value=15000,
            step=1000
        )

        col1, col2 = st.columns(2)

        nuevos_likes = col1.number_input(
            "Likes medios",
            min_value=0,
            value=1000,
            step=50
        )

        nuevos_comentarios = col2.number_input(
            "Comentarios medios",
            min_value=0,
            value=50,
            step=10
        )

        col1, col2 = st.columns(2)

        nuevos_compartidos = col1.number_input(
            "Compartidos medios",
            min_value=0,
            value=30,
            step=10
        )

        nuevos_guardados = col2.number_input(
            "Guardados medios",
            min_value=0,
            value=20,
            step=10
        )

        publicaciones_analizadas = st.number_input(
            "Número de publicaciones analizadas",
            min_value=1,
            value=30,
            step=1
        )

        st.caption(
            "El engagement se calcula como "
            "(likes medios + comentarios medios) / seguidores × 100. "
            "Los valores iniciales son un ejemplo editable."
        )

        calcular_tarifa = st.form_submit_button("Calcular tarifa estimada")


    if calcular_tarifa:

        nuevo_engagement = round(
            (nuevos_likes + nuevos_comentarios)
            / nuevos_seguidores * 100,
            2
        )

        nuevo_perfil = construir_entrada({
            "Category": nueva_categoria,
            "City": nueva_ciudad,
            "Language": nuevo_idioma,
            "Followers": nuevos_seguidores,
            "Average_Likes": nuevos_likes,
            "Average_Comments": nuevos_comentarios,
            "Average_Shares": nuevos_compartidos,
            "Average_Saves": nuevos_guardados,
            "Number_of_Posts_Analyzed": publicaciones_analizadas,
            "Average_Views_Per_Content": nuevas_visualizaciones,
            "Engagement_Rate_Percent": nuevo_engagement
        }, paquete_modelo["variables"])

        try:
            estimacion_nueva = predecir_tarifas(
                nuevo_perfil,
                paquete_modelo
            )[0]

            precio_formateado = (
                f"{estimacion_nueva:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            st.metric(
                "Tarifa estimada por reel",
                precio_formateado + " €"
            )

            st.caption(
                "Engagement utilizado: "
                + f"{nuevo_engagement:.2f}".replace(".", ",")
                + " %"
            )

            st.info(
                "Referencia basada en el catálogo del mercado indio. "
                "La tarifa final también depende del contenido, los derechos "
                "de uso, la exclusividad y otras condiciones de la colaboración."
            )

        except ValueError as error:
            st.error(f"No se ha podido calcular la tarifa: {error}")
