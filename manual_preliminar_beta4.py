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
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener datos de complementos específicos o destino
def get_complementos(id_proyecto, tipo_complemento):
    query = f"""
        SELECT {tipo_complemento}
        FROM `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [row[0] for row in results]

# Función para obtener los datos de una tabla específica
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    df = client.query(query).result().to_dataframe().fillna('No disponible')
    return df

# Mostrar tablas de complementos en la página principal
# Mostrar tablas de complementos con input para porcentaje y botón de actualización
# Mostrar tablas de complementos con input para porcentaje y botón de actualización
# Mostrar tablas de complementos con input para porcentaje y botón de actualización
def mostrar_complementos(titulo, complementos, tipo_complemento, id_proyecto_seleccionado):
    st.subheader(titulo)
    for complemento in complementos:
        # Mostrar título del complemento
        st.write(f"**{complemento} ({tipo_complemento})**")

        # Crear un input box para el porcentaje de importancia
        porcentaje_input = st.text_input(
            f"Porcentaje de importancia para {complemento} ({tipo_complemento})",
            value="0%",  # Valor inicial
            key=f"porcentaje_{complemento}"
        )

        # Obtener y mostrar la tabla directamente desde BigQuery (como antes)
        nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
        query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
        try:
            df = client.query(query).to_dataframe().fillna('No disponible')
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error al consultar la tabla {complemento}: {e}")
            continue

        # Mostrar botón para actualizar el porcentaje
        if st.button(f"Actualizar {complemento}", key=f"btn_{complemento}"):
            try:
                # Eliminar el símbolo '%' y convertir el valor a un float
                porcentaje_str = porcentaje_input.strip('%')
                
                # Verificar que el valor es numérico
                if not porcentaje_str.replace('.', '', 1).isdigit():
                    st.error("Por favor, introduce un porcentaje válido (por ejemplo, 20%).")
                    continue
                
                # Convertir el porcentaje a valor decimal
                porcentaje_importancia = float(porcentaje_str) / 100  # Convertir a decimal (20% -> 0.20)
                
                # Validar que el porcentaje esté entre 0 y 1
                if porcentaje_importancia < 0 or porcentaje_importancia > 1:
                    st.error("Por favor, introduce un porcentaje válido (0% - 100%).")
                    continue

                # Actualizar el campo porcentaje_importancia en la tabla correspondiente
                update_query = f"""
                    UPDATE `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
                    SET porcentaje_importancia = {porcentaje_importancia}
                    WHERE id_proyecto = {id_proyecto_seleccionado} AND {tipo_complemento} = '{complemento}'
                """
                client.query(update_query)
                st.success(f"Porcentaje de {complemento} actualizado a {porcentaje_importancia * 100:.0f}%.")
            except ValueError:
                st.error("Por favor, introduce un porcentaje válido (por ejemplo, 20%).")
            except Exception as e:
                st.error(f"Error al actualizar el porcentaje: {e}")



# Obtener el ID del proyecto de la URL (si está presente)
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
id_proyecto_url = int(id_proyecto_url) if id_proyecto_url else None

# Obtener la lista de proyectos desde BigQuery
proyectos = get_proyectos()

# Extraer solo los nombres para mostrarlos en el selectbox
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]

# Si hay un id_proyecto en la URL, selecciona ese por defecto
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if proyecto['id'] == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]  # Primer proyecto como predeterminado

# Crear el sidebar con el selectbox
st.sidebar.title("Opciones")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

# Obtener el ID del proyecto seleccionado
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Mostrar el ID seleccionado en el sidebar (opcional para verificación)
if id_proyecto_seleccionado:
    st.sidebar.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")

# Si se ha seleccionado un proyecto, mostrar complementos
if id_proyecto_seleccionado:
    # Complementos de destino
    complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
    if complementos_destino:
        mostrar_complementos("Factores de Destino del Proyecto", complementos_destino, "destino", id_proyecto_seleccionado)
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")

    # Complementos específicos
    complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")
    if complementos_especificos:
        mostrar_complementos("Factores Específicos del Proyecto", complementos_especificos, "específico", id_proyecto_seleccionado)
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")

