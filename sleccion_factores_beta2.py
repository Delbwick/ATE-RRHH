import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH del Norte-Sewlecciona los factores", page_icon="✅")
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




def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

#

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
        AND option_value LIKE '%"destino"%'
    )
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

        # Columna 2 (30%): checkbox, selectbox y inputbox
        with col2:
            if st.checkbox(f"Seleccionar {nombre_tabla}", key=f"checkbox_{nombre_tabla}"):
                selected_factores.append((nombre_completo, id_tabla))

                # Crear un selectbox para seleccionar el valor
                opciones_destino = df_factores.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                seleccion_destino = st.selectbox(f"Selecciona un valor para {nombre_tabla}:", opciones_destino, key=f"destino_{nombre_tabla}")

                if seleccion_destino:
                    # Extraer letra y descripción seleccionada
                    selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                    selected_descripcion_destino = selected_descripcion_destino[:15] + "..."  # Truncar descripción si es muy larga

                    puntos_destino = df_factores.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]

                    # Input para porcentaje
                    porcentaje_destino = st.number_input(f"% {selected_descripcion_destino}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_destino_{nombre_tabla}')

                    # Calcular puntos ajustados
                    puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)

                    # Mostrar resultados en una nueva línea
                    st.markdown("<h4>Resultados de la Selección</h4>", unsafe_allow_html=True)
                    st.write(f"Seleccionaste la letra: {selected_letra_destino}")
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



st.markdown("<h2>Selecciona los Factores de complemento específico:</h2>", unsafe_allow_html=True)        
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento específico:")
# Diccionario de tablas de factores de compelemto específico
PAGES_TABLES_2 = {
    #"Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    #"Complejidad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    #"Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    #"Complemento de Destino": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_de_destino", "id_complemento_destino"),
    #"Complemento Específico por Año": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_específico_xaño", "id_complemento_especifico"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    #"Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    #"Conocimientos específicos al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_especificos", "id_conocimientos_especificos"),
    #"Definitivo?¿ ": ("ate-rrhh-2024.Ate_kaibot_2024.definitivo", "id_definitivo"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    #"Idioma del Proyecto": ("ate-rrhh-2024.Ate_kaibot_2024.idioma_proyecto", "id_idioma_proyecto"),
    "Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "Id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    "Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    #"Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    #"Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    #"Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_formacion", "id_nivel_formacion"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad"),
    #"Porcentajes Variables": ("ate-rrhh-2024.Ate_kaibot_2024.porcentajes_variables", "id_porcentajes_variables"),
    #"Proyectos": ("ate-rrhh-2024.Ate_kaibot_2024.proyecto", "id_proyecto"),
    #"Puestos": ("ate-rrhh-2024.Ate_kaibot_2024.puestos", "id_puesto"),
    #"Responsabilidad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
    #"Salario Base por Categoría y Año": ("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño", "id_salario_base"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno"),
    "RESPONSABILIDAD DE LA ACTIVIDAD": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD (PERJUICIOS)": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_perjuicios", "id_responsabilidad_actividad_perjuicios"),
    "RESPONSABILIDAD DE PERJUICIOS/INTERVENCIÓN SUBSANACIÓN": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_subsanacion", "id_responsabilidad_actividad_subsanacion"),
    "POLIVALENCIA": ("ate-rrhh-2024.Ate_kaibot_2024.polivalencia", "id_polivalencia"),
    "RESPONSABILIDAD PARCIAL SOBRE EL PRESUPUESTO": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_presupuesto", "id_responsabilidad_presupuesto"),


    # Agregar el resto de las tablas aquí
}

st.markdown("<h2>Selecciona los Factores de complemento Especifico version 2:</h2>", unsafe_allow_html=True)
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
        AND option_value LIKE '%"especifico"%'
    )
