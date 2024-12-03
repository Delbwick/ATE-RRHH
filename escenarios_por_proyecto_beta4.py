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

# Función para obtener complementos y sus porcentajes
def obtener_complementos_con_importancia(tabla, id_proyecto):
    query = f"""
        SELECT complemento, porcentaje_importancia
        FROM `ate-rrhh-2024.Ate_kaibot_2024.{tabla}`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'complemento': row.complemento, 'porcentaje_importancia': row.porcentaje_importancia} for row in results]

# Filtrar complementos por categoría
def filtrar_complementos_por_categoria(complementos, categoria_seleccionada):
    categoria_orden = {
        'ap/e': 1,
        'a1': 2,
        'a2': 3,
        'b': 4,
        'c1': 5,
        'c2': 6
    }
    return [complemento for complemento in complementos if categoria_orden.get(categoria_seleccionada, 7) <= categoria_orden.get(complemento['complemento'], 7)]

# Mostrar complementos con inputs editables
def mostrar_opciones_complementos_editables(nombre_tabla, complementos):
    st.write(f"#### Opciones para el complemento: {nombre_tabla}")
    for complemento in complementos:
        col1, col2 = st.columns([3, 1])  # Dos columnas para alineación
        with col1:
            st.write(complemento['complemento'])  # Nombre del complemento
        with col2:
            nuevo_valor = st.number_input(
                "Porcentaje importancia",
                min_value=0.0,
                max_value=100.0,
                value=complemento['porcentaje_importancia'],
                step=0.1,
                key=f"{nombre_tabla}_{complemento['complemento']}"
            )
            complemento['porcentaje_importancia'] = nuevo_valor  # Actualizamos el valor editado

# Mostrar la interfaz principal
def mostrar_interfaz():
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0] if proyectos else None
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres)

    categorias = ['ap/e', 'a1', 'a2', 'b', 'c1', 'c2']
    categoria_seleccionada = st.sidebar.selectbox("Seleccione una Categoría:", categorias)

    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    st.markdown("""
    **Importante**: Los porcentajes para los complementos deben sumar **100%**.
    """)

    if id_proyecto_seleccionado:
        complementos_especificos = obtener_complementos_con_importancia('complemento_especifico_x_proyecto', id_proyecto_seleccionado)
        complementos_especificos_filtrados = filtrar_complementos_por_categoria(complementos_especificos, categoria_seleccionada)

        if complementos_especificos_filtrados:
            st.write("### Factores Específicos del Proyecto")
            mostrar_opciones_complementos_editables('complemento_especifico_x_proyecto', complementos_especificos_filtrados)
        else:
            st.write("No se encontraron complementos específicos para la categoría seleccionada.")

        complementos_destino = obtener_complementos_con_importancia('complemento_destino_x_proyecto', id_proyecto_seleccionado)
        complementos_destino_filtrados = filtrar_complementos_por_categoria(complementos_destino, categoria_seleccionada)

        if complementos_destino_filtrados:
            st.write("### Factores de Destino del Proyecto")
            mostrar_opciones_complementos_editables('complemento_destino_x_proyecto', complementos_destino_filtrados)
        else:
            st.write("No se encontraron complementos de destino para la categoría seleccionada.")

mostrar_interfaz()
