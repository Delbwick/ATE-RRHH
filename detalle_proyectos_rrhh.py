import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH Proyectos", page_icon="💾")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula tu Proyecto!")

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
st.write("Detalle de proyectos")
# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

#>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<
#CODIGO DE LA APLICACION
#<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>
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

# Mostrar el encabezado y línea separadora
st.markdown("<h2>Selector de Proyectos</h2>", unsafe_allow_html=True)
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

# Puedes usar 'id_proyecto_seleccionado' en tu lógica posterior según sea necesario


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#PUESTOS POR PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#Vamos extraer los datos de puestos de ese proyecto
# Mostrar el encabezado y línea separadora
st.markdown("<h2>Puestos asociados a ese proyecto</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)


    #probamos otra manera de manipular las fechas

    # Consulta SQL 
query_puestos_proyecto = f"""
        SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        WHERE id_puesto IN (
        SELECT id_puesto FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto`
        WHERE id_proyecto = {id_proyecto_seleccionado})
    """

query_job_puestos_proyecto = client.query(query_puestos_proyecto)
results_puestos_proyecto = query_job_puestos_proyecto.result()
df_puestos_proyecto = pd.DataFrame(data=[row.values() for row in results_puestos_proyecto], columns=[field.name for field in results_puestos_proyecto.schema])
st.dataframe(df_puestos_proyecto)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#COMPLEMENTOS DE DESTINO POR PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#Vamos extraer los datos de puestos de ese proyecto
# Mostrar el encabezado y línea separadora
st.markdown("<h2>Complementos de destino asociados a ese proyecto</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)


    #probamos otra manera de manipular las fechas

    # Consulta SQL 

#query_formacion_proyecto = f"""
 #       SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.formacion`
  #      WHERE id_formacion_general IN (
   #     SELECT id_formacion_general FROM `ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto`
     #   WHERE id_proyecto = {id_proyecto_seleccionado})
    #"""

#query_job_formacion_proyecto = client.query(query_formacion_proyecto)
#results_puestos_proyecto = query_job_formacion_proyecto.result()
#df_formacion_proyecto = pd.DataFrame(data=[row.values() for row in results_puestos_proyecto], columns=[field.name for field in results_puestos_proyecto.schema])
#st.markdown("<h3>Formacion</h3>", unsafe_allow_html=True)
#st.dataframe(df_formacion_proyecto)






#vamos aintentar una funcion más felxible
# Diccionario con las tablas y campos correspondientes
PAGES_TABLES = {
    "Formación": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Autonomía-Complejidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica destino": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Especialización destino /ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA/": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    "Responsabilidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad")
}

# Esta función genera y ejecuta la consulta SQL para una página específica
def execute_query_for_page(page_name, id_proyecto):
    if page_name in PAGES_TABLES:
        table_name, id_field = PAGES_TABLES[page_name]
        query = f"""
            SELECT * FROM `{table_name}`
            WHERE {id_field} IN (
                SELECT {id_field} FROM `ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto`
                WHERE id_proyecto = {id_proyecto}
            )
        """
        query_job = client.query(query)
        results = query_job.result()
        df = pd.DataFrame(data=[row.values() for row in results], columns=[field.name for field in results.schema])
        return df
    else:
        return None

# Obtener el id_proyecto seleccionado desde un inputbox en Streamlit
#id_proyecto_seleccionado = st.number_input('Ingrese el ID del proyecto', min_value=1)

# Iterar sobre todas las páginas en el diccionario y ejecutar las consultas
for page_name in PAGES_TABLES:
    st.markdown(f"<h3>{page_name}</h3>", unsafe_allow_html=True)
    df = execute_query_for_page(page_name, id_proyecto_seleccionado)
    if df is not None:
        st.dataframe(df)
    else:
        st.write(f"No se encontró la página '{page_name}' en el diccionario o no se pudo ejecutar la consulta.")


st.markdown("<h2>Complementos Especificos</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)



PAGES_TABLES_2 = {
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "Especialización": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "Id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    "Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno"),
    # Agregar el resto de las tablas aquí
}

def execute_query_for_page(page_name, id_proyecto):
    if page_name in PAGES_TABLES_2:
        table_name, id_field = PAGES_TABLES_2[page_name]
        query = f"""
            SELECT * FROM `{table_name}`
            WHERE {id_field} IN (
                SELECT {id_field} FROM `ate-rrhh-2024.Ate_kaibot_2024.complementos_especificos_por_proyecto`
                WHERE id_proyecto = {id_proyecto}
            )
        """
        query_job = client.query(query)
        results = query_job.result()
        df = pd.DataFrame(data=[row.values() for row in results], columns=[field.name for field in results.schema])
        if not df.empty:
            total_puntos = df['puntos'].iloc[0]
            
        else:
            total_puntos = 0
        return df, total_puntos
    else:
        return None, 0

# Obtener el id_proyecto seleccionado desde un inputbox en Streamlit
#id_proyecto_seleccionado = st.number_input('Ingrese el ID del proyecto', min_value=1)
# Variable para acumular los puntos totales
total_puntos_especificos = 0

# Iterar sobre todas las páginas en el diccionario y ejecutar las consultas
for page_name in PAGES_TABLES_2:
    st.markdown(f"<h3>{page_name}</h3>", unsafe_allow_html=True)
    df = execute_query_for_page(page_name, id_proyecto_seleccionado)
    df, total_puntos = execute_query_for_page(page_name, id_proyecto_seleccionado)
    if df is not None:
        st.dataframe(df)
        st.write(f"Total de puntos: {total_puntos}")
        total_puntos_especificos += total_puntos
    else:
        st.write(f"No se encontró la página '{page_name}' en el diccionario o no se pudo ejecutar la consulta.")

# Mostrar el total acumulado de puntos específicos
st.write(f"Total acumulado de puntos específicos: {total_puntos_especificos}")




PAGES_TABLES = {
    "Formación": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Autonomía-Complejidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica destino": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Especialización destino /ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA/": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    "Responsabilidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad")
}

PAGES_TABLES_2 = {
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "Especialización": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "Id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    "Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno"),
}

# Esta función genera y ejecuta la consulta SQL para una página específica
# Esta función genera y ejecuta la consulta SQL para una página específica
def execute_query_for_page(page_name, id_proyecto, table_dict, complementos_table):
    if page_name in table_dict:
        table_name, id_field = table_dict[page_name]
        query = f"""
            SELECT * FROM `{table_name}`
            WHERE {id_field} IN (
                SELECT {id_field} FROM `{complementos_table}`
                WHERE id_proyecto = @id_proyecto
            )
        """
        try:
            query_job = client.query(query, job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("id_proyecto", "INT64", int(id_proyecto))
                ]
            ))
            results = query_job.result()
            df = pd.DataFrame(data=[list(row.values()) for row in results], columns=[field.name for field in results.schema])
            return df
        except Exception as e:
            st.error(f"Error ejecutando la consulta para {page_name}: {e}")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    else:
        st.error(f"Página {page_name} no encontrada en el diccionario proporcionado.")
        return pd.DataFrame()  # Retorna un DataFrame vacío si la página no se encuentra

