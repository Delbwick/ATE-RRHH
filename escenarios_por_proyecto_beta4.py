import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="APP Escenarios por proyecto", page_icon="🤯")
st.title("¡Bienvenido a RRHH!")
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

# Función para obtener complementos específicos
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico, porcentaje_importancia
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [{'complemento_especifico': row.complemento_especifico, 'porcentaje_importancia': row.porcentaje_importancia} for row in results]

# Función para obtener complementos de destino
def get_complementos_destino(id_proyecto):
    query = f"""
        SELECT complemento_destino, porcentaje_importancia
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [{'complemento_destino': row.complemento_destino, 'porcentaje_importancia': row.porcentaje_importancia} for row in results]

# Función para obtener datos de una tabla específica
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    df = client.query(query).to_dataframe().fillna('No disponible')
    return df

# Mostrar complementos y tablas
def mostrar_complementos_y_tablas(complementos, tipo, id_proyecto):
    for complemento in complementos:
        porcentaje = st.text_input(
            f"Porcentaje para {complemento[f'{tipo}']} ({tipo.capitalize()}) - Ejemplo: 20%",
            value=str(complemento['porcentaje_importancia']),
        )
        nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento[f'{tipo}']}"
        df = obtener_datos_tabla(nombre_tabla)
        st.write(f"**{complemento[f'{tipo}']} ({tipo.capitalize()}) - Datos:**")
        st.dataframe(df, use_container_width=True)

# Mostrar la interfaz principal
def mostrar_interfaz():
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    st.sidebar.title("Opciones")
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres)

    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    if id_proyecto_seleccionado:
        st.markdown("**Importante:** Los porcentajes deben sumar **100%**.")
        st.write("### Complementos Específicos")
        complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
        mostrar_complementos_y_tablas(complementos_especificos, 'complemento_especifico', id_proyecto_seleccionado)

        st.write("### Complementos de Destino")
        complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
        mostrar_complementos_y_tablas(complementos_destino, 'complemento_destino', id_proyecto_seleccionado)

mostrar_interfaz()
