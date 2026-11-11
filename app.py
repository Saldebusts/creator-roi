import streamlit as st
from pathlib import Path
import pandas as pd
import joblib
import altair as alt
from html import escape
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


st.set_page_config(page_title="SEÑAL · Creator Intelligence", page_icon="◉", layout="wide", initial_sidebar_state="expanded")

# Identidad visual. Los cálculos y el modelo se mantienen separados del estilo.
st.markdown("""
<style>
:root{color-scheme:dark}
.stApp{background:#090b0b;color:#f5f6f2}
[data-testid="stHeader"]{background:#090b0b}
[data-testid="stSidebar"]{background:#101212;border-right:1px solid #2d3231}
[data-testid="stMainBlockContainer"]{padding-top:5rem;max-width:1500px}
h1,h2,h3{color:#f5f6f2!important;letter-spacing:-.035em}
h1{font-size:2.7rem!important;line-height:1.13!important}
[data-testid="stMetric"]{background:#141717;border:1px solid #2d3231;border-top:2px solid #4a5839;border-radius:10px;padding:18px 20px}
[data-testid="stMetricValue"]{font-size:1.85rem!important;color:#f5f6f2}
[data-testid="stMetricLabel"]{color:#b6bfba}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{color:#a7aeac!important}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#2d3231!important}
.st-key-logo{margin-bottom:28px}
.brand{font-size:44px;font-weight:850;letter-spacing:-2px;line-height:1.1;color:#fff}.brand span{color:#c3f564}
.brand-tag{font-size:10px;letter-spacing:2.4px;color:#a7aeac;margin-top:10px}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:2px;color:#c3f564;text-transform:uppercase;margin:10px 0 16px}
.hero-title{font-size:clamp(36px,4vw,62px);font-weight:780;line-height:1.08;letter-spacing:-2.3px;margin:12px 0 24px;color:#fff}.hero-title span{color:#c3f564}
.lead{font-size:17px;line-height:1.7;color:#b3bcb6;max-width:680px;margin-bottom:20px}
.hero-card{background:linear-gradient(145deg,#20261d,#151918);border:1px solid #384335;border-radius:12px;padding:27px;margin:8px 0 15px}.hero-card h3{font-size:23px;line-height:1.4;margin:8px 0 20px}.hero-card p{color:#c3ccc4;font-size:14px}.hero-card b{color:#c3f564;margin-right:9px}
.insight{background:#20291b;border-left:3px solid #c3f564;border-radius:0 6px 6px 0;padding:16px;color:#d4e2c8;font-size:14px;margin:14px 0 22px}
.step{border-top:2px solid #414f35;padding:17px 0}.step b{color:#c3f564;font-size:12px}.step h3{font-size:19px;margin:12px 0}.step p{color:#a7aeac;font-size:14px}
.nav-footer{font-size:12px;color:#9aa59e;border-top:1px solid #303631;margin-top:35px;padding-top:20px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px;border-radius:7px}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#232d1b;border-left:3px solid #c3f564}
[data-testid="stBaseButton-primary"]{background:#c3f564;color:#11180b;border:1px solid #c3f564;font-weight:700}
[data-testid="stBaseButton-secondary"]{border-color:#46533d;color:#edf5e8}
@media(max-width:760px){.hero-title{font-size:39px}h1{font-size:2rem!important}}
</style>
""", unsafe_allow_html=True)

PAGINAS = ["01 · El proyecto", "02 · Datos y metodología", "03 · Análisis del catálogo", "04 · Diseña tu campaña", "05 · Estima una tarifa", "06 · Próximos pasos y cierre"]

def navegar(pagina):
    st.session_state["pagina"] = pagina


def nota(texto):
    st.markdown('<div class="insight">'+escape(texto)+'</div>', unsafe_allow_html=True)


def grafico_estilo(grafico):
    return (grafico.configure(background="#141717")
            .configure_axis(labelColor="#b8c4ba", titleColor="#d9e1d9", gridColor="#2b332d", domain=False, labelFontSize=12, titleFontSize=12)
            .configure_view(stroke=None)
            .configure_legend(labelColor="#cbd5cd",titleColor="#cbd5cd"))

