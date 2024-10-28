# Importar las bibliotecas necesarias
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="Detalles del Proyecto", page_icon="📋")
st.title("Detalles del Proyecto")

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Obtener el ID de proyecto desde los parámetros de la URL
id_proyecto = st.experimental_get_query_params().get("id_proyecto", [None])[0]

if id_proyecto:
    # Obtener el nombre del cliente del proyecto
    query = f"""
        SELECT nombre 
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
        WHERE id_projecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    
    # Extraer el nombre del proyecto
    nombre_proyecto = None
    for row in results:
        nombre_proyecto = row['nombre']
    
    if nombre_proyecto:
        st.header(f"Proyecto: {nombre_proyecto} (ID: {id_proyecto})")
        
        # Mostrar los apartados con íconos
        st.markdown("""
        - 🏆 **Selección de factores de complemento de destino**
        - 🎯 **Selección de factores de complemento específico**
        - 🔧 **Modificación de factores por proyecto**
        - 📄 **Manuales preliminares**
        - 🧑‍💼 **Selección de puestos por proyecto**
        - 🧮 **Cálculo de puestos de trabajo por proyecto**
        - 📊 **Informes preliminares**
        """)
    else:
        st.warning("No se encontró el proyecto con el ID especificado.")
else:
    st.error("No se proporcionó un ID de proyecto.")
