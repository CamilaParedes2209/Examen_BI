import streamlit as st
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import plotly.express as px 
import pygwalker as pyg
import streamlit.components.v1 as components 
from io import BytesIO

st.set_page_config(page_title = "Dashboard Matriculados", layout="wide")

st.title("Dashboard Matriculados en Educacion Superior 2007 -2024")

#carga del data set

@st.cache_data
def cargar_datos(archivo):
    return pd.read_csv(archivo,sep=';', encoding='latin-1', low_memory=False, on_bad_lines='skip')
df = cargar_datos("dataset_Matriculas_2007_2024.csv")

st.write("vista previa df")
df.columns = df.columns.str.strip().str.replace(' ', '_').str.upper()
if 'MATRICULADOS_NO_BINARIO_POR_CARRERA' in df.columns:
    df = df.drop('MATRICULADOS_NO_BINARIO_POR_CARRERA', axis=1)

if 'MATRICULADOS_NO_BINARIO_PRIMER_AÑO' in df.columns:
    df = df.drop('MATRICULADOS_NO_BINARIO_PRIMER_AÑO', axis=1)

if 'PROMEDIO_EDAD_NO_BINARIO' in df.columns:
    df = df.drop('PROMEDIO_EDAD_NO_BINARIO', axis=1)

if 'TOTAL_RANGO_DE_EDAD' in df.columns:
    df = df.drop('TOTAL_RANGO_DE_EDAD', axis=1)

if 'PROVINCIA' in df.columns:
    df = df.drop('PROVINCIA', axis=1)

if 'AÑO' in df.columns:
    df['AÑO_NUM'] = df['AÑO'].astype(str).str.replace('MAT_', '', regex=False)

if "AÑO" in df.columns:
    df = df.drop("AÑO", axis=1)
   
st.dataframe(df.head())

st.write(df.shape)

def convertir_a_excel(df, ARCHIVO ="matriculados"):
        output = BytesIO()
        with pd.ExcelWriter(output,engine = "xlsxwriter") as writer :
            df.to_excel(writer, index=False , sheet_name= ARCHIVO)
        return output.getvalue()


## sidebar : filtros interactivos 

st.sidebar.header("filtros del panel")

AÑO = st.sidebar.multiselect("AÑO MATRICULA",df["AÑO_NUM"].unique())

INSTITUCION = st.sidebar.multiselect("TIPO DE INSTITUCION",df["CLASIFICACIÓN_INSTITUCIÓN_NIVEL_1"].unique(), default = df["CLASIFICACIÓN_INSTITUCIÓN_NIVEL_1"].unique())

REGION = st.sidebar.multiselect("REGION",df["REGIÓN"].unique(), default = df["REGIÓN"].unique())

DURACION_CARRERA = st.sidebar.slider("DURACION CARRERA" ,int(df["DURACIÓN_ESTUDIO_CARRERA"].min()), int(df["DURACIÓN_ESTUDIO_CARRERA"].max()) ,(2,15) )

JORNADA = st.sidebar.radio("TIPO DE JORNADA" , df["JORNADA"].unique())

#aplicar filtros 

df_filtrado = df[ (df["AÑO_NUM"].isin(AÑO) ) &( df["CLASIFICACIÓN_INSTITUCIÓN_NIVEL_1"].isin(INSTITUCION )) & (df["REGIÓN"].isin(REGION))  & (df["DURACIÓN_ESTUDIO_CARRERA"].between ( DURACION_CARRERA[0] , DURACION_CARRERA[1]) )   & (df["JORNADA"] == JORNADA) ]
st.write(df_filtrado.shape)

MENU = st.selectbox("SELECCIONAR UNA SECCION " , ["ANALISIS GENERAL ","EXPLORACION CON PyGWALKER " ] )