with st.sidebar:
    st.markdown('<div class="brand">SEÑAL<span>.</span></div><div class="brand-tag">CREATOR INTELLIGENCE</div>', unsafe_allow_html=True)
    st.write("")
    pagina = st.radio("Tu recorrido", PAGINAS, key="pagina")
    st.markdown('<div class="nav-footer"><b>Encuentra tu próxima señal.</b><br><br>Proyecto de Salvador Cruz<br>Ironhack · Data Analytics<br><br>Evolución de CreatorROI</div>',unsafe_allow_html=True)

carpeta_proyecto = Path(__file__).resolve().parent
ruta_datos = carpeta_proyecto / "data" / "processed" / "instagram_preparado.csv"
if not ruta_datos.exists():
    st.error("No se encuentra data/processed/instagram_preparado.csv. Coloca app.py en la raíz de tu proyecto.")
    st.stop()
instagram = cargar_catalogo(ruta_datos, ruta_datos.stat().st_mtime_ns)
st.caption("SEÑAL / " + pagina.split(" · ",1)[1])

if pagina == PAGINAS[0]:
    izquierda, derecha = st.columns([1.45,1], gap="large")
    with izquierda:
        st.markdown('<div class="eyebrow">Inteligencia para elegir creadores</div><div class="hero-title">Encuentra la señal.<br><span>Elige con criterio.</span></div><p class="lead">Transforma las métricas en contexto. Explora creadores, compara candidatos y negocia con una referencia de tarifa.</p>', unsafe_allow_html=True)
        st.button("Explorar el análisis →", type="primary", on_click=navegar, args=(PAGINAS[2],))
        st.caption("7.800 perfiles de Instagram · Mercado indio")
    with derecha:
        st.markdown('<div class="hero-card"><div class="eyebrow">La pregunta de negocio</div><h3>¿Cómo elegir un creador cuando tienes un presupuesto limitado?</h3><p><b>01</b> Entiende las diferencias del catálogo</p><p><b>02</b> Compara perfiles que encajan</p><p><b>03</b> Orienta la negociación de la tarifa</p></div>', unsafe_allow_html=True)
    st.write("")
    a,b,c,d=st.columns(4)
    a.metric("Perfiles de Instagram",formato_numero(instagram.Influencer_ID.nunique()))
    b.metric("Categorías",instagram.Category.nunique())
    c.metric("Ciudades de los creadores",instagram.City.nunique())
    d.metric("Tarifa mediana por reel",formato_numero(instagram.Price_Per_Reel_EUR.median(),2)+" €")
    st.write("")
    a,b=st.columns(2,gap="large")
    with a, st.container(border=True):
        st.caption("QUIÉN ESTÁ DETRÁS")
        st.subheader("Cada métrica cuenta una parte.")
        st.write("SEÑAL conecta el análisis de datos con el influencer marketing. Ayuda a interpretar métricas, seleccionar perfiles y orientar una negociación con más contexto.")
        st.caption("Creado por Salvador Cruz como proyecto académico de Data Analytics en Ironhack. Evolución de CreatorROI.")
    with b, st.container(border=True):
        st.caption("PARA QUIÉN LO CONSTRUIMOS")
        st.subheader("Una herramienta para marcas y agencias.")
        st.write("Un recorrido desde la comprensión del catálogo hasta una selección de candidatos ajustada a una campaña.")
        st.caption("Las visualizaciones son históricas. La herramienta no estima ventas ni el retorno de una campaña.")
    st.subheader("Primero entendemos. Después decidimos.")
    for col,n,t,d in zip(st.columns(3),["01 / EXPLORAR","02 / SELECCIONAR","03 / ESTIMAR"],["Lee el mercado","Construye tu campaña","Prepara la negociación"],["Descubre dónde hay más opciones y cómo se distribuyen las tarifas.","Filtra candidatos, compara métricas y revisa el coste de tu selección.","Obtén una referencia de tarifa basada en las características del perfil."]):
        col.markdown(f'<div class="step"><b>{n}</b><h3>{t}</h3><p>{d}</p></div>',unsafe_allow_html=True)

