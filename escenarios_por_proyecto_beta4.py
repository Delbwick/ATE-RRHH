import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="APP Escenarios por proyecto ", page_icon="🤯")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula los Salarios Por Poryecto!")

# HTML personalizado para el encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be;
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
        h1, h2 {
            font-family: 'Arial', sans-serif;
            font-size: 17pt;
            text-align: left;
            color: #333333;
        }
        h3 {
            font-family: 'Arial', sans-serif;
            font-size: 14pt;
            text-align: center;
            color: #333333;
        }
        .cell {
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .header-cell {
            background-color: #e0e0e0;
            font-weight: bold;
            border: 1px solid black;
            padding: 10px;
            text-align: center;
        }
        .dataframe-cell {
            overflow-x: auto;
            overflow-y: auto;
            max-width: 100%;
            max-height: 200px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #2596be;
            color: white;
        }
        td {
            background-color: #f9f9f9;
        }
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
#st.write("Detalle de proyectos")



# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)
# Función para obtener proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM ate-rrhh-2024.Ate_kaibot_2024.proyecto
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener complementos para un proyecto
# Función para obtener complementos para un proyecto
def get_complementos(id_proyecto, tipo_complemento):
    query = f"""
        SELECT {tipo_complemento}
        FROM ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [{'complemento': row[0]} for row in results]


# Función para obtener los datos de una tabla específica
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM {nombre_tabla} LIMIT 100"
    df = client.query(query).result().to_dataframe().fillna('No disponible')
    return df

# Función para actualizar el porcentaje de importancia en BigQuery
def actualizar_porcentajes(id_proyecto, complementos, tipo_complemento, porcentajes):
    for complemento in complementos:
        porcentaje = porcentajes.get(complemento, 0)
        update_query = f"""
            UPDATE ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto
            SET porcentaje_importancia = {porcentaje}
            WHERE id_proyecto = {id_proyecto} AND {tipo_complemento} = '{complemento}'
        """
        client.query(update_query)

# Función para convertir los porcentajes introducidos por el usuario
def convertir_a_decimal(porcentaje_input):
    if isinstance(porcentaje_input, str) and "%" in porcentaje_input:
        try:
            porcentaje_decimal = float(porcentaje_input.replace('%', '').strip()) / 100
            return porcentaje_decimal
        except ValueError:
            return 0.0
    return float(porcentaje_input)  # Si no es un string con '%', devolverlo como está

# Función para validar la suma de los porcentajes
def validar_suma_porcentajes(porcentajes):
    return sum(porcentajes) == 1.0  # La suma debe ser 1 (100%)

# Función para obtener el complemento más relevante dependiendo de la categoría seleccionada
def filtrar_complementos_por_categoria(complementos, categoria_seleccionada):
    """
    Filtra los complementos según la categoría seleccionada.
    Categorías con letras más altas se consideran más relevantes.
    """
    categoria_orden = {
        'ap/e': 1,  # Más baja
        'a1': 2,
        'a2': 3,
        'b': 4,
        'c1': 5,
        'c2': 6
    }
    
    # Filtrar los complementos según la categoría seleccionada
    return [complemento for complemento in complementos if categoria_orden.get(categoria_seleccionada, 7) <= categoria_orden.get(complemento['complemento'], 7)]

# Mostrar la interfaz de usuario
# Mostrar la interfaz de usuario
def mostrar_interfaz():
    # Obtener los proyectos
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0]  # Selección por defecto del primer proyecto

    # Sidebar: Selector de proyecto
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))
    
    # Sidebar: Selector de categoría
    categorias = ["a1", "a2", "b", "c1", "c2", "ap/e"]
    categoria_seleccionada = st.sidebar.selectbox("Selecciona una categoría:", categorias)

    # Obtener el ID del proyecto seleccionado
    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    # Mostrar el ID seleccionado en el sidebar (opcional para verificación)
    if id_proyecto_seleccionado:
        st.sidebar.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")

    # Mostrar mensaje de advertencia
    st.markdown("""
    **Importante**: Los porcentajes para los complementos de destino y específicos deben sumar **100%**.
    Asegúrate de que la suma de los porcentajes de cada grupo sea exactamente 100%.
    """)

    # Mostrar los complementos de destino y específicos según la categoría
    if id_proyecto_seleccionado:
        complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
        complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")

        # Filtrar complementos por la categoría seleccionada
        complementos_destino_filtrados = filtrar_complementos_por_categoria(complementos_destino, categoria_seleccionada)
        complementos_especificos_filtrados = filtrar_complementos_por_categoria(complementos_especificos, categoria_seleccionada)

        # Mostrar complementos de destino filtrados
        for complemento in complementos_destino_filtrados:
            nombre_complemento = complemento['complemento']
            descripcion = complemento['descripcion']
            st.write(f"**{nombre_complemento} (Destino)**")
            st.write(f"Descripción: {descripcion}")
            # Mostrar tabla con los datos del complemento de destino
            nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_complemento}"
            df = obtener_datos_tabla(nombre_tabla)
            st.dataframe(df, use_container_width=True)

        # Mostrar complementos específicos filtrados
        for complemento in complementos_especificos_filtrados:
            nombre_complemento = complemento['complemento']
            descripcion = complemento['descripcion']
            st.write(f"**{nombre_complemento} (Específico)**")
            st.write(f"Descripción: {descripcion}")
            # Mostrar tabla con los datos del complemento específico
            nombre_tabla = f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_complemento}"
            df = obtener_datos_tabla(nombre_tabla)
            st.dataframe(df, use_container_width=True)

        # Botón para actualizar los porcentajes
        if st.button("Actualizar Porcentajes"):
            if not validar_suma_porcentajes(list(porcentajes_destino.values())):
                st.error("Los porcentajes de los complementos de destino no suman 100%. Por favor, revisa los valores.")
            elif not validar_suma_porcentajes(list(porcentajes_especificos.values())):
                st.error("Los porcentajes de los complementos específicos no suman 100%. Por favor, revisa los valores.")
            else:
                try:
                    actualizar_porcentajes(id_proyecto_seleccionado, complementos_destino, "complemento_destino", porcentajes_destino)
                    actualizar_porcentajes(id_proyecto_seleccionado, complementos_especificos, "complemento_especifico", porcentajes_especificos)
                    st.success("Porcentajes actualizados correctamente.")
                except Exception as e:
                    st.error(f"Error al actualizar los porcentajes: {e}")
    else:
        st.write("Selecciona un proyecto para actualizar los complementos.")

# Llamar a la función para mostrar la interfaz
mostrar_interfaz()
