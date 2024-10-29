import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH del Norte-Sewlecciona los factores de complemento de Destino", page_icon="✅")
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
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
st.write("# Seleccion Factores por proyecto")

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
# Crear el sidebar
# Crear el sidebar
st.sidebar.title("Opciones")
opcion_proyecto = st.sidebar.selectbox(
    "Seleccione un Proyectos:",
    ("Acme", 
     "Acme2", 
     "Acme3", 
     "Acme4")
)


# Crear el selectbox en el sidebar con las opciones
opcion = st.sidebar.selectbox(
    "Seleccione una categoría:",
    ("Factores de formación", 
     "Factores de jerarquización o mando", 
     "Factores de responsabilidad", 
     "Factores de iniciativa o autonomía",
     "Factores de Complejidad")
)

# Modificar la etiqueta en función de la opción seleccionada
if opcion == "Factores de formación":
    etiqueta = "formacion"
elif opcion == "Factores de jerarquización o mando":
    etiqueta = "factor_jerarquizacion"
elif opcion == "Factores de responsabilidad":
    etiqueta = "factor_responsabilidad"
elif opcion == "Factores de iniciativa o autonomía":
    etiqueta = "factor_iniciativa"
elif opcion == "Factores de Complejidad":
    etiqueta = "factor_complejidad"
else:
    etiqueta = ""