elif pagina == PAGINAS[2]:
    st.markdown('<div class="eyebrow">03 / Conoce el catálogo</div>',unsafe_allow_html=True)
    st.title("Antes de elegir, entiende los datos.")
    st.write("Las categorías, las tarifas y sus diferencias dan contexto a tu próxima selección.")
    categoria_analisis = st.selectbox("Categoría del análisis",["Todo el catálogo"]+sorted(instagram.Category.dropna().unique()),key="categoria_analisis")
    datos_analisis = instagram if categoria_analisis == "Todo el catálogo" else instagram[instagram.Category==categoria_analisis]
    precios=datos_analisis.Price_Per_Reel_EUR
    a,b,c,d=st.columns(4)
    a.metric("Perfiles seleccionados",formato_numero(len(datos_analisis)))
    b.metric("Ciudades de los creadores",datos_analisis.City.nunique())
    c.metric("Tarifa mediana",formato_numero(precios.median(),2)+" €")
    d.metric("Perfiles de hasta 300 €",formato_numero((precios<=300).mean()*100,1)+" %")
    st.caption("La ciudad es la ubicación del creador; no describe necesariamente dónde vive su audiencia.")
    resumen=(instagram.groupby("Category").agg(Perfiles=("Influencer_ID","nunique"),Tarifa=("Price_Per_Reel_EUR","median")).reset_index())
    izquierda,derecha=st.columns(2,gap="large")
    with izquierda, st.container(border=True):
        modo=st.radio("Comparar categorías por",["Número de perfiles","Tarifa mediana"],horizontal=True)
        campo="Perfiles" if modo=="Número de perfiles" else "Tarifa"
        st.subheader("¿Dónde hay más opciones?" if campo=="Perfiles" else "¿Qué categorías cuestan más?")
        st.caption("Comparativa de las 15 categorías · catálogo completo")
        resumen["Etiqueta"]=resumen[campo].map(lambda x:formato_numero(x,0 if campo=="Perfiles" else 2)+(" €" if campo=="Tarifa" else ""))
        orden=resumen.sort_values(campo,ascending=False).Category.tolist()
        base=alt.Chart(resumen).encode(y=alt.Y("Category:N",sort=orden,title=None,axis=alt.Axis(labelLimit=140)),x=alt.X(campo+":Q",title="Perfiles" if campo=="Perfiles" else "Tarifa mediana (€)",scale=alt.Scale(domain=[0,float(resumen[campo].max())*1.24])),tooltip=[alt.Tooltip("Category:N",title="Categoría"),alt.Tooltip("Etiqueta:N",title=modo)])
        barras=base.mark_bar(size=14,cornerRadiusEnd=3).encode(color=alt.condition(alt.datum.Category==categoria_analisis,alt.value("#e5b66f"),alt.value("#b4df70")))
        etiquetas=base.mark_text(align="left",dx=6,color="#edf5e8").encode(text="Etiqueta:N")
        st.altair_chart(grafico_estilo((barras+etiquetas).properties(height=450)),use_container_width=True)
        lider=resumen.sort_values(campo,ascending=False).iloc[0]
        nota(f"{lider.Category} encabeza esta comparación: {lider.Etiqueta}. La categoría aporta contexto, pero no explica por sí sola la tarifa.")
    with derecha, st.container(border=True):
        st.subheader("¿Qué tarifas predominan?")
        st.caption(categoria_analisis+" · número de perfiles por tramo")
        tramos=["Menos de 100 €","100–<300 €","300–<1.000 €","1.000–<5.000 €","5.000 € o más"]
        grupos=pd.cut(precios,bins=[0,100,300,1000,5000,float("inf")],labels=tramos,right=False)
        distribucion=grupos.value_counts(sort=False).rename_axis("Tramo").reset_index(name="Perfiles")
        distribucion["Etiqueta"]=distribucion.Perfiles.map(formato_numero)
        base=alt.Chart(distribucion).encode(y=alt.Y("Tramo:N",sort=tramos,title=None,axis=alt.Axis(labelLimit=150)),x=alt.X("Perfiles:Q",title="Perfiles",scale=alt.Scale(domain=[0,int(distribucion.Perfiles.max())*1.25])),tooltip=["Tramo:N","Perfiles:Q"])
        chart=base.mark_bar(color="#b4df70",size=23,cornerRadiusEnd=3)+base.mark_text(align="left",dx=6,color="#edf5e8").encode(text="Etiqueta:N")
        st.altair_chart(grafico_estilo(chart.properties(height=270)),use_container_width=True)
        a,b=st.columns(2)
        a.metric("Mediana",formato_numero(precios.median(),2)+" €")
        b.metric("Media",formato_numero(precios.mean(),2)+" €")
        nota("La media es "+formato_numero(precios.mean()/precios.median(),1)+" veces la mediana. Las tarifas altas elevan el promedio; por eso mostramos ambas medidas.")
    with st.container(border=True):
        st.subheader("¿Qué tarifa es habitual según el tamaño del creador?")
        st.caption(categoria_analisis + " · tarifa mediana por reel y número de perfiles en cada grupo")
        orden = ["Menos de 10.000", "10.000–<50.000", "50.000–<100.000", "100.000–<500.000", "500.000–<1 millón", "1 millón o más"]
        tabla_grupos = datos_analisis[["Influencer_ID", "Followers", "Price_Per_Reel_EUR"]].copy()
        for campo in ["Followers", "Price_Per_Reel_EUR"]:
            tabla_grupos[campo] = pd.to_numeric(tabla_grupos[campo], errors="coerce")
        tabla_grupos = tabla_grupos.replace([float("inf"), -float("inf")], float("nan")).dropna()
        tabla_grupos = tabla_grupos[(tabla_grupos.Followers >= 0) & (tabla_grupos.Price_Per_Reel_EUR >= 0)]
        tabla_grupos["Grupo"] = pd.cut(tabla_grupos.Followers,
            bins=[0, 10000, 50000, 100000, 500000, 1000000, float("inf")],
            labels=orden, right=False)
        resumen = tabla_grupos.groupby("Grupo", observed=True).agg(
            Mediana=("Price_Per_Reel_EUR", "median"),
            Perfiles=("Influencer_ID", "nunique")
        ).reset_index()
        if resumen.empty:
            st.info("No hay datos válidos para comparar estos grupos.")
        else:
            resumen["Grupo"] = resumen["Grupo"].astype(str)
            resumen["Tarifa"] = resumen.Mediana.map(lambda x: formato_numero(x, 2) + " €")
            resumen["Etiqueta"] = resumen.apply(lambda r: r.Tarifa + " · " + formato_numero(r.Perfiles) + " perfiles", axis=1)
            base = alt.Chart(resumen).encode(
                y=alt.Y("Grupo:N", sort=orden, title="Seguidores", axis=alt.Axis(labelLimit=180)),
                x=alt.X("Mediana:Q", title="Tarifa mediana por reel (€)",
                    scale=alt.Scale(domain=[0, max(float(resumen.Mediana.max()) * 1.65, 1)])),
                tooltip=[alt.Tooltip("Grupo:N", title="Seguidores"), alt.Tooltip("Tarifa:N", title="Tarifa mediana"), "Perfiles:Q"]
            )
            chart = base.mark_bar(color="#c3f564", size=28, cornerRadiusEnd=3) + base.mark_text(
                align="left", dx=7, color="#edf5e8", fontSize=12
            ).encode(text="Etiqueta:N")
            st.altair_chart(grafico_estilo(chart.properties(height=330)), use_container_width=True)
            st.caption("Grupos definidos por seguidores, de menor a mayor. La mediana divide las tarifas del grupo en dos mitades. Los grupos sin perfiles no se muestran.")
            if (resumen.Perfiles < 10).any():
                st.caption("Hay grupos con menos de 10 perfiles: interpreta su tarifa con especial cautela por el tamaño de la muestra.")
            nota("Utiliza estas cifras como referencia dentro de la categoría elegida. No son una tarifa recomendada: el contenido, la audiencia y las condiciones de colaboración también importan.")
    ejemplo=instagram[(instagram.Category=="Beauty")&instagram.Followers.between(10000,100000)&(instagram.Price_Per_Reel_EUR<=300)]
    nota("Del análisis a la decisión: "+formato_numero(len(ejemplo))+" perfiles de Beauty tienen entre 10.000 y 100.000 seguidores y una tarifa de hasta 300 € por reel. Este ejemplo es independiente del filtro de análisis.")
    st.button("Diseñar una campaña →",type="primary",on_click=navegar,args=(PAGINAS[3],))

