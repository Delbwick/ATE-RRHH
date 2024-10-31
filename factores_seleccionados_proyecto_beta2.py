import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino-Manual preliminar")

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener complementos específicos (con nombres de tablas) de cada proyecto
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_especifico for row in results]

# Función para obtener complementos de destino (con nombres de tablas) de cada proyecto
def get_complementos_destino(id_proyecto):
    query = f"""
        SELECT complemento_destino
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_destino for row in results]

# Función para obtener datos de la tabla específica usando el nombre de la tabla
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Crear el sidebar para selección de proyectos
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]

# Obtener id_proyecto desde la URL si está disponible
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Crear el selectbox para proyectos en el sidebar
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

# Obtener el ID del proyecto seleccionado
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Mostrar ID de proyecto seleccionado para verificación
st.write(f"**ID del Proyecto Seleccionado**: {id_proyecto_seleccionado}")

# Obtener y mostrar datos de tablas específicas para el proyecto seleccionado
if id_proyecto_seleccionado:
    # Complementos específicos
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_especifico)
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")
    
    # Complementos de destino
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_destino)
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")