if MENU == "ANALISIS GENERAL ":
    #aca crearemos la seccion general
    st.write("ANALISIS GENERAL")

    col1,col2,col3,col4,col5, = st.columns(5)
    
    total = df_filtrado["TOTAL_MATRICULADOS"].sum()
    matriculas_mujeres = df_filtrado["MATRICULADOS_MUJERES_POR_PROGRAMA"].sum()
    matriculas_hombres = df_filtrado["MATRICULADOS_HOMBRES_POR_PROGRAMA"].sum()
    por_matr_mujeres = round((matriculas_mujeres/total) * 100 , 2) if total > 0 else 0
    por_matr_hombres = round((matriculas_hombres/total) * 100 , 2) if total > 0 else 0


    col1.metric("TOTAL MATRICULADOS", total)
    col2.metric("MUJERES MATRICULADAS",matriculas_mujeres)
    col3.metric("HOMBRES MATRICULADOS",matriculas_hombres)
    col4.metric("PORCENTAJE MATRICULAS MUJERES", f"{por_matr_mujeres}%")
    col5.metric("PORCENTAJE MATRICULAS HOMBRES", f"{por_matr_hombres}%")
    
    st.subheader("Distribución de Matrículas por Año")
    df_grouped = df_filtrado.groupby("AÑO_NUM")["TOTAL_MATRICULADOS"].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(
    data=df_grouped,
    x="AÑO_NUM",
    y="TOTAL_MATRICULADOS",
    palette="pastel",
    ax=ax
    )
    ax.set_title("Total de Matriculados por Año")
    ax.set_xlabel("Año")
    ax.set_ylabel("Total Matriculados")
    plt.xticks(rotation=45)
    st.pyplot(fig,use_container_width = True)
    st.write("\nInsight 1.1: El gráfico de líneas muestra la tendencia general de la matrícula.'Se observa una tendencia a la baja desde 2019 al 2022, que podría correlacionarse con factores demográficos o sociales' (Pandemia), y un crecimiento desde el año 2022 en adelante")

 
    st.title("Gráfico de Barras: Matriculados por Año")


# Seleccionar la columna numérica que quieres graficar
    columna = st.selectbox(
        "Selecciona la columna de matrícula para graficar por año:",
        df_filtrado.select_dtypes(include='number').columns
    )

# Agrupar por año y sumar la columna seleccionada
    df_grouped = df_filtrado.groupby("AÑO_NUM")[columna].sum().reset_index()

# Graficar barras
    fig2, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
    data=df_grouped,
    x="AÑO_NUM",
    y=columna,
    palette="pastel",
    ax=ax
    )
    ax.set_title(f"Total de {columna} por Año")
    ax.set_xlabel("Año")
    ax.set_ylabel(f"Total {columna}")
    plt.xticks(rotation=45)

    st.pyplot(fig2,use_container_width = True)

    
    st.title("Gráfico de Barras Multiple: Matriculados por Año")

    columnas_numericas = df_filtrado.select_dtypes(include='number').columns.tolist()

# Multiselect
    columnas_seleccionadas = st.multiselect(
        "Selecciona columnas numéricas para graficar por año:",
        columnas_numericas
    )

