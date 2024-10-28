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


# Incluimos los primeros campos del Proyecto
st.title('Nuevo Proyecto:')
st.markdown("<h2>Datos de Proyecto</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)  # Línea horizontal ancha

# Crear formulario para datos del proyecto
with st.form(key="nuevo_proyecto_form"):
    # Campos del proyecto
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nombre = st.text_input('Nombre de Proyecto')
    with col2:
        descripcion = st.text_input('Descripción')
    with col3:
        fecha_inicio = st.date_input('Fecha de Inicio')
    with col4:
        fecha_fin = st.date_input('Fecha de Fin')
    
    # Otros campos del proyecto
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        proyecto_activo = st.checkbox('Proyecto Activo')
    with col2:
        id_ads = st.text_input('Cliente')
    with col3:
        id_tag = st.date_input('Creado en')
    with col4:
        id_propiedad = st.date_input('Actualizado en')
    
    # Datos adicionales
    col1, col2 = st.columns(2)
    
    with col1:
        sector = st.selectbox(
            'Sector', 
            ['Ayuntamiento', 'Gobierno','Administración local', 'Ayuntamiento de primera categoría', 'Ayuntamiento de segunda categoría', 'Ayuntamiento de tercera categoría', 'Consorcio', 'Mancomunidad', 'Cuadrilla', 'Entidad autónoma local', 'Empresa pública', 'Sociedad pública local', 'Sociedad pública autonómica', 'Sociedad pública estatal', 'Agencia', 'Departamento']
        )
    with col2:
        tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])
    
    # Datos de alta
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_alta = st.date_input('Fecha de Alta')
    with col2:
        pago = st.text_input('Forma de Pago')
    
    # Botón de submit
    submit = st.form_submit_button("Alta nuevo proyecto")

# Procesamiento de datos al enviar el formulario
if submit:
    try:
        # Consulta para obtener el último ID de proyecto
        query_max_id = """
        SELECT MAX(id_proyecto) FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
        """
        query_job_max_id = client.query(query_max_id)
        max_id_result = query_job_max_id.result()

        # Obtener el máximo ID actual y sumar 1 para el nuevo ID
        max_id = next(max_id_result)[0] if max_id_result.total_rows > 0 else 0
        new_id_proyecto = max_id + 1

        # Insertar el nuevo proyecto en la tabla de proyectos
        query_kai_insert = """
            INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.proyecto` 
            (id_projecto, nombre, descripcion, fecha_comienzo, fecha_fin, proyecto_activo) 
            VALUES 
            (@new_id_proyecto, @nombre, @descripcion, @fecha_inicio, @fecha_fin, @proyecto_activo)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("new_id_proyecto", "INT64", new_id_proyecto),
                bigquery.ScalarQueryParameter("nombre", "STRING", nombre),
                bigquery.ScalarQueryParameter("descripcion", "STRING", descripcion),
                bigquery.ScalarQueryParameter("fecha_inicio", "DATE", fecha_inicio),
                bigquery.ScalarQueryParameter("fecha_fin", "DATE", fecha_fin),
                bigquery.ScalarQueryParameter("proyecto_activo", "BOOL", proyecto_activo),
            ]
        )
        query_job_kai_insert = client.query(query_kai_insert, job_config=job_config)
        query_job_kai_insert.result()  # Esperar a que se complete la inserción

        st.success("¡Proyecto registrado exitosamente!")
        
    except Exception as e:
        st.error(f"Error al registrar el proyecto: {e}")