elif pagina == PAGINAS[3]:
    st.title("Diseña tu campaña.")
    st.write("Encuentra perfiles, compara sus métricas y comprueba el coste de tu selección.")
    st.divider()
    st.subheader("Encuentra creadores para tu campaña")

    col_categoria, col_presupuesto = st.columns(2)

    ajustes = st.session_state.get("ajustes_campana", {})
    categorias = sorted(instagram["Category"].dropna().unique())

    categoria = col_categoria.selectbox(
        "Categoría de contenido",
        options=categorias,
        index=categorias.index(ajustes.get("categoria", "Beauty"))
    )

    presupuesto_maximo = col_presupuesto.number_input(
        "Presupuesto máximo por reel (€)",
        min_value=0.0,
        value=ajustes.get("presupuesto", 300.0),
        step=50.0
    )

    col_minimo, col_maximo = st.columns(2)

    seguidores_minimos = col_minimo.number_input(
        "Seguidores mínimos",
        min_value=0,
        value=ajustes.get("minimo", 10000),
        step=1000
    )

    seguidores_maximos = col_maximo.number_input(
        "Seguidores máximos",
        min_value=0,
        value=ajustes.get("maximo", 100000),
        step=1000
    )

    st.session_state["ajustes_campana"] = {"categoria": categoria, "presupuesto": presupuesto_maximo, "minimo": seguidores_minimos, "maximo": seguidores_maximos}
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
    st.divider()
    st.subheader("Compara tus candidatos")

    if seguidores_minimos <= seguidores_maximos and not candidatos.empty:

        nombres_creadores = candidatos.set_index(
            "Influencer_ID"
        )["Influencer_Name"].to_dict()

        seleccionados = st.multiselect(
            "Selecciona hasta tres perfiles",
            options=candidatos["Influencer_ID"].tolist(),
            default=[x for x in st.session_state.get("seleccion_guardada", []) if x in candidatos["Influencer_ID"].tolist()],
            max_selections=3,
            format_func=lambda identificador: (
                f"{nombres_creadores[identificador]} · {identificador}"
            )
        )

        st.session_state["seleccion_guardada"] = seleccionados

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
                value=st.session_state.get("presupuesto_guardado", 1000.0),
                step=100.0,
                key="presupuesto_campana"
            )

            st.session_state["presupuesto_guardado"] = presupuesto_campana
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
elif pagina == PAGINAS[4]:
    st.title("Estima una tarifa.")
    ruta_modelo = carpeta_proyecto / "modelos" / "bagging_creatorroi.joblib"
    if not ruta_modelo.exists():
        st.error("No se encuentra modelos/bagging_creatorroi.joblib. Conserva tu modelo original en esa carpeta.")
        st.stop()
    paquete_modelo = cargar_paquete(ruta_modelo, ruta_modelo.stat().st_mtime_ns)
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

