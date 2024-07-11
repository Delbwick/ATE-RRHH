import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH Proyectos", page_icon="🆕")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula tu Proyecto!")

# HTML personalizado para el encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be; /* Color de fondo */
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
    h1 {
        font-family: 'Arial', sans-serif;
        font-size: 17pt;
        text-align: left;
        color: #333333;
    }
    h2 {
        font-family: 'Arial', sans-serif;
        font-size: 17pt;
        text-align: left;
        color: #333333;
    }
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
st.write("Detalle de proyectos")
# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

#>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<
#CODIGO DE LA APLICACION
#<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>
#FUncion para selecciopnar los proyectos
def get_puestos():
    query = """
        SELECT *
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    proyectos = [row.nombre for row in results]
    id_proyecto_seleccionado = [row.id_projecto for row in results]
    return proyectos

# Mostrar el selectbox de puestos
st.markdown("<h2>Datos de Factores</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
selected_proyecto = st.selectbox("Selecciona un proyecto", get_proyectos())
st.write(id_proyecto_seleccionado)
#mostrar los puestos como checkbox
# Obtener los puestos
proyectos = get_proyectos()
