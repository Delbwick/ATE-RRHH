import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino - Versión 2")

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Datos de proyecto y dataset
project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Crear el selectbox en el sidebar con las categorías de factores
opcion = st.sidebar.selectbox(
    "Seleccione una categoría:",
    ("Factores de formación", 
     "Factores de jerarquización o mando", 
     "Factores de responsabilidad", 
     "Factores de iniciativa o autonomía",
     "Factores de Complejidad")
)

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

# Función para obtener tablas con la etiqueta seleccionada
def get_tablas_por_etiqueta(etiqueta):
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
    query_job = client.query(query)
    results = query_job.result()
    return [(row.table_name, row.column_name) for row in results]

# Función para obtener los datos de una tabla de BigQuery
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Función para mostrar factores basados en la etiqueta seleccionada
def mostrar_factores():
    tablas_con_etiqueta = get_tablas_por_etiqueta(etiqueta)
    if tablas_con_etiqueta:
        for nombre_tabla, columna_principal in tablas_con_etiqueta:
            st.write(f"**Tabla: {nombre_tabla}** (Columna principal: {columna_principal})")
            df = obtener_datos_tabla(f"{project_id}.{dataset_id}.{nombre_tabla}")
            st.dataframe(df)
    else:
        st.write("No se encontraron tablas para la categoría seleccionada.")

# Función para crear una nueva tabla
def crear_tabla_nueva():
    st.write("**Crear una nueva tabla**")
    table_name = st.text_input("Nombre de la nueva tabla")
    num_columns = st.number_input("Número de columnas", min_value=1, max_value=10)
    columns = []
    for i in range(num_columns):
        col_name = st.text_input(f"Nombre de la columna {i + 1}")
        col_type = st.selectbox(f"Tipo de dato de la columna {i + 1}", ["STRING", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP"])
        columns.append((col_name, col_type))
    
    # Crear la tabla si el botón es presionado
    if st.button("Crear Tabla"):
        cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns])
        query = f"CREATE TABLE `{project_id}.{dataset_id}.{table_name}` ({cols_str})"
        client.query(query)
        st.success("Tabla creada exitosamente")

# Mostrar el HTML de la descripción inicial
st.markdown("<h2>Selecciona los Factores de complemento de destino versión 2:</h2>", unsafe_allow_html=True)
st.markdown("<h2>Es necesario que selecciones por lo menos un Factor</h2>", unsafe_allow_html=True)
st.markdown("<p>Por defecto el PRIMERO SIEMPRE ESTÁ SELECCIONADO</p>", unsafe_allow_html=True)

# Mostrar los factores de la categoría seleccionada
mostrar_factores()

# Crear nueva tabla - Sección al final de la página
st.sidebar.write("---")
st.sidebar.write("Crear una nueva tabla de factores")
crear_tabla_nueva()
