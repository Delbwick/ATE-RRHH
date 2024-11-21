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

# HTML personalizado para el encabezado y estilos globales
header_html = """
    <style>
        /* Colores principales */
        :root {
            --color-principal: #007d9a;
            --color-secundario: #dfa126;
            --color-texto: #333333;
        }

        /* Estilos generales */
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: var(--color-texto);
        }

        .header-container {
            background-color: var(--color-principal);
            padding: 0;
            text-align: center;
        }

        .logo {
            width: 100%;
            max-height: 200px;
            object-fit: cover;
        }

        .wide-line {
            width: 100%;
            height: 2px;
            background-color: var(--color-secundario);
            margin-top: 20px;
            margin-bottom: 20px;
        }

        h4 {
            font-size: 20pt;
            color: var(--color-principal);
            font-weight: bold;
        }

        /* Estilo para el formulario */
        .stTextInput, .stDateInput, .stCheckbox, .stSelectbox, .stRadio {
            background-color: #ffffff;
            border: 1px solid var(--color-principal);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }

        .stTextInput input, .stDateInput input, .stCheckbox input, .stSelectbox select, .stRadio input {
            color: var(--color-texto);
        }

        .stButton>button {
            background-color: var(--color-secundario);
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            border: none;
            font-size: 14pt;
        }

        .stButton>button:hover {
            background-color: darkorange;
        }

        /* Estilo del botón de redirección */
        .stButton a {
            color: white;
            text-decoration: none;
        }
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Crear formulario para datos del proyecto
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
            st.markdown(f"""
                <a href="https://ate-rrhh-jwinmwitfd8gsoc4va9cjc.streamlit.app?id_proyecto={new_id_proyecto}" target="_blank">
                    <button class="stButton">Ir a la APP de Selección de Factores</button>
                </a>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al registrar el proyecto: {e}")

# Crear un botón para ir al menú principal
st.markdown("""
    <a href="https://ate-rrhh-jwinmwitfd8gsoc4va9cjc.streamlit.app?id_proyecto={new_id_proyecto}" target="_blank">
        <button class="stButton">Ir al Menú Principal</button>
    </a>
    """, unsafe_allow_html=True)

