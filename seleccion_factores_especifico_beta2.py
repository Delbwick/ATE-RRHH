import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH del Norte-Selecciona los factores de complemento Especificos", page_icon="🎯")
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
guardar_selecciones_html = """
    <style>
        .guardar-btn {
            background-color: green;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .guardar-btn:hover {
            background-color: blue;  /* Cambiar a azul en hover */
        }
    </style>
    <button class="guardar-btn" onclick="guardar_selecciones()">Guardar selecciones</button>
    <script>
        function guardar_selecciones() {
            document.getElementById('guardar-btn').click();
        }
    </script>
"""


# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
st.write("# Seleccion Factores Complemento Específico por proyecto")

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
# Función para seleccionar los proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    proyectos = [{'id': row.id_projecto, 'nombre': row.nombre} for row in results]
    return proyectos

# Obtener el ID del proyecto de la URL (si está presente)
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]

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

# Mostrar el ID seleccionado (para fines de verificación)
if id_proyecto_seleccionado:
    st.sidebar.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")

# Crear el selectbox en el sidebar con las opciones
opcion = st.sidebar.selectbox(
    "Seleccione una categoría:",
    ("Factores de Especializacion Dificultad Técnica", 
     "Factores de Responsabilidad", 
     "Factores de Peligrosidad", 
     "Factores de Penosidad",
     "Factores de Complejidad")
)

# Modificar la etiqueta en función de la opción seleccionada
if opcion == "Factores de Especializacion Dificultad Técnica":
    etiqueta = "dificultad_tecnica"
elif opcion == "Factores de Penosidad":
    etiqueta = "factor_penosidad"
elif opcion == "Factores de Responsabilidad":
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
st.markdown("<h2>Es necesario que selecciones por lo menos un Factor</h2>", unsafe_allow_html=True)
st.markdown("<p>Poe defecto el PRIMERO SIEMPRE ESTÄ SELECCIONADO</p>", unsafe_allow_html=True)
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
selected_factores = []
selecciones_destino = []  # Aseguramos que la lista de selecciones esté vacía al iniciar

# Seleccionar la primera tabla por defecto
primer_nombre_tabla, (primer_nombre_completo, primer_id_tabla) = next(iter(PAGES_TABLES.items()))
selected_factores.append((primer_nombre_completo, primer_id_tabla))

# Bucle para recorrer PAGES_TABLES y mostrar opciones
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
            # Determinar si la tabla actual es la primera de PAGES_TABLES para marcarla por defecto
            is_selected = (nombre_tabla == primer_nombre_tabla)

            if st.checkbox(f"Seleccionar {nombre_tabla}", key=f"checkbox_{nombre_tabla}", value=is_selected):
                if (nombre_completo, id_tabla) not in selected_factores:
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

# Definir el nombre de la tabla donde guardaremos las selecciones
tabla_seleccion = f"{project_id}.{dataset_id}.complemento_especifico_x_proyecto"

# Crear la función para insertar solo el ID del proyecto y el nombre de la tabla seleccionada
def guardar_selecciones_en_bigquery(tabla, id_proyecto, selecciones):
    """Guarda solo el ID del proyecto y el nombre de la tabla de factores seleccionada en BigQuery."""
    registros = []
    for seleccion in selecciones:
        registros.append({
            "id_proyecto": id_proyecto,            # ID del proyecto seleccionado
            "complemento_especifico": seleccion['Tabla']  # Nombre de la tabla de factores seleccionada
        })
    
    # Convertir a DataFrame y subir a BigQuery
    df_registros = pd.DataFrame(registros)
    client.load_table_from_dataframe(df_registros, tabla).result()
    st.success("Las selecciones se han guardado correctamente en BigQuery.")

# Almacenar los complementos seleccionados
if st.button("Guardar selecciones"):
    # Llamar a la función para guardar solo el ID del proyecto y la tabla seleccionada en BigQuery
    guardar_selecciones_en_bigquery(tabla_seleccion, id_proyecto_seleccionado, selecciones_destino)






# Crear un botón
st.markdown("""
    <a href="https://ate-rrhh-izvsuxhpkanqfvdymwklej.streamlit.app/" target="_blank">
        <button style="background-color:Green;padding:10px;border-radius:5px;color:white;border:none;">
            Ir a Actualizacion de factores Seleccionados
        </button>
    </a>
    """, unsafe_allow_html=True)
