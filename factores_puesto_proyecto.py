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
    .preview-table th {
        text-align: left;
        font-size: 14px;
        color: #555555;
    }
    .preview-table td {
        font-size: 12px;
        color: #333333;
        padding: 5px;
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

# Función para obtener datos de BigQuery
def obtener_datos_bigquery(query):
    query_job = client.query(query)
    results = query_job.result()
    df = pd.DataFrame(data=[row.values() for row in results], columns=[field.name for field in results.schema])
    return df

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# SELECCION DE PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Función para seleccionar los proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto, nombre
        FROM ate-rrhh-2024.Ate_kaibot_2024.proyecto
    """
    query_job = client.query(query)
    results = query_job.result()
    proyectos = [{'id': row.id_projecto, 'nombre': row.nombre} for row in results]
    return proyectos

# Mostrar el encabezado y línea separadora
st.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Obtener lista de proyectos
proyectos = get_proyectos()

# Extraer solo los nombres de los proyectos para el selectbox
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]

# Mostrar el cuadro de selección de proyectos
index_seleccionado = st.selectbox("Selecciona un proyecto", proyectos_nombres)

# Obtener el ID del proyecto seleccionado
id_proyecto_seleccionado = None
for proyecto in proyectos:
    if proyecto['nombre'] == index_seleccionado:
        id_proyecto_seleccionado = proyecto['id']
        break

# Mostrar el ID seleccionado (solo para propósitos de verificación)
if id_proyecto_seleccionado is not None:
    st.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")
else:
    st.write("Selecciona un proyecto para ver su ID")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# PUESTOS POR PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Mostrar el encabezado y línea separadora
st.markdown("<h2>Puestos asociados a ese proyecto</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Consulta SQL para obtener los puestos de trabajo asociados al proyecto
query_puestos_proyecto = f"""
    SELECT * FROM ate-rrhh-2024.Ate_kaibot_2024.puestos
    WHERE id_puesto IN (
        SELECT id_puesto FROM ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto
        WHERE id_proyecto = {id_proyecto_seleccionado})
"""

df_puestos_proyecto = obtener_datos_bigquery(query_puestos_proyecto)
st.markdown(f"<div class='cell dataframe-cell'>{df_puestos_proyecto.to_html(index=False)}</div>", unsafe_allow_html=True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# COMPLEMENTOS ESPECIFICOS Y DE DESTINO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Definir las tablas disponibles
PAGES_TABLES = {
    "Formación": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Complejidad Técnica destino": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Especialización destino": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Autonomía-Iniciativa-Complejidad": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    "Responsabilidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
}

# Mostrar checkboxes para seleccionar las tablas de factores de complemento de destino
selected_factores = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES.items():
    if st.checkbox(nombre_tabla):
        selected_factores.append((nombre_completo, id_tabla))
        # Obtener la descripción de la tabla
        table = client.get_table(nombre_completo)  # Asegúrate de usar el nombre correcto para la llamada
        descripcion = table.description
        st.write(descripcion)

# Mostrar los datos seleccionados
if selected_factores:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.write("Selecciona los valores específicos de las tablas seleccionadas:")

    valores_seleccionados = {}
    for nombre_completo, id_tabla in selected_factores:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(f"SELECT * FROM {nombre_completo}")
        if not df.empty:
            # Crear lista de opciones para st.radio
            opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df.iterrows()]
            opciones.insert(0, 'Ninguno')  # Añadir opción 'Ninguno' al inicio

            # Mostrar radio buttons para seleccionar opciones
            seleccion = st.radio(f"Selecciona el valor para {nombre_completo.split('.')[-1]}", opciones)
            if seleccion != 'Ninguno':
                fila_seleccionada = df.loc[df['descripcion'] == seleccion.split(' (')[0]]
                st.write(f"Descripción seleccionada: {fila_seleccionada['descripcion']}")
                valores_seleccionados[id_tabla] = fila_seleccionada['letra']
        else:
            st.write(f"No hay datos disponibles para {nombre_completo}")

    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# VISTA PREVIA
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Función para mostrar la vista previa
def mostrar_vista_previa():
    st.markdown("<h2>Vista previa del Proyecto</h2>", unsafe_allow_html=True)
    for _, row in df_puestos_proyecto.iterrows():
        st.markdown(f"### {row['nombre_puesto']}")  # Mostrar el nombre del puesto como título
        st.markdown("#### Complementos Específicos")
        # Mostrar los valores seleccionados para complementos específicos
        for id_tabla, letra in valores_seleccionados.items():
            if "especifico" in id_tabla:
                st.write(f"{id_tabla}: {letra}")
        st.markdown("#### Complementos de Destino")
        # Mostrar los valores seleccionados para complementos de destino
        for id_tabla, letra in valores_seleccionados.items():
            if "destino" in id_tabla:
                st.write(f"{id_tabla}: {letra}")

# Llamar a la función para mostrar la vista previa si hay valores seleccionados
if valores_seleccionados:
    mostrar_vista_previa()
