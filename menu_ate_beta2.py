# Importar las bibliotecas necesarias
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

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
        
        # Crear una fila con tres columnas para las tarjetas
        col1, col2, col3 = st.columns(3)

        # Crear una función de tarjeta para evitar repetición
        def crear_tarjeta(columna, titulo, url, icono):
            with columna:
                st.markdown(f"""
                    <div style="padding: 15px; border-radius: 8px; border: 1px solid #ddd; box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
                        <h2 style="font-size: 16px; color: #333; margin-bottom: 10px;">{icono} {titulo}</h2>
                        <a href="{url}?id_proyecto={id_proyecto}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #2596be; color: white; border: none; padding: 8px 16px; border-radius: 4px;">Ir</button>
                        </a>
                    </div>
                """, unsafe_allow_html=True)

        # Añadir las tarjetas con iconos y enlaces
        crear_tarjeta(col1, "Selección de factores de complemento de destino", "https://ate-rrhh-sj96rw9k7b3phjarzwzqz8.streamlit.app", "🏆")
        crear_tarjeta(col2, "Selección de factores de complemento específico", "https://example.com/factores_especifico", "🎯")
        crear_tarjeta(col3, "Modificación de factores por proyecto", "https://example.com/factores_modificacion", "🔧")
        
        col1, col2, col3 = st.columns(3)
        crear_tarjeta(col1, "Manuales preliminares", "https://example.com/manuales_preliminares", "📄")
        crear_tarjeta(col2, "Selección de puestos por proyecto", "https://example.com/puestos_proyecto", "🧑‍💼")
        crear_tarjeta(col3, "Cálculo de puestos de trabajo por proyecto", "https://example.com/calculo_puestos", "🧮")

        col1, col2, col3 = st.columns(3)
        crear_tarjeta(col1, "Informes preliminares", "https://example.com/informes_preliminares", "📊")
        
    else:
        st.warning("No se encontró el proyecto con el ID especificado.")
else:
    st.error("No se proporcionó un ID de proyecto.")