elif pagina == PAGINAS[1]:
    st.title("Datos y metodología.")
    st.write("Cómo pasamos del archivo original a una herramienta para tomar decisiones.")
    with st.expander("Origen y alcance del catálogo"):
        st.write(
            "Fuente: dataset CreatorROI Influencers. El archivo original contiene 10.000 perfiles "
            "de varias plataformas; el proyecto trabaja con el subconjunto de Instagram del mercado indio."
        )
        st.write(
            "Los importes en euros facilitan la lectura. La conversión usada en el proyecto "
            "es fija: 1 EUR = 106,0395 INR. No convierte estas tarifas en precios del mercado español."
        )
        st.caption("La ciudad corresponde al creador; no describe necesariamente dónde vive su audiencia.")

    st.markdown("### 01 · Cómo organizamos los datos")
    st.write(
        "**SQL organiza y consulta los perfiles que ya conocemos.** La tabla perfiles "
        "se relaciona con categorías, ciudades e idiomas mediante claves externas. "
        "Así evitamos repetir sus nombres en cada perfil y mantenemos referencias consistentes."
    )
    st.write(
        "Las consultas combinan esas tablas con JOIN y aplican criterios comerciales: "
        "categoría, seguidores y presupuesto. La tabla creadores conserva la importación original."
    )
    ruta_diagrama = carpeta_proyecto / "docs" / "diagrama_relacional.png"
    with st.expander("Ver el diagrama de relaciones"):
        if ruta_diagrama.exists():
            st.image(str(ruta_diagrama), caption="Categorías, ciudades e idiomas: relaciones de uno a muchos con perfiles.")
        else:
            st.info("El diagrama todavía no está disponible en esta copia de la aplicación.")
        st.caption(
            "Influencer_ID identifica cada perfil. categoria_id, ciudad_id e idioma_id "
            "conectan con las claves de las tablas de referencia."
        )
    st.caption(
        "La aplicación carga el CSV preparado con Python. Tableau utiliza una exportación "
        "de SQL; no hay una conexión en directo entre esta aplicación y MySQL."
    )

    st.markdown("### 02 · Cómo evaluamos el modelo")
    st.write(
        "**El modelo estima una tarifa por reel a partir de las características del perfil.** "
        "Puede valorar una nueva combinación de datos sin que ese perfil esté guardado en SQL. "
        "Su resultado es una referencia para negociar, no una predicción de ventas o de ROI."
    )
    st.write(
        "Se separaron 4.680 perfiles para entrenamiento, 1.560 para validación y 1.560 para prueba. "
        "La validación permitió comparar y ajustar modelos; la prueba se reservó para evaluar "
        "el modelo elegido sobre datos que no se usaron para entrenarlo ni seleccionarlo."
    )
    st.caption(
        "Las cifras siguientes son los resultados registrados en el notebook del proyecto; "
        "no se recalculan ni se reentrena el modelo al abrir la aplicación."
    )
    col_base, col_modelo = st.columns(2)
    col_base.metric("MAE en prueba · referencia", "1.234,42 €")
    col_modelo.metric("MAE en prueba · Bagging ajustado", "364,19 €")
    st.write(
        "**Cómo leer el MAE:** en el conjunto de prueba, la diferencia absoluta entre "
        "tarifa estimada y registrada fue de 364,19 € de media. Es menor que la referencia, "
        "pero no significa que cada predicción tenga ese error ni que exista un margen garantizado de ±364,19 €."
    )
    st.write(
        "La amplitud de precios del catálogo importa: un error de cientos de euros puede "
        "ser especialmente relevante para perfiles económicos. Por eso mostramos la estimación "
        "junto al contexto del perfil y no como un precio que deba aceptarse automáticamente."
    )
    with st.expander("Ver la comparación de modelos en validación"):
        comparativa_modelos = pd.DataFrame({
            "Modelo": ["Bagging ajustado", "Bagging", "Random Forest", "Random Forest ajustado",
                       "Pasting", "Gradient Boosting", "Árbol de decisión", "AdaBoost",
                       "Regresión lineal", "Referencia", "KNN"],
            "MAE de validación (€)": [295.24, 296.32, 297.17, 301.14, 306.67,
                                      315.85, 396.31, 486.42, 490.52, 1046.43, 1395.01]
        })
        st.dataframe(
            comparativa_modelos.style.format({
                "MAE de validación (€)": lambda x: formato_numero(x, 2) + " €"
            }), hide_index=True
        )
        st.caption(
            "Menor MAE es mejor. Bagging ajustado obtuvo el menor error de validación. "
            "Su MAE de prueba fue 364,19 €: corresponde a otro conjunto de perfiles."
        )
    with st.expander("Qué información usa para estimar"):
        st.write(
            "Categoría, ciudad, idioma, seguidores, likes, comentarios, compartidos, "
            "guardados, publicaciones analizadas, visualizaciones medias y engagement: 11 variables."
        )
        st.write(
            "No utiliza precios como variables de entrada. Las categorías, columnas y "
            "escalado aprendidos en entrenamiento se conservan con el modelo para preparar "
            "las nuevas entradas de la misma forma."
        )

    st.markdown("### 03 · Análisis complementario en Tableau")
    st.write(
        "El libro contiene dos dashboards: panorama del catálogo y selección de campaña. "
        "Permiten explorar la oferta, las tarifas y los candidatos que encajan con unos criterios."
    )
    ruta_tableau = carpeta_proyecto / "tableau" / "creator_roi_dashboard.twbx"
    if ruta_tableau.exists():
        st.download_button(
            "Descargar dashboards de Tableau",
            data=ruta_tableau.read_bytes(),
            file_name="creator_roi_dashboard.twbx",
            mime="application/octet-stream",
            key="descargar_tableau"
        )
        st.caption("Libro empaquetado (.twbx). Requiere una aplicación compatible de Tableau para abrirlo.")
    else:
        st.info("El libro de Tableau todavía no está disponible en esta copia de la aplicación.")

    st.markdown("### Qué podemos decidir y qué debemos revisar")
    st.write(
        "**Podemos:** preseleccionar perfiles, comparar métricas históricas, sumar honorarios "
        "registrados y obtener una referencia de tarifa."
    )
    st.write(
        "**Antes de contratar:** revisar audiencia real, afinidad con la marca, disponibilidad, "
        "derechos de uso, exclusividad y condiciones. No disponemos de ingresos atribuibles "
        "a campañas para calcular un retorno económico."
    )

