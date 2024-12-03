import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="APP Escenarios por proyecto ", page_icon="🤯")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula los Salarios Por Proyecto!")

# HTML personalizado para el encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 10px;
        }
        .wide-line {
            width: 100%;
            height: 2px;
            background-color: #333333;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        h1, h2 {
            font-family: 'Arial', sans-serif;
            font-size: 17pt;
            text-align: left;
            color: #333333;
        }
        h3 {
            font-family: 'Arial', sans-serif;
            font-size: 14pt;
            text-align: center;
            color: #333333;
        }
        .cell {
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .header-cell {
            background-color: #e0e0e0;
            font-weight: bold;
            border: 1px solid black;
            padding: 10px;
            text-align: center;
        }
        .dataframe-cell {
            overflow-x: auto;
            overflow-y: auto;
            max-width: 100%;
            max-height: 200px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #2596be;
            color: white;
        }
        td {
            background-color: #f9f9f9;
        }
    </style>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM ate-rrhh-2024.Ate_kaibot_2024.proyecto
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener complementos específicos de cada proyecto
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_especifico for row in results]

# Función para obtener complementos de destino
def get_complementos_destino(id_proyecto):
    query = f"""
        SELECT complemento_destino
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_destino for row in results]

# Función para obtener datos de una tabla específica
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM {nombre_tabla} LIMIT 100"
    df = client.query(query).result().to_dataframe().fillna('No disponible')
    return df

# Función para filtrar complementos según la categoría
def filtrar_complementos_por_categoria(complementos, categoria_seleccionada):
    categoria_orden = {
        'ap/e': 1,
        'a1': 2,
        'a2': 3,
        'b': 4,
        'c1': 5,
        'c2': 6
    }
    return [complemento for complemento in complementos if categoria_orden.get(categoria_seleccionada, 7) <= categoria_orden.get(complemento, 7)]

# Mostrar complementos específicos y de destino
def mostrar_opciones_complementos(nombre_tabla, df, tipo_complemento):
    st.write(f"#### Opciones para el {tipo_complemento}: {nombre_tabla}")
    st.dataframe(df, use_container_width=True)

# Mostrar la interfaz principal
def mostrar_interfaz():
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0] if proyectos else None
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres)

    # Selección de categoría en el sidebar
    categorias = ['ap/e', 'a1', 'a2', 'b', 'c1', 'c2']
    categoria_seleccionada = st.sidebar.selectbox("Seleccione una Categoría:", categorias)

    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    st.markdown("""
    **Importante**: Los porcentajes para los complementos deben sumar **100%**.
    """)

    if id_proyecto_seleccionado:
        # Obtener y filtrar complementos específicos
        complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
        complementos_especificos_filtrados = filtrar_complementos_por_categoria(complementos_especificos, categoria_seleccionada)

        if complementos_especificos_filtrados:
            st.write("### Factores Específicos del Proyecto")
            for nombre_tabla in complementos_especificos_filtrados:
                df_complemento = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
                mostrar_opciones_complementos(nombre_tabla, df_complemento, "complemento específico")
        else:
            st.write("No se encontraron complementos específicos para la categoría seleccionada.")

        # Obtener y filtrar complementos de destino
        complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
        complementos_destino_filtrados = filtrar_complementos_por_categoria(complementos_destino, categoria_seleccionada)

        if complementos_destino_filtrados:
            st.write("### Factores de Destino del Proyecto")
            for nombre_tabla in complementos_destino_filtrados:
                df_complemento = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
                mostrar_opciones_complementos(nombre_tabla, df_complemento, "complemento de destino")
        else:
            st.write("No se encontraron complementos de destino para la categoría seleccionada.")

mostrar_interfaz()
