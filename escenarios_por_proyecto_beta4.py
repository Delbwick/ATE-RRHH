import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH Cálculo de Puestos por Proyecto y por puesto ", page_icon="🤯")
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
def get_complementos(id_proyecto, tipo_complemento):
    query = f"""
        SELECT {tipo_complemento}, descripcion
        FROM ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [{'complemento': row[0], 'descripcion': row[1]} for row in results]

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
def mostrar_interfaz():

 