#
def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')
#Finde Primeros campos de proyectos
#para las selecciones de los factores que ya estan seleccionadops
def obtener_datos_bigquery(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"  # Ajusta el límite según sea necesario
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df




st.markdown("<h2>Selecciona los Factores de complemento de destino version 2:</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Nombre del proyecto y dataset
project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Consulta SQL para obtener las tablas y sus columnas principales (por ejemplo, la primera columna)
# Modificar la consulta para excluir tablas con nombres concretos
query = f"""
    SELECT table_name, column_name
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE ordinal_position = 1
    AND table_name IN (
        SELECT table_name
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_OPTIONS`
        WHERE option_name = 'labels'
        AND option_value LIKE '%"{etiqueta}"%'
    )
    ORDER BY column_name  -- Asumiendo que column_name es el campo string 'letra'
"""


# Ejecutar la consulta en BigQuery
query_job = client.query(query)
results = query_job.result()

# Construir el diccionario dinámicamente
PAGES_TABLES = {}
for row in results:
    table_name = row.table_name
    column_name = row.column_name
    
    # Crear una entrada en el diccionario
    # El valor puede cambiar dependiendo de cómo quieras estructurar el diccionario
    PAGES_TABLES[table_name] = (f"{project_id}.{dataset_id}.{table_name}", column_name)

# Ver el diccionario construido dinámicamente
print(PAGES_TABLES)

# Inicializar lista de selecciones de destino
# Inicializar lista de selecciones de destino
selecciones_destino = []

# Mostrar checkboxes para seleccionar las tablas de factores de complemento de destino
selected_factores = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES.items():
    # Separador para cada tabla
    st.markdown("<hr>", unsafe_allow_html=True)

    # Crear dos columnas: 70% para el dataframe y 30% para selectbox/inputbox
    col1, col2 = st.columns([7, 3])  # 70% y 30%

    # Obtener los datos de la tabla seleccionada
    table = client.get_table(nombre_completo)
    descripcion = table.description

    # Mostrar el dataframe en la columna 1 (70%)
    df_factores = obtener_datos_tabla(nombre_completo)
    if not df_factores.empty:
        with col1:
            st.write(f"Factores para la tabla: {nombre_tabla}")
            st.write(descripcion)
            st.dataframe(df_factores)

        # Columna 2 (30%): checkbox e inputbox
        with col2:
            if st.checkbox(f"Seleccionar {nombre_tabla}", key=f"checkbox_{nombre_tabla}"):
                selected_factores.append((nombre_completo, id_tabla))

                # Selección automática de la primera letra y descripción disponibles en df_factores
                primera_fila = df_factores.iloc[0]
                selected_letra_destino = primera_fila['letra']
                selected_descripcion_destino = primera_fila['descripcion'][:15] + "..."  # Truncar descripción si es muy larga

                puntos_destino = primera_fila['puntos']

                # Input para porcentaje
                porcentaje_destino = st.number_input(f"% {selected_descripcion_destino}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_destino_{nombre_tabla}')

                # Calcular puntos ajustados
                puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)

                # Mostrar resultados en una nueva línea
                st.markdown("<h4>Resultados de la Selección</h4>", unsafe_allow_html=True)
                #st.write(f"Seleccionaste la letra: {selected_letra_destino}")
                st.write(f"Puntos originales: {puntos_destino}")
                st.write(f"Puntos ajustados (con {porcentaje_destino}%): {puntos_ajustados_destino:.2f}")

                # Guardar en la lista de selecciones
                selecciones_destino.append({
                    'Tabla': nombre_tabla, 
                    'Letra': selected_letra_destino, 
                    'Descripción': selected_descripcion_destino, 
                    'Puntos': puntos_ajustados_destino
                })


# Mostrar las selecciones al final si hay datos seleccionados
if selecciones_destino:
    st.markdown("<h3>Resumen de Factores de Complemento de Destino Seleccionados</h3>", unsafe_allow_html=True)
    for seleccion in selecciones_destino:
        st.write(f"Tabla: {seleccion['Tabla']}, Letra: {seleccion['Letra']}, Descripción: {seleccion['Descripción']}, Puntos Ajustados: {seleccion['Puntos']:.2f}")

# Mostrar los datos seleccionados
#if selected_factores:
  #  st.write("Selecciona los valores específicos de las tablas seleccionadas:")
 #   st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

#    valores_seleccionados = {}
 #   for nombre_completo, id_tabla in selected_factores:
  #      st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
   #     df = obtener_datos_bigquery(nombre_completo)
    #    if not df.empty:
     #       valores_seleccionados[id_tabla] = []
      #      for index, row in df.iterrows():
                # Crear la etiqueta del checkbox usando descripcion y letra
       #         etiqueta_checkbox = f"{row['descripcion']} ({row['letra']})"
        #        if st.checkbox(etiqueta_checkbox, key=f"{id_tabla}_{index}"):
         #           valores_seleccionados[id_tabla].append(row[id_tabla])

  #  st.write("Valores seleccionados:")
   # st.write(valores_seleccionados)

if selected_factores:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    #st.write("Selecciona los valores específicos de las tablas seleccionadas:") Esto valia cuando teniamos los radioboton (linea 283)
    st.write("Tablas seleccionadas:")


    valores_seleccionados = {}
    for nombre_completo, id_tabla in selected_factores:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(nombre_completo)
        if not df.empty:
            # Crear lista de opciones para st.radio
            opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df.iterrows()]
            opciones.insert(0, 'Ninguno')  # Añadir opción 'Ninguno' al inicio

            # Mostrar radio buttons para seleccionar una opción
            #seleccion = st.radio(f"Seleccione una opción para {nombre_completo.split('.')[-1]}:", opciones, key=f"radio_{id_tabla}")

            #if seleccion != 'Ninguno':
                # Encontrar el valor seleccionado
                #fila_seleccionada = df.loc[opciones.index(seleccion) - 1]  # -1 para compensar 'Ninguno'
                #valores_seleccionados[id_tabla] = fila_seleccionada[id_tabla]

    #st.write("Valores seleccionados:")
    #st.write(valores_seleccionados)






#CONSULTA DE INSERCION de proyecto

# Formulario de envío

# Función para abrir otra aplicación
#def abrir_otra_app():
    #url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    #webbrowser.open_new_tab(url_otra_app)

# Función para obtener datos de BigQuery













# Crear un botón
st.markdown("""
    <a href="https://ate-rrhh-9keb7jlgxce6dthzz8gdzx.streamlit.app/" target="_blank">
        <button style="background-color:Green;padding:10px;border-radius:5px;color:white;border:none;">
            Ir a la APP de Cálculo de Valoraciones
        </button>
    </a>
    """, unsafe_allow_html=True)