"""


# Ejecutar la consulta en BigQuery
query_job = client.query(query)
results = query_job.result()

# Construir el diccionario dinámicamente
PAGES_TABLES_2 = {}
for row in results:
    table_name = row.table_name
    column_name = row.column_name
    
    # Crear una entrada en el diccionario
    # El valor puede cambiar dependiendo de cómo quieras estructurar el diccionario
    PAGES_TABLES_2[table_name] = (f"{project_id}.{dataset_id}.{table_name}", column_name)

# Ver el diccionario construido dinámicamente
print(PAGES_TABLES_2)
selecciones_especifico = []
# Mostrar checkboxes para seleccionar las tablas de factores de complemento de destino
selected_factores_2 = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES_2.items():
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
            # Columna 2 (30%): checkbox, selectbox y inputbox
        with col2:
            if st.checkbox(f"Seleccionar {nombre_tabla}", key=f"checkbox_especifico_{nombre_tabla}"):
                selected_factores_2.append((nombre_completo, id_tabla))

                # Crear un selectbox para seleccionar el valor
                opciones_especifico = df_factores.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                seleccion_especifico = st.selectbox(f"Selecciona un valor para {nombre_tabla}:", opciones_especifico, key=f"destino_{nombre_tabla}")

                if seleccion_especifico:
                    # Extraer letra y descripción seleccionada
                    selected_letra_especifico, selected_descripcion_especifico = seleccion_especifico.split(" - ")
                    selected_descripcion_especifico = selected_descripcion_especifico[:15] + "..."  # Truncar descripción si es muy larga

                    puntos_especifico = df_factores.query(f"letra == '{selected_letra_especifico}'")['puntos'].values[0]

                    # Input para porcentaje
                    porcentaje_especifico = st.number_input(f"% {selected_descripcion_especifico}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{nombre_tabla}')

                    # Calcular puntos ajustados
                    puntos_ajustados_especifico = puntos_especifico * (porcentaje_especifico / 100)

                    # Mostrar resultados en una nueva línea
                    st.markdown("<h4>Resultados de la Selección</h4>", unsafe_allow_html=True)
                    st.write(f"Seleccionaste la letra: {selected_letra_especifico}")
                    st.write(f"Puntos originales: {puntos_especifico}")
                    st.write(f"Puntos ajustados (con {porcentaje_especifico}%): {puntos_ajustados_especifico:.2f}")

                    # Guardar en la lista de selecciones
                    selecciones_especifico.append({
                        'Tabla': nombre_tabla, 
                        'Letra': selected_letra_especifico, 
                        'Descripción': selected_descripcion_especifico, 
                        'Puntos': puntos_ajustados_especifico
                    })

# Mostrar las selecciones al final si hay datos seleccionados
if selecciones_especifico:
    st.markdown("<h3>Resumen de Factores de Complemento Especifico Seleccionados</h3>", unsafe_allow_html=True)
    for seleccion in selecciones_especifico:
        st.write(f"Tabla: {seleccion['Tabla']}, Letra: {seleccion['Letra']}, Descripción: {seleccion['Descripción']}, Puntos Ajustados: {seleccion['Puntos']:.2f}")




# Mostrar los datos seleccionados
#if selected_factores_2:
 #   st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
  #  st.write("Selecciona los valores específicos de las tablas seleccionadas:")

   # valores_seleccionados_2 = {}
  #  for nombre_completo, id_tabla in selected_factores_2:
   #     st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
    #    df = obtener_datos_bigquery(nombre_completo)
     #   if not df.empty:
      #      valores_seleccionados_2[id_tabla] = []
       #     for index, row in df.iterrows():
        #        # Crear la etiqueta del checkbox usando descripcion y letra
         #       etiqueta_checkbox = f"{row['descripcion']} ({row['letra']})"
          #      if st.checkbox(etiqueta_checkbox, key=f"{id_tabla}_{index}"):
           #         valores_seleccionados_2[id_tabla].append(row[id_tabla])

  #  st.write("Valores seleccionados:")
   # st.write(valores_seleccionados_2)

if selected_factores_2:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    #st.write("Selecciona los valores específicos de las tablas seleccionadas:") Esto valia con las radio button linea 386
    st.write("Tablas seleccionadas:")

    valores_seleccionados_2 = {}
    for nombre_completo, id_tabla in selected_factores_2:
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
                #valores_seleccionados_2[id_tabla] = fila_seleccionada[id_tabla]

    #st.write("Valores seleccionados:")
    #st.write(valores_seleccionados_2)



#CONSULTA DE INSERCION de proyecto

# Formulario de envío

# Función para abrir otra aplicación
#def abrir_otra_app():
    #url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    #webbrowser.open_new_tab(url_otra_app)

# Función para obtener datos de BigQuery








#nueva funcion alta nuevo proyecto
# Añadir el botón dentro de un formulario
# Añadir el botón dentro de un formulario
with st.form("alta_proyecto"):
    st.markdown("### Alta nuevo proyecto")
    
    # Campos para ingresar detalles del nuevo proyecto
    nombre = st.text_input("Nombre del proyecto")
    descripcion = st.text_area("Descripción del proyecto")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_fin = st.date_input("Fecha de fin")
    proyecto_activo = st.checkbox("Proyecto activo")

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
            new_id_proyecto = max_id + 1 if max_id is not None else 1

            # Insertar el nuevo proyecto en la tabla de proyectos
            query_kai_insert = f"""
                INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.proyecto` 
                (id_projecto, nombre, descripcion, fecha_comienzo, fecha_fin, proyecto_activo) 
                VALUES 
                ({new_id_proyecto}, '{nombre.replace("'", "''")}', '{descripcion.replace("'", "''")}', '{fecha_inicio}', '{fecha_fin}', {proyecto_activo})
            """
            query_job_kai_insert = client.query(query_kai_insert)
            query_job_kai_insert.result()  # Asegurarse de que la consulta se complete

            # Preparar la inserción de los puestos seleccionados
            rows_to_insert_puestos = []
            for descripcion in selected_puestos:
                # Obtener el id_puesto
                query = f"""
                    SELECT id_puesto
                    FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
                    WHERE descripcion = @descripcion
                """
                query_job = client.query(query, job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("descripcion", "STRING", descripcion)
                    ]
                ))
                results = query_job.result()

                id_puesto = None
                for row in results:
                    id_puesto = row.id_puesto
                    break

                if id_puesto is not None:
                    # Insertar cada combinación de factores específicos y de destino
                    for nombre_completo_f in [nombre_completo for nombre_completo, _ in selected_factores]:
                        for nombre_completo_d in [nombre_completo for nombre_completo, _ in selected_factores_2]:
                            row = {
                                'id_proyecto': new_id_proyecto,
                                'id_puesto': id_puesto,
                                'complementos_especificos': nombre_completo_f,
                                'complementos_destino': nombre_completo_d,
                                #'puntos_ajustados_especifico': puntos_ajustados_especifico,  # Nuevo campo para puntos específicos calculados
                                'puntos_ajustados_especifico': puntos_especifico,  # Nuevo campo para puntos específicos originales
                                'puntos_ajustados_destino': puntos_destino  # Nuevo campo para puntos destino
                            }
                            rows_to_insert_puestos.append(row)

            # Insertar en la tabla de factores seleccionados
            if rows_to_insert_puestos:
                try:
                    query_insert_factores = """
                        INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
                        (id_proyecto, id_puesto, complementos_especificos, complementos_destino, puntos_ajustados_especifico, puntos_ajustados_destino)
                        VALUES
                    """
                    valores = []
                    for row in rows_to_insert_puestos:
                        valores.append(f"({row['id_proyecto']}, {row['id_puesto']}, '{row['complementos_especificos'].replace("'", "''")}', '{row['complementos_destino'].replace("'", "''")}', {row['puntos_ajustados_especifico']}, {row['puntos_ajustados_destino']})")

                    query_insert_factores += ", ".join(valores)

                    query_job_insert = client.query(query_insert_factores)
                    query_job_insert.result()  # Asegurarse de que la consulta se complete

                    st.success("Proyecto y complementos insertados correctamente.")
                except Exception as e:
                    st.error(f"Error al insertar los complementos seleccionados: {e}")

        except Exception as e:
            st.error(f"Error al crear el proyecto: {e}")



#fin funcion nueva






# Crear un botón
st.markdown("""
    <a href="https://ate-rrhh-9keb7jlgxce6dthzz8gdzx.streamlit.app/" target="_blank">
        <button style="background-color:Green;padding:10px;border-radius:5px;color:white;border:none;">
            Ir a la APP de Cálculo de Valoraciones
        </button>
    </a>
    """, unsafe_allow_html=True)