# Tipo de agregado
    opcion_agregado = st.selectbox(
        "¿Qué quieres mostrar?",
        ["Suma total", "Promedio", "Mediana"]
    )

    if columnas_seleccionadas:
    # Agrupar por año y calcular el agregado
        if opcion_agregado == "Suma total":
            df_grouped = df_filtrado.groupby("AÑO_NUM")[columnas_seleccionadas].sum().reset_index()
        elif opcion_agregado == "Promedio":
            df_grouped = df_filtrado.groupby("AÑO_NUM")[columnas_seleccionadas].mean().reset_index()
        else:
            df_grouped = df_filtrado.groupby("AÑO_NUM")[columnas_seleccionadas].median().reset_index()

    # Transformar a formato largo para Seaborn (necesario para barras agrupadas)
        df_long = df_grouped.melt(id_vars="AÑO_NUM", value_vars=columnas_seleccionadas,
                              var_name="Variable", value_name="Valor")

    # Crear gráfico de barras agrupadas
        fig3, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(
            data=df_long,
            x="AÑO_NUM",
            y="Valor",
            hue="Variable",
            palette="pastel",
            ax=ax
        )

        ax.set_title(f"{opcion_agregado} por Año")
        ax.set_xlabel("Año")
        ax.set_ylabel(opcion_agregado)
        plt.xticks(rotation=45)
        ax.legend(title="Variable")

        st.pyplot(fig3,use_container_width = True)

    else:
        st.info("Selecciona al menos una columna para mostrar el gráfico de barras por año.")
    
    st.title("Gráfico de Torta: Clasificación Institución Nivel 1")


    if "CLASIFICACIÓN_INSTITUCIÓN_NIVEL_1" in df_filtrado.columns:
        df_pie = df_filtrado["CLASIFICACIÓN_INSTITUCIÓN_NIVEL_1"].value_counts().reset_index()
        df_pie.columns = ["Clasificación", "Cantidad"]

    # Crear gráfico de torta
        fig4, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            df_pie["Cantidad"],
            labels=df_pie["Clasificación"],
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Pastel1.colors
        )
        ax.set_title("Distribución por Clasificación Institución Nivel 1")
        ax.axis("equal")  # Para que sea redonda

        st.pyplot(fig4, use_container_width = True)

    else:
        st.error("La columna 'CLASIFICACIÓN INSTITUCIÓN NIVEL 1' no existe en el DataFrame.")

    tab1,tab2,tab3 = st.tabs(["TABLA","GRAFICOS","ESTADISTICAS"])
    
    with tab1:
        st.dataframe(df_filtrado)
    with tab2:
        fig5 = px.violin(df_filtrado, x = "AÑO_NUM", y = "TOTAL_MATRICULADOS",color = "CARRERA_CLASIFICACIÓN_NIVEL_1", box = True , points = "all")
        st.plotly_chart(fig5, use_container_width = True)
    with tab3:
        st.write("ESTADISTICA DESCRIPTIVA")
        st.dataframe(df_filtrado.describe())
    with st.expander("¿QUE SIGNIFICA CADA COLUMNA?"):
        st.markdown("""
        - `AÑO` : Año del proceso de matricula.
        - `TOTAL MATRICULADOS`: Total de Matriculados por año,universidad y programa.
        - `MATRICULADOS MUJERES POR PROGRAMA`: Cantidad de mujeres matriculadas por programa.
        -  `MATRICULADOS HOMBRES POR PROGRAMA`: Cantidad de hombres matriculados por pograma.
        -  `TOTAL MATRICULADOS PRIMER AÑO`: Total de Matriculados de primer año,universidad y programa.
        -  `MATRICULADOS MUJERES PRIMER AÑO`: Cantidad de mujeres matriculadas en primer año.
        -  `MATRICULADOS HOMBRES PRIMER AÑO`: Cantidad de hombres matriculados en primer año
        -  `CLASIFICACIÓN INSTITUCIÓN NIVEL 1`: Universidad , IP, CFT.
        -  `CLASIFICACIÓN INSTITUCIÓN NIVEL 2`: CFT,IP, Universidades Cruch , Universidades Privadas , Universidades carrera en convenio.
        -  `CLASIFICACIÓN INSTITUCIÓN NIVEL 3`: CFT, CFT Estatales , IP, Universidades carrera en convenio, Universidades Estatales Cruch, Universidades Privadas Cruch, Universidades Privadas.
        -  `CÓDIGO DE INSTITUCIÓN`: Codigo unico de la institucion.
        -  `NOMBRE INSTITUCIÓN`: Nombre de la institucion.
        -  `ACREDITACIÓN INSTITUCIONAL`: Acreditada - No Acreditada.
        -  `REGIÓN`: Region donde se encuentra la facultad o sede .
        -  `PROVINCIA`: Provincia donde se encuentra la facultad o sede.
        -  `COMUNA`: Comuna donde se encuentra la facultad o sede.
        -  `NOMBRE SEDE`: Nombre de la sede.
        -  `NOMBRE CARRERA`: Nombre de la carrera.
        -  `ÁREA DEL CONOCIMIENTO`: Area de conocimiento.
        -  `CINE-F 1997 ÁREA`: Define áreas de estudio, que incluyen campos generales como educación, humanidades y artes, ciencias sociales, empresariales y jurídicas.
        -  `CINE-F 1997 SUBAREA`: representan campos de estudio específicos dentro de un área general de educación
        -  `ÁREA CARRERA GENÉRICA`: Area generica de la carrera.
        -  `CINE-F 2013 ÁREA`:  Permite agrupar los programas educativos según su área de contenido.
        -  `CINE-F 2013 SUBAREA`: representan campos de estudio específicos dentro de un área general de educación
        -  `NIVEL GLOBAL`: Pregrado, Prosgrado, Postitulo.
        -  `CARRERA CLASIFICACIÓN NIVEL 1`: Clasificacion de la carrera.
        -  `CARRERA CLASIFICACIÓN NIVEL 2`: Carreras profesionales, Carreras tecnicas , Doctorado, Magister, Postitulo.
        -  `MODALIDAD`: No presencial, Presencial, Semipresencial.
        -  `JORNADA`: A distancia, Diurno, Otros, Vespertino , Semipresencial.
        -  `TIPO DE PLAN DE LA CARRERA`: Plan regular , Plan especial, Plan regular de continuidad.
        -  `DURACIÓN ESTUDIO CARRERA`: Duracion formal de la carrera.
        -  `DURACIÓN TOTAL DE CARRERA`: Duracion total de la carrera.
        -  `CÓDIGO CARRERA`: Codigo unico de la carrera
        -  `ACREDITACIÓN CARRERA`: Acreditada, No acreditada, Sin informacion.
        -  `RANGO DE EDAD 15 A 19 AÑOS`: Total matriculados de 15 a 19 años.
        -  `RANGO DE EDAD 20 A 24 AÑOS`: Total matriculados de 20 a 24 años.
        -  `RANGO DE EDAD 25 A 29 AÑOS`: Total matriculados de 25 a 29 años.
        -  `RANGO DE EDAD 30 A 34 AÑOS`: Total matriculados de 30 a 34 años.
        -  `RANGO DE EDAD 35 A 39 AÑOS`: Total matriculados de 35 a 39 años.
        -  `RANGO DE EDAD 40 Y MÁS AÑOS`: Total matriculados de 40 o mas años.
        -  `RANGO DE EDAD SIN INFORMACIÓN`: Total matriculados sin edad informada.
        -  `PROMEDIO EDAD CARRERA`: Promedio de edad por carrera.
        -  `PROMEDIO EDAD MUJER`: Promedio de edad de mujeres matriculadas.
        -  `PROMEDIO EDAD HOMBRE`: Promedio de edad de hombres matriculados.
        -  `PROMEDIO EDAD NO BINARIO`: Promedio de edad de personas no binarias matriculadas.
        -  `TES MUNICIPAL`: Cantidad de estudiantes provenientes de establecimientos categorizados como Corporación Municipal.
        -  `TES PARTICULAR SUBVENCIONADO`: Cantidad de estudiantes provenientes de establecimientos categorizados como Particular Subvencionado.
        -  `TES PARTICULAR PAGADO`: Cantidad de estudiantes provenientes de establecimientos categorizados como Particular Pagado.
        -  `TES CORP. DE ADMINISTRACIÓN DELEGADA`:Cantidad de estudiantes provenientes de establecimientos categorizados como Corporación de Administración Delegada.
        -  `TES SERVICIO LOCAL EDUCACION`: Cantidad de estudiantes provenientes de establecimientos categorizados como Servicio Local de Educación.
        -  `TOTAL TES`: Cantidad total de estudiantes que fueron identificados como provenientes de establecimientos secundarios en el período 2002-2021 (egresados de enseñanza media)
        -  `% COBERTURA TES`: % de estudiantes que fueron identificados en la base de establecimientos secundarios (TOTAL TES/TOTAL MATRICULADOS POR CARRERA)
        -  `TIPO ESTABLECIMIENTO HC`: Cantidad de estudiantes provenientes de un tipo de enseñanza específico: Científico Humanista
        -  `TIPO ESTABLECIMIENTO TP`: Cantidad de estudiantes provenientes de un tipo de enseñanza específico: Técnico Profesional
        -  `CLAS_EST ADULTO`: Cantidad Tipo de estudiantes Adultos provenientes de enseñanza secundaria (egresados de enseñanza media)
        -  `CLAS_EST JOVEN`: Cantidad Tipo de estudiantes Jóvenes provenientes de enseñanza secundaria (egresados de enseñanza media)
            """)
        
    with st.form("FORMULARIO DE FEEDBACK"):
        st.subheader("FEEDBACK DEL USUARIO")

        NOMBRE = st.text_input(" TU NOMBRE")
        COMENTARIO = st.text_area("¿QUE TE PARECIO EL DASHBOARD?")
        PUNTAJA = st.slider("PUNTAJE DE SATISFACCION :" , 1,10,5)

        ENVIAR = st.form_submit_button("ENVIAR")
        
        if ENVIAR:
            # ENVIAR LA INFORMACION A LA BASE DE DATOS 
            st.success(f' GRACIAS {NOMBRE}!! CALIFICASTE A NUESTRO DASHBOARD CON UN {PUNTAJE}/10 ' )

    st.download_button(
    label="DESCARGAR EXCEL",
    data= convertir_a_excel(df_filtrado),
    file_name="Matriculados_filtrado.xlsx",
    mime="application/vnd.openxmlformats.officedocument.spreadsheetml.sheet"
    )



