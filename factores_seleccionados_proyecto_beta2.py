import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino-Manual preliminar")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
        1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.
    </h3>
    <p style="font-family: Arial, sans-serif; font-size: 14px; color: #555555; text-align: justify;">
        Un libro de valoración se utiliza para valorar puestos de trabajo de forma objetiva. No se tienen en cuenta las personas que ocupan los puestos, sino los requisitos necesarios de cada puesto.
        Se presentan los factores elegidos para valorar la organización, la graduación de los factores y el peso porcentual específico de cada factor en función de la organización.
        El objetivo de la valoración de puestos de trabajo es establecer el valor relativo de los puestos de una organización, asignando a cada puesto una clasificación profesional y estableciendo una retribución en función de la valoración de diversos factores.
        Hay que elegir los factores que se van a utilizar para realizar la valoración. Tanto los que determinan los complementos de destino como los que determinan los complementos específicos. La elección de los factores es relativamente libre mientras nos adaptemos a los criterios legales.
        Además, a cada factor se le asignará un peso porcentual específico. De esta forma, escalonamos la importancia del propio factor dentro de la organización.
        Los factores de cada complemento, de destino, por un lado, y los específicos, por otro, deben sumar cada uno por su lado un 100%.
        Los pesos porcentuales se refieren y se suelen escoger según la importancia o repetición de determinadas funciones en los puestos de trabajo de la institución, aunque la negociación con los representantes sindicales puede dar porcentajes poco habituales.
        Asimismo, los factores se dividen en niveles alfabéticos (se pueden añadir más graduaciones de la A a la G si se desea) y cada grado tiene una valoración entre 0 y 100.
        La combinación del peso específico del factor y la valoración por puntos nos permite trasladarnos a un resultado económico numérico de cada puesto de trabajo.
    </p>
</div>
"""

# Mostrar el HTML en Streamlit
st.markdown(scrollable_text_html, unsafe_allow_html=True)

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