elif pagina == PAGINAS[5]:
    st.markdown('<div class="eyebrow">06 / Del proyecto a su siguiente etapa</div>', unsafe_allow_html=True)
    st.title("Más contexto. Mejores decisiones.")
    st.write("SEÑAL conecta la exploración de datos, la selección de candidatos y una referencia de tarifa en un mismo recorrido.")

    st.subheader("Qué hemos conseguido")
    for col, titulo, texto in zip(
        st.columns(3),
        ["Entender el catálogo", "Preparar una campaña", "Orientar la negociación"],
        ["Analizar 7.800 perfiles de Instagram, sus categorías, métricas y tarifas.",
         "Filtrar perfiles, comparar hasta tres candidatos y calcular los honorarios de la selección.",
         "Estimar una tarifa por reel con un modelo evaluado sobre datos reservados para prueba."]
    ):
        with col, st.container(border=True):
            st.subheader(titulo)
            st.write(texto)
    nota("Aprendizaje principal: una cifra aislada no basta. La tarifa cobra sentido al compararla con el tipo de perfil, sus métricas y las condiciones de la colaboración.")

    st.subheader("Próximos pasos")
    st.caption("Propuestas de evolución; estas funcionalidades todavía no están implementadas.")
    hoja_ruta = pd.DataFrame({
        "Prioridad": ["01 · Consolidar", "02 · Ampliar", "03 · Evaluar", "04 · Validar"],
        "Siguiente paso": [
            "Publicar y probar la aplicación con usuarios",
            "Incorporar datos recientes y de otros mercados",
            "Evaluar el error por categoría y tramo de tarifa",
            "Conectar la selección con resultados de campañas reales"
        ],
        "Qué aporta": [
            "Comprobar navegación, claridad y utilidad para marcas y agencias.",
            "Disponer de referencias del mercado en el que se va a contratar.",
            "Identificar dónde el modelo funciona mejor y dónde necesita mejoras.",
            "Medir conversiones e ingresos atribuibles antes de estimar retorno económico."
        ]
    })
    st.dataframe(hoja_ruta, hide_index=True, use_container_width=True)

    with st.container(border=True):
        st.subheader("Qué falta antes de una decisión real")
        st.write("Validar la audiencia y la afinidad con la marca, confirmar disponibilidad y acordar derechos de uso, exclusividad y entregables.")
        st.caption("El catálogo corresponde al mercado indio. La conversión a euros no lo convierte en una referencia del mercado español. La estimación no garantiza resultados de una campaña.")

    st.markdown('<div class="hero-card"><div class="eyebrow">SEÑAL · Creator Intelligence</div><h3>Encuentra la señal. Elige con criterio.</h3><p>Datos para preparar mejores preguntas, comparar opciones y negociar con contexto.</p></div>', unsafe_allow_html=True)
    st.caption("Proyecto de Salvador Cruz · Ironhack · Data Analytics")
    st.button("Volver al proyecto →", type="primary", on_click=navegar, args=(PAGINAS[0],))

st.divider()
st.caption("SEÑAL · Proyecto académico de Salvador Cruz · Mercado indio · Conversión fija: 1 EUR = 106,0395 INR. Las tarifas son referencias del catálogo, no presupuestos cerrados.")
