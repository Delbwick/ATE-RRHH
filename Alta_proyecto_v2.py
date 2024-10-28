import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH del Norte-Alta nuevos proyectos-beta2", page_icon="🆕")
st.title("¡Bienvenido a RRHH del Norte! 👷")
st.header("¡Empieza tu Proyecto!")

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
st.title('Nuevo Proyecto:')
st.markdown("<h2>Datos de Proyecto</h2>", unsafe_allow_html=True)
    # Línea horizontal ancha
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
  
col1, col2, col3, col4 = st.columns(4)

with col1:
    nombre = st.text_input('Nombre de Proyecto')
with col2:
    descripcion = st.text_input('Descripción')
with col3:
    fecha_inicio = st.date_input('Fecha de Inicio')
with col4:
    fecha_fin = st.date_input('Fecha de Fin')

# Filas para otros campos del proyecto
col1, col2, col3, col4 = st.columns(4)
with col1:
    proyecto_activo = st.checkbox('Proyecto Activo')
with col2:
    id_ads = st.text_input('Cliente')
with col3:
    id_tag = st.date_input('Creado en')
with col4:
    id_propiedad = st.date_input('Actualizado en')

# Filas para datos adicionales
col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox('Sector', ['Ayuntamiento', 'Gobierno','Administración local',
'Ayuntamiento de primera categoría',
'Ayuntamiento de segunda categoría',
'Ayuntamiento de tercera categoría',
'Consorcio',
'Mancomunidad',
'Cuadrilla',
'Entidad autónoma local',
'Empresa pública',
'Sociedad pública local',
'Sociedad pública autonómica',
'Sociedad pública estatal',
'Agencia',
'Departamento'])
with col2:
    tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])

# Filas para datos de alta
col1, col2 = st.columns(2)
with col1:
    fecha_alta = st.date_input('Fecha de Alta')
with col2:
    pago = st.text_input('Forma de Pago')

# Botón de submit
    submit = st.form_submit_button("Alta nuevo proyecto")

    if submit:
        try:
            # Consulta para obtener el último ID de proyecto
            query_max_id = """
            SELECT MAX(id_projecto) FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
            """
            query_job_max_id = client.query(query_max_id)
            max_id_result = query_job_max_id.result()

            max_id = 0
            for row in max_id_result:
                max_id = row[0]

            # Incrementar el máximo ID en 1 para obtener el nuevo ID de proyecto
            new_id_proyecto = max_id + 1 if max_id is not None else 1

            # Insertar el nuevo proyecto en la tabla de proyectos
            query_kai_insert = f"""
                INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.proyecto` 
                (id_projecto, nombre, descripcion, fecha_comienzo, fecha_fin, proyecto_activo) 
                VALUES 
                ({new_id_proyecto}, '{nombre.replace("'", "''")}', '{descripcion.replace("'", "''")}', '{fecha_inicio}', '{fecha_fin}', {proyecto_activo})
            """
            query_job_kai_insert = client.query(query_kai_insert)
            query_job_kai_insert.result()  # Asegurarse de que la consulta se complete
             st.success("¡Proyecto registrado exitosamente!")
        
        except Exception as e:
            st.error(f"Error al registrar el proyecto: {e}")
