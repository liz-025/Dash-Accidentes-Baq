import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dashboard de Accidentes de Tránsito de Barranquilla", layout="wide")

# Configuración de estilo
sns.set_theme(style="whitegrid")

# Opciones de navegación
menu = st.sidebar.selectbox("Navegación", ["Dashboard", "Mapa de Accidentes"])

if menu == "Dashboard":
    # Conexión a la base de datos
    db_url = 'postgresql+psycopg2://postgres.ankpdyfjelmbahoberfv:jose12345@aws-0-us-west-1.pooler.supabase.com:6543/postgres'
    try:
        engine = create_engine(db_url)
        connection = engine.connect()

        # Cargar datos directamente con pandas
        query = """
        SELECT
            v.id_victima,
            v.condicion_victima,
            v.sexo_victima,
            v.edad_victima,
            v.cantidad_victimas,
            a.id_accidente,
            a.fecha_accidente,
            a.direccion_accidente,
            c.id_clase_accidente,
            c.clase_accidente,
            c.gravedad_accidente
        FROM victima v
        LEFT JOIN accidente a ON v.id_accidente = a.id_accidente
        LEFT JOIN clase_accidente c ON a.id_clase_accidente = c.id_clase_accidente;
        """
        data = pd.read_sql_query(query, connection)
        connection.close()
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        data = pd.DataFrame()

    # Convertir fecha a formato datetime
    data['fecha_accidente'] = pd.to_datetime(data['fecha_accidente'], errors='coerce')

    # Filtrar edades mayores a 100
    data = data[data['edad_victima'] <= 100]

    # Sidebar para filtros
    st.sidebar.header("Filtros")

    # Filtro por año
    years = sorted(data['fecha_accidente'].dt.year.dropna().unique())
    years.insert(0, "Todos")
    selected_year = st.sidebar.selectbox("Selecciona un año:", years)

    # Filtro por mes
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    selected_month = st.sidebar.selectbox("Selecciona un mes:", ["Todos"] + list(months.values()))

    # Filtro por gravedad del accidente
    gravity_levels = ["Todos"] + data['gravedad_accidente'].dropna().unique().tolist()
    selected_gravity = st.sidebar.selectbox("Selecciona la gravedad del accidente:", gravity_levels)

    # Filtro por clase de accidente
    accident_classes = ["Todos"] + data['clase_accidente'].dropna().unique().tolist()
    selected_class = st.sidebar.selectbox("Selecciona la clase de accidente:", accident_classes)

    # Aplicar filtros
    data_filtered = data.copy()
    if selected_year != "Todos":
        data_filtered = data_filtered[data_filtered['fecha_accidente'].dt.year == selected_year]

    if selected_month != "Todos":
        month_number = list(months.keys())[list(months.values()).index(selected_month)]
        data_filtered = data_filtered[data_filtered['fecha_accidente'].dt.month == month_number]

    if selected_gravity != "Todos":
        data_filtered = data_filtered[data_filtered['gravedad_accidente'] == selected_gravity]

    if selected_class != "Todos":
        data_filtered = data_filtered[data_filtered['clase_accidente'] == selected_class]

    # Título principal
    st.title("Dashboard de Accidentes de Tránsito de Barranquilla")
    st.markdown("### Exploración interactiva de los datos de accidentes.")

    # Tarjetas con métricas principales
    st.header("Resumen General")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_accidentes = data_filtered['id_accidente'].nunique()
        st.markdown(
            f"""
            <div style="background-color:#e8f5e9;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:#388e3c;margin:0">Número de Accidentes</h3>
                <h1 style="margin:10px 0">{total_accidentes}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        total_victimas = data_filtered['cantidad_victimas'].sum()
        st.markdown(
            f"""
            <div style="background-color:#ffebee;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:#d32f2f;margin:0">Número de Víctimas</h3>
                <h1 style="margin:10px 0">{int(total_victimas)}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        edad_promedio = data_filtered['edad_victima'].mean()
        st.markdown(
            f"""
            <div style="background-color:#e3f2fd;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:#1976d2;margin:0">Edad Promedio de Víctimas</h3>
                <h1 style="margin:10px 0">{edad_promedio:.1f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Función para agregar etiquetas en las barras
    def add_labels(ax):
        for p in ax.patches:
            ax.annotate(f'{int(p.get_width())}', (p.get_width() + 1, p.get_y() + 0.5), 
                        ha='left', va='center', fontsize=10, color='black')

    # Gráficas de análisis
    st.header("Análisis de Frecuencias")
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("Condición de la Víctima")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.countplot(y=data_filtered['condicion_victima'], palette="coolwarm", ax=ax1)
        add_labels(ax1)
        st.pyplot(fig1)

    with col5:
        st.subheader("Clase de Accidente")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.countplot(y=data_filtered['clase_accidente'], palette="viridis", ax=ax2)
        add_labels(ax2)
        st.pyplot(fig2)

    st.header("Análisis Temporal")
    col6, col7 = st.columns(2)

    with col6:
        st.subheader("Distribución Mensual")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.countplot(x=data_filtered['fecha_accidente'].dt.month, palette="magma", ax=ax3)
        add_labels(ax3)
        st.pyplot(fig3)

    with col7:
        st.subheader("Accidentes por Día de la Semana")
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.countplot(x=data_filtered['fecha_accidente'].dt.day_name(), palette="cubehelix", ax=ax4)
        add_labels(ax4)
        ax4.tick_params(axis='x', rotation=45)
        st.pyplot(fig4)

    st.header("Análisis por Género y Edades")
    col8, col9 = st.columns(2)

    with col8:
        st.subheader("Análisis por Género")
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        sns.countplot(x=data_filtered['sexo_victima'], palette="Set2", ax=ax5)
        add_labels(ax5)
        st.pyplot(fig5)

    with col9:
        st.subheader("Distribución de Edades")
        fig6, ax6 = plt.subplots(figsize=(6, 4))
        sns.histplot(data_filtered['edad_victima'], kde=True, bins=20, color='orange', ax=ax6)
        st.pyplot(fig6)

elif menu == "Mapa de Accidentes":
    st.title("Mapa de Accidentes de Tránsito")
    st.markdown("### Visualización geográfica de los accidentes reportados en Barranquilla.")

    try:
        with open("mapa_burbujas.html", "r", encoding="utf-8") as html_file:
            map_content = html_file.read()
        st.components.v1.html(map_content, height=800, scrolling=True)
    except FileNotFoundError:
        st.error("El archivo 'mapa_burbujas.html' no se encontró. Asegúrate de que esté en el directorio correcto.")

# Nota final
st.markdown("---")
st.markdown("### Explora más datos ajustando los filtros en la barra lateral.")
