import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH del Norte-Alta nuevos proyectos-beta4", page_icon="✅")
st.title("¡Bienvenido a RRHH del Norte! 👷")
st.header("¡Empieza tu Proyecto! - beta4")

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
st.write("# Alta nuevo Proyecto")

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

#>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<
#CODIGO DE LA APLICACION
#<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>


#Incluimos Los primeros campos del Proyecto
# Crear formulario para datos del proyecto



# Función para obtener puestos desde BigQuery
def get_puestos():
    query = """
        SELECT *
        FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
    """
    query_job = client.query(query)
    results = query_job.result()
    puestos = [row.descripcion for row in results]
    return puestos

# Mostrar el selectbox de puestos
st.markdown("<h2>Selecciona los Puestos de Trabajo del Proyecto</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
#selected_puesto = st.selectbox("Selecciona un puesto", get_puestos())
#mostrar los puestos como checkbox
# Obtener los puestos
puestos = get_puestos()


# Crear dos columnas
col1, col2 = st.columns(2)

# Mostrar los puestos como checkboxes en dos columnas
selected_puestos = []

with col1:
    st.write("Columna 1")
    for descripcion in puestos[:len(puestos)//2]:
        if st.checkbox(descripcion):
            selected_puestos.append(descripcion)

with col2:
    st.write("Columna 2")
    for descripcion in puestos[len(puestos)//2:]:
        if st.checkbox(descripcion):
            selected_puestos.append(descripcion)

# Mostrar los puestos seleccionados
if selected_puestos:
    st.write("Puestos seleccionados:")
    for descripcion in selected_puestos:
        st.write(f"{descripcion}")
else:
    st.warning("Por favor, selecciona al menos un puesto para continuar.")

#Funcion para ibcluir algun puesto nuevo
# Función para insertar un nuevo puesto en BigQuery
def add_puesto(nuevo_puesto):
    #Primero el id_puesto
    # Consulta para obtener el último ID de proyecto
    query_max_id_puestos = """
        SELECT MAX(id_puesto) FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        ORDER BY descripcion
        """
        
    query_job_max_id_puestos = client.query(query_max_id_puestos)
    max_id_result_puesto = query_job_max_id_puestos.result()

    max_id_puesto = 0
    for row in max_id_result_puesto:
        max_id_puesto = row[0]

        # Incrementar el máximo ID en 1 para obtener el nuevo ID de proyecto
    new_id_puesto = max_id_puesto + 1 if max_id_puesto is not None else 1
    #
    query = f"""
        INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.puestos` (id_puesto,descripcion)
        VALUES ({new_id_puesto},'{nuevo_puesto}')
    """
    query_job = client.query(query)
    query_job.result()  # Esperar a que la inserción se complete
    # Rerun the application to reflect the changes
    st.experimental_rerun()

# Mostrar el inputbox para añadir un nuevo puesto
st.markdown("<h2>Añadir un nuevo puesto de trabajo</h2>", unsafe_allow_html=True)
nuevo_puesto = st.text_input("Introduce el nombre del nuevo puesto")

# Botón para añadir el puesto
if st.button("Añadir puesto"):
    if nuevo_puesto:
        add_puesto(nuevo_puesto)
        st.success(f"Se ha añadido el puesto: {nuevo_puesto}")
    else:
        st.error("El campo de puesto no puede estar vacío.")

#botener datos de tablas

def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')


#

#Finde Primeros campos de proyectos
#para las selecciones de los factores que ya estan seleccionadops
def obtener_datos_bigquery(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"  # Ajusta el límite según sea necesario
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

