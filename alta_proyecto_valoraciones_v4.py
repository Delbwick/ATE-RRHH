import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="APP VALORACIONES DE PUESTOS DE TRABAJO-Alta nuevos proyectos-beta4", page_icon="🤓")
st.title("¡Bienvenido a APP VALORACIONES DE PUESTOS DE TRABAJO 👷")
st.header("¡Empieza dando de alta tu Proyecto!")

# HTML personalizado para el encabezado
header_html = """
     <style>
        .header-container {
            background-color: #007d9a; /* Color de fondo principal */
            padding: 0;
            text-align: center;
        }
        .logo {
            width: 100%;  /* Hacer que el logo ocupe todo el ancho */
            max-height: 300px; /* Limitar la altura del banner */
            object-fit: cover;  /* Asegura que el logo se ajuste bien */
        }
        .wide-line {
            width: 100%;
            height: 2px;
            background-color: #dfa126; /* Color secundario */
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
st.markdown('<div class="header-container"><img class="logo" src="https://kaibot.es/wp-content/uploads/2024/11/banner-app-1.png" alt="Logo"></div>', unsafe_allow_html=True)
#st.write("# Alta nuevo Proyecto")

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

#>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<
#CODIGO DE LA APLICACION
#<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>


# Crear formulario para datos del proyecto
#st.title('Nuevo Proyecto:')
st.markdown("<h4>Introduce los Datos de tu nuevo Proyecto</h4>", unsafe_allow_html=True)
# Línea horizontal ancha
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

with st.form(key='nuevo_proyecto_form'):
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
        sector = st.selectbox('Sector', [
            'Ayuntamiento', 'Gobierno', 'Administración local',
            'Ayuntamiento de primera categoría', 'Ayuntamiento de segunda categoría',
            'Ayuntamiento de tercera categoría', 'Consorcio', 'Mancomunidad',
            'Cuadrilla', 'Entidad autónoma local', 'Empresa pública',
            'Sociedad pública local', 'Sociedad pública autonómica',
            'Sociedad pública estatal', 'Agencia', 'Departamento'
        ])
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
            if max_id is not None:
                new_id_proyecto = max_id + 1
            else:
                new_id_proyecto = 1

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
            # Botón para abrir otra pantalla
            # Botón para redirigir a la otra aplicación con el ID de proyecto
            st.markdown(f"""
                <a href="https://ate-rrhh-jwinmwitfd8gsoc4va9cjc.streamlit.app?id_proyecto={new_id_proyecto}" target="_blank">
                    <button style="background-color:Green;padding:10px;border-radius:5px;color:white;border:none;">
                    Ir a la APP de Seleccion de Factores
                    </button>
                </a>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al registrar el proyecto: {e}")

# Crear un botón
st.markdown("""
    <a href="https://ate-rrhh-jwinmwitfd8gsoc4va9cjc.streamlit.app?id_proyecto={new_id_proyecto}" target="_blank">
        <button style="background-color:Green;padding:10px;border-radius:5px;color:white;border:none;">
            Ir al Menú Principal
        </button>
    </a>
    """, unsafe_allow_html=True)
