import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="Escenarios - Valoraciones Puesto de trabajo", page_icon="⚙️")
st.title("Escenarios de Valoración de Puestos de Trabajo")

# HTML personalizado para el encabezado
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
            background-color: var(--color-secundario);
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

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://kaibot.es/wp-content/uploads/2024/11/banner-app-1.png" alt="Logo"></div>', unsafe_allow_html=True)

# Título adicional para la app
st.markdown("<h2 style='color:#007d9a; font-size: 24pt;'>Cálculo de Escenarios de Valoración de Puestos de Trabajo</h2>", unsafe_allow_html=True)

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
       1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.

Un libro de valoración se utiliza para valorar puestos de trabajo de forma objetiva. No se tienen en cuenta las personas que ocupan los puestos, sino los requisitos necesarios de cada puesto...
    </h3>
</div>
"""
# Renderizar el contenido HTML
st.markdown(scrollable_text_html, unsafe_allow_html=True)

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener los complementos para un proyecto
def get_complementos(id_proyecto, tipo_complemento):
    query = f"""
        SELECT {tipo_complemento}
        FROM `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [row[0] for row in results]

# Función para obtener los datos de una tabla específica (complementos)
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    df = client.query(query).result().to_dataframe().fillna('No disponible')
    return df

# Función para obtener la descripción de una tabla
def obtener_descripcion_tabla(nombre_tabla):
    query = f"DESCRIBE `{nombre_tabla}`"
    result = client.query(query).result()
    return result

# Función para mostrar la interfaz
def mostrar_interfaz():
    # Obtener los proyectos
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0]  # Selección por defecto del primer proyecto

    # Crear el sidebar con el selectbox
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

    # Obtener el ID del proyecto seleccionado
    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    # Mostrar mensaje de advertencia
    st.markdown("""
    **Importante**: Los porcentajes para los complementos de destino y específicos deben sumar **100%**.
    Asegúrate de que la suma de los porcentajes de cada grupo sea exactamente 100%.
    """)

    # Mostrar los complementos de destino y específicos
    if id_proyecto_seleccionado:
        # Obtener complementos
        complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
        complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")

        # Complementos de destino
        for complemento in complementos_destino:
            # Mostrar la descripción de la tabla
            nombre_tabla_destino = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            descripcion_destino = obtener_descripcion_tabla(nombre_tabla_destino)
            st.write(f"**Descripción de la tabla: {complemento} (Destino)**")
            st.write(descripcion_destino)

            # Mostrar los datos de la tabla
            df_destino = obtener_datos_tabla(nombre_tabla_destino)
            st.write(f"**Datos de la tabla {complemento} (Destino):**")
            st.dataframe(df_destino)

        # Complementos específicos
        for complemento in complementos_especificos:
            # Mostrar la descripción de la tabla
            nombre_tabla_especifico = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            descripcion_especifico = obtener_descripcion_tabla(nombre_tabla_especifico)
            st.write(f"**Descripción de la tabla: {complemento} (Específico)**")
            st.write(descripcion_especifico)

            # Mostrar los datos de la tabla
            df_especifico = obtener_datos_tabla(nombre_tabla_especifico)
            st.write(f"**Datos de la tabla {complemento} (Específico):**")
            st.dataframe(df_especifico)

# Llamar a la función para mostrar la interfaz
mostrar_interfaz()
