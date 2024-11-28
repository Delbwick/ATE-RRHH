import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="App Valoraciones Puesto de trabajo - Manual Preliminar", page_icon="😬")
st.title("App Valoraciones Puesto de trabajo - Manual Preliminar")

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
#st.write("# Alta nuevo Proyecto")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
       1.	Qué es un libro de valoración, para qué se utiliza y cómo funciona.

Un libro de valoración se utiliza para valorar puestos de trabajo de forma objetiva. No se tienen en cuenta las personas que ocupan los puestos, sino los requisitos necesarios de cada puesto.
Se presentan los factores elegidos para valorar la organización, la graduación de los factores y el peso porcentual específico de cada factor en función de la organización.
El objetivo de la valoración de puestos de trabajo es establecer el valor relativo de los puestos de una organización, asignando a cada puesto una clasificación profesional y estableciendo una retribución en función de la valoración de diversos factores.
Hay que elegir los factores que se van a utilizar para realizar la valoración. Tanto los que determinan los complementos de destino como los que determinan los complementos específicos. La elección de los factores es relativamente libre mientras nos adaptemos a  los criterios legales.
Además, a cada factor se le asignará un peso porcentual específico. De esta forma, escalonamos la importancia del propio factor dentro de la organización.
Los factores de cada complemento, de destino, por un lado, y los específicos, por otro, deben sumar cada uno por su lado un 100%.
Los pesos porcentuales se refieren y se suelen escoger según la importancia o repetición de determinadas funciones en los puestos de trabajo de la institución, aunque la negociación con los representantes sindicales puede dar porcentajes poco habituales.
Asimismo, los factores se dividen en niveles alfabéticos (se pueden añadir más graduaciones de la A a la G si se desea) y cada grado tiene una valoración entre 0 y 100.
La combinación del peso específico del factor y la valoración por puntos nos permite trasladarnos a un resultado económico numérico de cada puesto de trabajo.

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
# Función para obtener los proyectos desde BigQuery
# Función para obtener los proyectos desde BigQuery
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

# Función para actualizar el porcentaje de importancia en BigQuery
def actualizar_porcentajes(id_proyecto, complementos, tipo_complemento, porcentajes):
    for complemento in complementos:
        porcentaje = porcentajes.get(complemento, 0)
        update_query = f"""
            UPDATE `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
            SET porcentaje_importancia = {porcentaje}
            WHERE id_proyecto = {id_proyecto} AND {tipo_complemento} = '{complemento}'
        """
        client.query(update_query)

# Función para convertir los porcentajes introducidos por el usuario
def convertir_a_decimal(porcentaje_input):
    if isinstance(porcentaje_input, str) and "%" in porcentaje_input:
        try:
            # Eliminar '%' y convertir a decimal
            porcentaje_decimal = float(porcentaje_input.replace('%', '').strip()) / 100
            return porcentaje_decimal
        except ValueError:
            return 0.0
    return float(porcentaje_input)  # Si no es un string con '%', devolverlo como está

# Mostrar la interfaz de usuario
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

    # Mostrar el ID seleccionado en el sidebar (opcional para verificación)
    if id_proyecto_seleccionado:
        st.sidebar.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")

    # Mostrar los complementos de destino y específicos
    if id_proyecto_seleccionado:
        # Obtener complementos
        complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
        complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")

        # Diccionario para los porcentajes de cada complemento
        porcentajes = {}

        # Mostrar inputs para porcentajes en los títulos
        st.subheader("Actualizar Porcentajes de Importancia")

        # Complementos de destino
        for complemento in complementos_destino:
            porcentaje_input = st.text_input(f"Porcentaje para {complemento} (Destino) - Ejemplo: 20%", value="0.0")
            porcentaje_decimal = convertir_a_decimal(porcentaje_input)  # Convertir a decimal
            porcentajes[complemento] = porcentaje_decimal
            # Mostrar tabla con los datos del complemento de destino
            nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            df = obtener_datos_tabla(nombre_tabla)
            st.write(f"**{complemento} (Destino) - Porcentaje: {porcentaje_decimal * 100}%**")
            st.dataframe(df, use_container_width=True)

        # Complementos específicos
        for complemento in complementos_especificos:
            porcentaje_input = st.text_input(f"Porcentaje para {complemento} (Específico) - Ejemplo: 20%", value="0.0")
            porcentaje_decimal = convertir_a_decimal(porcentaje_input)  # Convertir a decimal
            porcentajes[complemento] = porcentaje_decimal
            # Mostrar tabla con los datos del complemento específico
            nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            df = obtener_datos_tabla(nombre_tabla)
            st.write(f"**{complemento} (Específico) - Porcentaje: {porcentaje_decimal * 100}%**")
            st.dataframe(df, use_container_width=True)

        # Botón para actualizar los porcentajes
        if st.button("Actualizar Porcentajes"):
            # Actualizar los porcentajes en BigQuery
            try:
                actualizar_porcentajes(id_proyecto_seleccionado, complementos_destino, "complemento_destino", porcentajes)
                actualizar_porcentajes(id_proyecto_seleccionado, complementos_especificos, "complemento_especifico", porcentajes)
                st.success("Porcentajes actualizados correctamente.")
            except Exception as e:
                st.error(f"Error al actualizar los porcentajes: {e}")
    else:
        st.write("Selecciona un proyecto para actualizar los complementos.")
    
# Llamar a la función para mostrar la interfaz
mostrar_interfaz()