# Ejecuta las consultas para todas las páginas y combina los resultados en una única tabla
def get_combined_table(id_proyecto, table_dict, complementos_table):
    combined_df = pd.DataFrame()
    
    for page_name in table_dict:
        df = execute_query_for_page(page_name, id_proyecto, table_dict, complementos_table)
        if not df.empty:  # Verifica si el DataFrame no está vacío
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df

# Interfaz de Streamlit
st.title("Consulta de Proyectos")
id_proyecto = st.text_input("Ingrese el ID del proyecto:")

if id_proyecto:
    with st.spinner('Ejecutando consultas...'):
        result_df_general = get_combined_table(id_proyecto, PAGES_TABLES, "ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto")
        result_df_especifico = get_combined_table(id_proyecto, PAGES_TABLES_2, "ate-rrhh-2024.Ate_kaibot_2024.complementos_especificos_por_proyecto")
    
    if not result_df_general.empty:
        st.success("Consulta complemento destino exitosa!")
        st.dataframe(result_df_general)
        total_destino = result_df_general['puntos'].sum()
        st.write(f"Total puntos (General): {total_destino}")
    else:
        st.warning("No se encontraron datos para el ID de proyecto proporcionado en la consulta general.")
    
    if not result_df_especifico.empty:
        st.success("Consulta de complemento específico exitosa!")
        st.dataframe(result_df_especifico)
        total_especifico = result_df_especifico['puntos'].sum()
        st.write(f"Total puntos (Específico): {total_especifico}")
        st.write(f"Total puntos: {total_especifico}+{total_destino}")
        total_puntos=total_especifico+total_destino
    else:
        st.warning("No se encontraron datos para el ID de proyecto proporcionado en la consulta de complemento específico.")

#>>>>>>>>>Valor por punto especifico por poryecto
#ºel valor por peso especifico por poryecto va variar dependiendo del ayntamiento del año y de la legislacion por lo que tendremos que tener una tabla
#puntos por peso especifico por año
valor_punto_especifico_proyecto = st.number_input('valor_punto_especifico_proyecto', min_value=1)
valor_especifico_puesto=total_puntos*valor_punto_especifico_proyecto
st.write(f"Valor especifico del puesto de trabajo: {valor_especifico_puesto}")