else:

    #creacion con Pygwalker
    st.header("EXPLORACION CON PyGWALKER")
    tab_pyg1,tab_pyg2 = st.tabs(["⚙️ PyGWalker dinámico", "📂 Cargar JSON de PyGWalker"])

    with tab_pyg1:
        pyg_html = pyg.to_html(df_filtrado,return_html = True, dark = "light")
        st.subheader("⚙️ Exploración Dinámica con PyGWalker")
        components.html(pyg_html,height = 800, scrolling = True)

    
    with tab_pyg2:
        st.subheader("📂 Subir archivo JSON de PyGWalker")
        carga = st.file_uploader("Selecciona un archivo json", type = "json")
        
        if carga is not None:
            try:

                json_content = carga.read().decode("utf-8")
                html_json = pyg.to_html(df_filtrado,html_json = True, dark = "ligth" , spec = json_content)
                st.subheader("⚙️ Carga Grafica a PygWalker desde Json")
                components.html(html_json , height = 800 , scrolling = True)
            except Exception as e:
                st.error(f"error al cargar el archivo : {e}")

st.sidebar.markdown("----")
st.sidebar.markdown(" Creado por : Camila Paredes y Diego Cerpa")
st.sidebar.markdown(" correo de contacto : 1234@alumnos.santotomas.cl")