import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# Configuración de la página
st.set_page_config(page_title="Selector de Factores", layout="wide")

# Autenticación con credenciales desde streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Cliente de BigQuery autenticado
client = bigquery.Client(credentials=credentials)

# Función para obtener los datos de la tabla
def obtener_datos_tabla():
    query = """
    SELECT id_proyecto, id_puesto, complementos_especificos, complementos_destino
    FROM `nombre_de_tu_proyecto.tu_dataset.tu_tabla`
    """
    df = client.query(query).to_dataframe()
    return df

# Obtener los datos
df = obtener_datos_tabla()

# Mostrar los checkboxes para seleccionar complementos de destino
st.markdown("<h2>Selecciona los Factores de complemento de destino:</h2>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento de destino:")

# Convertir la columna `complementos_destino` en una lista de opciones únicas
opciones_destino = df['complementos_destino'].dropna().unique().tolist()

# Mostrar las opciones de complementos de destino y guardar la selección
seleccion_destino = st.multiselect("Selecciona los complementos de destino:", opciones_destino)

# Mostrar los checkboxes para seleccionar complementos específicos
st.markdown("<h2>Selecciona los Factores de complemento específico:</h2>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento específico:")

# Convertir la columna `complementos_especificos` en una lista de opciones únicas
opciones_especificos = df['complementos_especificos'].dropna().unique().tolist()

# Mostrar las opciones de complementos específicos y guardar la selección
seleccion_especificos = st.multiselect("Selecciona los complementos específicos:", opciones_especificos)

# Mostrar las selecciones realizadas
st.write("Complementos de destino seleccionados:")
st.write(seleccion_destino)

st.write("Complementos específicos seleccionados:")
st.write(seleccion_especificos)
