import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino - Manual preliminar")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
        1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.
    </h3>
    <!-- Contenido omitido para brevedad -->
</div>
"""

# Mostrar el HTML en Streamlit
st.markdown(scrollable_text_html, unsafe_allow_html=True)

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Funciones para obtener datos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Función para guardar selecciones en BigQuery
def guardar_selecciones_en_bigquery(tabla, id_proyecto, selecciones):
    """Guarda solo el ID del proyecto y el nombre de la tabla de factores seleccionada en BigQuery."""
    registros = []
    for seleccion in selecciones:
        registros.append({
            "id_proyecto": id_proyecto,            # ID del proyecto seleccionado
            "complemento_destino": seleccion  # Nombre de la tabla de factores seleccionada
        })
    
    # Convertir a DataFrame y subir a BigQuery
    df_registros = pd.DataFrame(registros)
    client.load_table_from_dataframe(df_registros, tabla).result()
    st.success("Las selecciones se han guardado correctamente en BigQuery.")

# Configuración del Sidebar
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar el proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Selectbox para seleccionar el proyecto
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Funcionalidad de selección de factores
st.sidebar.markdown("<h2>Selecciona los Factores</h2>", unsafe_allow_html=True)
opcion = st.sidebar.selectbox("Tipo de Factor", [
    "Factores de formación", 
    "Factores de jerarquización o mando", 
    "Factores de responsabilidad", 
    "Factores de iniciativa o autonomía", 
    "Factores de Complejidad"
])

# Modificar la etiqueta en función de la opción seleccionada
if opcion == "Factores de formación":
    etiqueta = "formacion"
elif opcion == "Factores de jerarquización o mando":
    etiqueta = "factor_jerarquizacion"
elif opcion == "Factores de responsabilidad":
    etiqueta = "factor_responsabilidad"
elif opcion == "Factores de iniciativa o autonomía":
    etiqueta = "factor_iniciativa"
elif opcion == "Factores de Complejidad":
    etiqueta = "factor_complejidad"
else:
    etiqueta = ""

# Obtener los datos de la tabla en función de la etiqueta
project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Consulta SQL para obtener las tablas y sus columnas principales
query = f"""
    SELECT table_name, column_name
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE ordinal_position = 1
    AND table_name IN (
        SELECT table_name
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_OPTIONS`
        WHERE option_name = 'labels'
        AND option_value LIKE '%"{etiqueta}"%'
    )
    ORDER BY column_name
"""

# Ejecutar la consulta y obtener los resultados
tables_query_job = client.query(query)
tables = tables_query_job.result()
tablas_seleccionadas = [row.table_name for row in tables]

# Inicializar la lista de selecciones
selecciones_destino = []

# Mostrar las tablas y permitir la selección
st.sidebar.markdown("<h2>Selecciona los Factores de complemento de destino:</h2>", unsafe_allow_html=True)
for tabla in tablas_seleccionadas:
    if st.sidebar.checkbox(tabla, key=f"checkbox_{tabla}"):
        selecciones_destino.append(tabla)

# Botón para guardar selecciones
if st.sidebar.button("Guardar selecciones"):
    tabla_seleccion = f"{project_id}.{dataset_id}.nombre_de_la_tabla_de_destino"  # Cambia este valor por el nombre correcto de la tabla de destino
    guardar_selecciones_en_bigquery(tabla_seleccion, id_proyecto_seleccionado, selecciones_destino)

# Mostrar complementos específicos y de destino según la selección del proyecto
if id_proyecto_seleccionado:
    # Complementos específicos
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            mostrar_opciones_complementos(nombre_tabla, df_complemento_especifico, "complemento específico")
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")
    
    # Complementos de destino
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            mostrar_opciones_complementos(nombre_tabla, df_complemento_destino, "complemento de destino")
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")
