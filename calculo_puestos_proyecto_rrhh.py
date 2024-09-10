import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid


# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH Cálculo de Puestos por Proyecto", page_icon="🧑‍🏫")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula los Salarios Por Poryecto!")

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
        margin-bottom: 20px; /* Margen inferior para toda la "tabla" */
    }
    .header-cell {
        background-color: #e0e0e0;
        font-weight: bold;
        border: 1px solid black;
        padding: 10px;
        text-align: center;
       
    }
    .dataframe-cell {
        overflow-x: auto;  /* Habilita scroll horizontal */
        overflow-y: auto;  /* Habilita scroll vertical */
        max-width: 100%;   /* Limita el ancho al 100% del contenedor */
        max-height: 200px; /* Limita la altura a 300px y habilita scroll */
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
#st.dataframe(df_puestos_proyecto)
st.markdown(f"<div class='cell dataframe-cell'>{df_puestos_proyecto.to_html(index=False)}</div>", unsafe_allow_html=True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#COMPLEMENTOS DE DESTINO POR PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#Vamos extraer los datos de puestos de ese proyecto
# Mostrar el encabezado y línea separadora
st.markdown("<h1>Complementos de destino asociados a ese proyecto</h1>", unsafe_allow_html=True)
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
        if not df.empty:
            total_puntos_destino_1 = df['puntos'].iloc[0]
            
        else:
            total_puntos_destino_1 = 0
        return df, total_puntos_destino_1
    else:
        return None, 0

# Obtener el id_proyecto seleccionado desde un inputbox en Streamlit
# id_proyecto_seleccionado = st.number_input('Ingrese el ID del proyecto', min_value=1)

# Iterar sobre todas las páginas en el diccionario y ejecutar las consultas
# Iterar sobre todas las páginas en el diccionario y ejecutar las consultas
puntos_destino_peso_total=0
peso_especifico_por_proyecto = {}  # Diccionario para almacenar los pesos por página

for page_name in PAGES_TABLES:
    df = execute_query_for_page(page_name, id_proyecto_seleccionado)
    df,total_puntos_destino_1 = execute_query_for_page(page_name, id_proyecto_seleccionado)

    if df is not None and not df.empty:  # Verificar si el DataFrame no está vacío
    # Crear tres columnas con anchos 50%, 25%, 25%
        col1, col2, col3,col4 = st.columns([2, 1, 1,1])

    # Contenido de la primera columna (50%)
        with col1:
            st.markdown(f"<div class='header-cell'><h3>{page_name}</h3></div>", unsafe_allow_html=True)
        
            # Ajuste del DataFrame con scroll horizontal
            st.markdown(f"<div class='cell dataframe-cell'>{df.to_html(index=False)}</div>", unsafe_allow_html=True)
        
            # Total de puntos
            st.markdown(f"<div class='cell'><b>Total de puntos: {total_puntos_destino_1}</b></div>", unsafe_allow_html=True)

    # Contenido de la segunda columna (25%)
        with col2:
            st.markdown(f"<div class='header-cell'><b>Peso del complemento de destino para {page_name}</b></div>", unsafe_allow_html=True)
            peso_especifico_por_proyecto[page_name] = st.number_input(
                f'Peso del complemento de destino para {page_name}', 
                min_value=0.0,
                key=f'{page_name}_peso'
            )


    # Contenido de la tercera columna (25%)
        with col3:
            puntos_destino_peso = total_puntos_destino_1 * peso_especifico_por_proyecto[page_name] / 100
            st.markdown(f"<div class='header-cell'><b>Total de puntos de destino con el peso específico</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cell'>{puntos_destino_peso}</div>", unsafe_allow_html=True)
            puntos_destino_peso_total += puntos_destino_peso
        
        with col4:
         # Diccionario para almacenar las notas específicas
            nota_especifico = {}
            st.markdown(f"<div class='header-cell'><b>Notas</b></div>", unsafe_allow_html=True)
    
    # Input de texto para la nota específica por proyecto
            nota_especifico[page_name] = st.text_input(
                f'Nota específica para {page_name}',
                key=f'{page_name}_nota'
            )
            
    else:
        # No mostramos nada o mostramos un mensaje específico si la tabla no tiene datos
        st.write(f"No se encontraron datos para '{page_name}' en la consulta.")

st.markdown(f"<div class='cell'><b>Suma de % de Peso Específico(Ha de ser Igual a 100%: {peso_especifico_por_proyecto}</b></div>", unsafe_allow_html=True)
st.markdown(f"<div class='cell'><b>Suma de Puntos x el peso específico->VALORACIÓN: {puntos_destino_peso_total}</b></div>", unsafe_allow_html=True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#COMPLEMENTOS Especificos POR PROYECTO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#Vamos extraer los datos de puestos de ese proyecto
# Mostrar el encabezado y línea separadora
st.markdown("<h2>Complementos específicos asociados a ese proyecto</h2>", unsafe_allow_html=True)
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
puntos_especifico_peso_total=0
peso_complemento_especifico_por_proyecto = {}  # Diccionario para almacenar los pesos por página

# Iterar sobre todas las páginas en el diccionario y ejecutar las consultas
for page_name in PAGES_TABLES_2:
    #st.markdown(f"<h3>{page_name}</h3>", unsafe_allow_html=True)
    
    # Ejecutar la consulta para obtener el DataFrame y los puntos
    df, total_puntos = execute_query_for_page(page_name, id_proyecto_seleccionado)
    
    if df is not None and not df.empty:
        # Incrementar el total acumulado de puntos específicos
        total_puntos_especificos += total_puntos

        # Crear las columnas (50%, 25%, 25%)
        col1, col2, col3,col4 = st.columns([6, 3, 1,1])

        # Contenido en la primera columna (50%)
        with col1:
            st.markdown(f"<div class='header-cell'><h3>{page_name}</h3></div>", unsafe_allow_html=True)
            
            # Mostrar DataFrame con límite de tamaño
            st.markdown(f"<div class='cell dataframe-cell'>{df.to_html(index=False)}</div>", unsafe_allow_html=True)
            
            # Mostrar el total de puntos de la página
            st.markdown(f"<div class='cell'><b>Total de puntos: {total_puntos}</b></div>", unsafe_allow_html=True)

        # Contenido en la segunda columna (25%)
        with col2:
            st.markdown(f"<div class='header-cell'><b>Peso del complemento específico</b></div>", unsafe_allow_html=True)
            
            # Input para el peso del destino por proyecto
            peso_complemento_especifico_por_proyecto[page_name] = st.number_input(
                f'Peso del complemento específico para {page_name}', 
                min_value=0.0,
                key=f'{page_name}_peso'
            )

        # Contenido en la tercera columna (25%)
        with col3:
            # Calcular puntos con el peso específico
            puntos_especifico_peso = total_puntos * peso_complemento_especifico_por_proyecto[page_name] / 100
            
            st.markdown(f"<div class='header-cell'><b>Total puntos con peso</b></div>", unsafe_allow_html=True)
            
            # Mostrar puntos con peso
            st.markdown(f"<div class='cell'>{puntos_especifico_peso}</div>", unsafe_allow_html=True)

            # Actualizar el total acumulado de puntos destino peso
            puntos_especifico_peso_total += puntos_especifico_peso

        

        with col4:
         # Diccionario para almacenar las notas específicas
            nota_especifico = {}
            st.markdown(f"<div class='header-cell'><b>Notas</b></div>", unsafe_allow_html=True)
    
    # Input de texto para la nota específica por proyecto
            nota_especifico[page_name] = st.text_input(
                f'Nota específica para {page_name}',
                key=f'{page_name}_nota'
            )

    else:
        # No mostramos nada o mostramos un mensaje específico si la tabla no tiene datos
        st.write(f"No se encontraron datos para '{page_name}' en la consulta.")

st.markdown(f"<div class='cell'><b>Suma de % de Peso Específico(Ha de ser Igual a 100%: {peso_complemento_especifico_por_proyecto}</b></div>", unsafe_allow_html=True)
st.markdown(f"<div class='cell'><b>Suma de Puntos x el peso específico->VALORACIÓN: {puntos_especifico_peso_total}</b></div>", unsafe_allow_html=True)

#CAluculo de Sueldo
#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤

st.markdown("<h2>Caluculo de Importes para la Valoración del Puesto de trabajo</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)




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
id_proyecto = st.text_input("Ingrese el ID del proyecto:",value=id_proyecto_seleccionado)

if id_proyecto:
    with st.spinner('Ejecutando consultas...'):
        result_df_general = get_combined_table(id_proyecto, PAGES_TABLES, "ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto")
        result_df_especifico = get_combined_table(id_proyecto, PAGES_TABLES_2, "ate-rrhh-2024.Ate_kaibot_2024.complementos_especificos_por_proyecto")
    
    if not result_df_general.empty:
        st.success("Consulta complemento destino exitosa!")
        #st.dataframe(result_df_general)
        total_destino = result_df_general['puntos'].sum()
        #st.write(f"Total puntos (Destino): {total_destino}")
        #st.write(f"Total puntos (Destino) con peso especifico: {puntos_destino_peso_total}")
        
    else:
        st.warning("No se encontraron datos para el ID de proyecto proporcionado en la consulta general.")
    
    if not result_df_especifico.empty:
        st.success("Consulta de complemento específico exitosa!")
        #st.dataframe(result_df_especifico)
        total_especifico = result_df_especifico['puntos'].sum()
        #st.write(f"Total puntos (Específico): {total_especifico}")
        #st.write(f"Total puntos (Específico) con peso especifico: {puntos_especifico_peso_total}")

        total_puntos=total_especifico+total_destino
        st.write(f"Total puntos Factores  de Compelmentos Especifico + Destino: {total_especifico}+{total_destino} = {total_puntos}")
        
    else:
        st.warning("No se encontraron datos para el ID de proyecto proporcionado en la consulta de complemento específico.")



#≤≤≤≤≤≤≤≤≤SELECCION PUESTOS CALCULO
# Encabezado y línea separadora
st.markdown("<h2>Puestos asociados a ese proyecto; Selecciona para Valoracion</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Consulta SQL para obtener los puestos del proyecto
query_puestos_proyecto = f"""
        SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        WHERE id_puesto IN (
        SELECT id_puesto FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto`
        WHERE id_proyecto = {id_proyecto_seleccionado})
    """

query_job_puestos_proyecto = client.query(query_puestos_proyecto)
results_puestos_proyecto = query_job_puestos_proyecto.result()
df_puestos_proyecto = pd.DataFrame(data=[row.values() for row in results_puestos_proyecto], columns=[field.name for field in results_puestos_proyecto.schema])

# Consulta para obtener las categorías de sueldo
query_categorias_sueldo = """
    SELECT nombre_categoria, sueldo
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_categoria_sueldo_por_ano`
"""

# Ejecutar la consulta para obtener las categorías de sueldo
query_job_categorias_sueldo = client.query(query_categorias_sueldo)
results_categorias_sueldo = query_job_categorias_sueldo.result()
df_categorias_sueldo = pd.DataFrame(data=[row.values() for row in results_categorias_sueldo], columns=[field.name for field in results_categorias_sueldo.schema])

# Convertir el DataFrame de categorías de sueldo en un diccionario para fácil acceso
categorias_sueldo_dict = df_categorias_sueldo.set_index('nombre_categoria')['sueldo'].to_dict()

# Mostrar el dataframe de puestos del proyecto
st.dataframe(df_puestos_proyecto)

# Lista para almacenar los IDs de los puestos seleccionados y los sueldos
selected_puestos_ids = []
sueldo_categoria_puesto = {}

# Generar los checkboxes y selectboxes para cada puesto
for index, row in df_puestos_proyecto.iterrows():
    puesto_id = row['id_puesto']
    puesto_nombre = row['descripcion']
    if st.checkbox(f"{puesto_nombre} (ID: {puesto_id})",value=True):
        selected_puestos_ids.append(puesto_id)
        
        # Selectbox para elegir la categoría de sueldo
        st.markdown("<h2>Selecciona la Categoría para el Puesto</h2>", unsafe_allow_html=True)
        st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
        categoria_seleccionada = st.selectbox(
            f"Seleccione la categoría de sueldo para {puesto_nombre}",
            list(categorias_sueldo_dict.keys()),
            key=f"{puesto_id}_categoria"
        )
        
        # Obtener el sueldo de la categoría seleccionada
        sueldo = categorias_sueldo_dict[categoria_seleccionada]
        st.write(f"Sueldo: {sueldo}")
        
        # Almacenar el sueldo en la variable
        sueldo_categoria_puesto[puesto_id] = sueldo

# Mostrar los IDs de los puestos seleccionados y sus sueldos correspondientes
st.write("Puestos seleccionados:", selected_puestos_ids)
st.write("Sueldos por categoría de puesto:", sueldo_categoria_puesto)

#>>>>>>>>>Valor por punto especifico por poryecto

# Mensaje markdown para explicar la regla de tres
st.markdown("<h2>Valoración para regla de 3 para tabla de complemento específico por Año (Variable) son 100 puntos -> 34.388,95 euros</h2>", unsafe_allow_html=True)
puntos_base = 100
#valor_base = 33714.66  # euros habria que recogerlo de la tabla Desactualizado
valor_base = 34388.95  # euros habria que recogerlo de la tabla

valor_punto_especifico_proyecto = (total_especifico * valor_base) / 100

# Input para que el usuario introduzca el valor de puntos
valor_punto_especifico_proyecto = st.number_input('Introduce el número de puntos específicos del proyecto:',
                                                  min_value=1.0,
                                                  value=valor_punto_especifico_proyecto,
                                                  step=0.01)

#ºel valor por peso especifico por poryecto va variar dependiendo del ayntamiento del año y de la legislacion por lo que tendremos que tener una tabla
#puntos por peso especifico por año
#st.markdown("<h2>Calculo puntos de complemento especifico</h2>", unsafe_allow_html=True)
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
# Definimos los valores conocidos
#puntos_base = 100
#valor_base = 33714.66  # euros
#st.write(f"Total puntos (Específico): {total_especifico}")
#st.write(f"Total puntos (Destino) con peso especifico: {puntos_destino_peso_total}")


# Calculamos el total específico (suponiendo que lo obtienes de alguna manera)
#total_especifico = 500  # Este valor debería ser el total real de puntos específicos del proyecto
# Calculamos el valor de puntos específicos del proyecto
valor_punto_especifico_proyecto = (total_especifico * valor_base) / 100
#st.write(f'El valor específico del puesto con el total de puntos es: {valor_punto_especifico_proyecto:.2f} euros')
puntos_específico_sueldo = (puntos_especifico_peso_total * valor_base) / 100
#st.write(f'El valor específico del puesto con la asignacion de peso es: {puntos_específico_sueldo:.2f} euros')




# Aseguramos que valor_punto_especifico_proyecto no sea menor que min_value
#valor_punto_especifico_proyecto = max(valor_punto_especifico_proyecto, 1.0)









#Valoracion de destino por año 
puntos_destino_peso_total=round(puntos_destino_peso_total)
# Construir la consulta SQL
query_valoracion_puntos = f"""
    SELECT complemento_destino_anual
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_destino_puntos_por_ano`
    WHERE puntos_valoracion_destino = {puntos_destino_peso_total}
    LIMIT 1
"""

# Ejecutar la consulta
query_job = client.query(query_valoracion_puntos)
results = query_job.result()

# Procesar los resultados
puntos_valoracion = None
for row in results:
    puntos_valoracion = row.complemento_destino_anual

# Mostrar el resultado en Streamlit
#st.title("Consulta de Puntos de Valoración de destino con el peso asignado")
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

#if puntos_valoracion:
    #st.dataframe(result_df_general)
    #st.write(f"Total puntos (Destino): {total_destino}")
    #st.write(f"Total puntos (Destino) con peso especifico: {puntos_destino_peso_total}")
    #st.write(f"Puntos de valoración de destino con el porcentaje de importancia: {puntos_valoracion:.2f} euros")
#else:
    #st.write("No se encontraron puntos de valoración para el valor introducido.")

# Mostramos el valor específico del puesto
#st.title("Consulta de Complemento especifico")
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
#st.dataframe(result_df_especifico)       
#st.write(f"Total puntos (Específico): {total_especifico}")
#st.write(f'El valor específico del puesto para el complemento específico sin el peso es: {valor_punto_especifico_proyecto:.2f} euros')
#st.write(f'El valor específico del puesto para el complemento específico con el calculo con puntos es: {puntos_específico_sueldo:.2f} euros')


# Mostrar el resultado en Streamlit
#st.title("Consulta de Sueldo base por categoría")
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

#if sueldo:
 #   st.write(f"Sueldo base por categoría para el puesto de trabajo: {sueldo}")
#else:
      #st.write("No se encontraron puntos de valoración para el valor introducido.")


# Mostrar el resultado en Streamlit
#st.title("Total calculo de Sueldo : Complemento de destino + complemento específico + sueldo base por categoría")
sueldo_total=sueldo+valor_punto_especifico_proyecto+puntos_valoracion
#st.write(f"Sueldo total: {sueldo}+{valor_punto_especifico_proyecto}+{puntos_valoracion} = {sueldo_total} euros")

#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
#creacion de tabalas un poco más roganizadas

# Título para la consulta de puntos
st.title("Consulta de Puntos de Valoración de destino con el peso asignado")
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Mostrar información si hay puntos de valoración
if puntos_valoracion:
    col1, col2, col3,col4 = st.columns([6, 3, 3,3])  # Proporciones 60%, 30%, 10%

    # Columna 1: Mostrar el DataFrame
    with col1:
        st.markdown(f"<div class='header-cell'>Datos de Puntos de Valoración</div>", unsafe_allow_html=True)
        st.dataframe(result_df_general)

    # Columna 2: Mostrar totales de puntos
    with col2:
        st.markdown(f"<div class='header-cell'>Pesos Totales</div>", unsafe_allow_html=True)
        st.write(f"Total puntos (Destino): {total_destino}")
        st.write(f"Total puntos (Destino) con peso específico: {puntos_destino_peso_total}")
        
    # Columna 3: Mostrar otros cálculos
    with col3:
        st.markdown(f"<div class='header-cell'>Valoración</div>", unsafe_allow_html=True)
        # Aquí puedes añadir más cálculos o cualquier otro dato que quieras mostrar.
        st.write(f"Puntos de valoración (Peso x Puntos%): {puntos_destino_peso_total}")

    with col4:
        st.markdown(f"<div class='header-cell'>Importes</div>", unsafe_allow_html=True)
        # Aquí puedes añadir más cálculos o cualquier otro dato que quieras mostrar.
        st.write(f"Importe de Complemento de Destino: {puntos_valoracion:.2f} euros")


else:
    st.write("No se encontraron puntos de valoración para el valor introducido.")

# Título para la consulta del complemento específico
st.title("Consulta de Complemento específico")
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Mostrar información relacionada con el complemento específico
col1, col2, col3,col4 = st.columns([6, 3, 3,3])  # Proporciones 60%, 30%, 10%

# Columna 1: Mostrar el DataFrame del complemento específico
with col1:
    st.markdown(f"<div class='header-cell'>Datos de Complemento Específico</div>", unsafe_allow_html=True)
    st.dataframe(result_df_especifico)

# Columna 2: Mostrar totales de puntos específicos
with col2:
    st.markdown(f"<div class='header-cell'>Pesos Totales</div>", unsafe_allow_html=True)
    st.write(f"Total puntos (Específico): {total_especifico}")
    

# Columna 3: Mostrar valor específico del puesto
with col3:
    st.markdown(f"<div class='header-cell'>Valoración</div>", unsafe_allow_html=True)
    st.write(f"Puntos de valoración (Peso x Puntos%): {puntos_especifico_peso_total}")
    #st.write(f"El valor específico del puesto con el cálculo en puntos es: {puntos_específico_sueldo:.2f} euros")

with col4:
    st.markdown(f"<div class='header-cell'>Importes</div>", unsafe_allow_html=True)
    st.write(f"El valor específico del puesto para el complemento específico es: {valor_punto_especifico_proyecto:.2f} euros")
    st.write(f"El valor específico del puesto con el cálculo en puntos es: {puntos_específico_sueldo:.2f} euros")

# Título para la consulta de sueldo base por categoría
#st.title("Consulta de Sueldo base por categoría")
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Mostrar sueldo base si existe
#if sueldo:
 #   st.write(f"Sueldo base por categoría para el puesto de trabajo: {sueldo}")
#else:
 #   st.write("No se encontraron puntos de valoración para el valor introducido.")

#vamos a organizar los datos como en las tablas
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
#st.markdown(f"<h2>Calculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
#st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Título para el cálculo final del sueldo total
st.markdown(f"<div class='header-cell'>Valoración preliminar Sueldo Total Final</div>", unsafe_allow_html=True)
st.title("Total calculo de Sueldo: sueldo base por categoría y por puesto +Complemento específico + complemento de destino")
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)


# Iterar sobre los puestos seleccionados y calcular el sueldo total para cada uno
for puesto_id in selected_puestos_ids:
    puesto_nombre = df_puestos_proyecto.loc[df_puestos_proyecto['id_puesto'] == puesto_id, 'descripcion'].values[0]
    sueldo = sueldo_categoria_puesto[puesto_id]
    
    # Suponiendo que `puntos_específico_sueldo` y `puntos_valoracion` están definidos y son valores fijos.
    sueldo_total_puesto = sueldo + puntos_específico_sueldo + puntos_valoracion
    
    # Mostrar el cálculo para cada puesto
    #st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.markdown(f"<h2>Calculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
    st.write(f"Bruto Anual con Jornada Ordinaria : {sueldo} + {puntos_específico_sueldo} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")

#Añadimos los calculos de Jornada
# Título para el cálculo final del sueldo total
st.markdown(f"<div class='header-cell'>Valoración preliminar Sueldo Total Final</div>", unsafe_allow_html=True)
st.title("Total cálculo de Sueldo: sueldo base por categoría y por puesto + Complemento específico + complemento de destino")
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Selección de la modalidad de disponibilidad especial
modalidad_disponibilidad = st.selectbox(
    'Selecciona la modalidad de disponibilidad especial:',
    options=[
        'Ninguna',
        'Jornada ampliada (hasta 10%)',
        'Disponibilidad absoluta (hasta 15%)',
        'Jornada ampliada con disponibilidad absoluta (hasta 20%)'
    ]
)

# Inicialización del porcentaje según la modalidad seleccionada
porcentaje_disponibilidad = 0.0
if modalidad_disponibilidad == 'Jornada ampliada (hasta 10%)':
    porcentaje_disponibilidad = 10.0
elif modalidad_disponibilidad == 'Disponibilidad absoluta (hasta 15%)':
    porcentaje_disponibilidad = 15.0
elif modalidad_disponibilidad == 'Jornada ampliada con disponibilidad absoluta (hasta 20%)':
    porcentaje_disponibilidad = 20.0

# Iterar sobre los puestos seleccionados y calcular el sueldo total para cada uno
for puesto_id in selected_puestos_ids:
    puesto_nombre = df_puestos_proyecto.loc[df_puestos_proyecto['id_puesto'] == puesto_id, 'descripcion'].values[0]
    sueldo = sueldo_categoria_puesto[puesto_id]
    
    # Suponiendo que `puntos_específico_sueldo` y `puntos_valoracion` están definidos y son valores fijos.
    sueldo_total_puesto = sueldo + puntos_específico_sueldo + puntos_valoracion
    
    # Mostrar el cálculo para cada puesto
    st.markdown(f"<h2>Cálculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
    st.write(f"Bruto Anual con Jornada Ordinaria: {sueldo} + {puntos_específico_sueldo} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")

    # Calcular el complemento específico tramo dedicación especial
    sueldo_bruto_con_complementos = sueldo + puntos_específico_sueldo + puntos_valoracion
    if porcentaje_disponibilidad > 0:
        incremento_disponibilidad = sueldo_bruto_con_complementos * (porcentaje_disponibilidad / 100)
        sueldo_total_con_disponibilidad = sueldo_total_puesto + incremento_disponibilidad
        st.write(f"Con la modalidad '{modalidad_disponibilidad}' ({porcentaje_disponibilidad}%), el sueldo total ajustado es: {sueldo_total_con_disponibilidad:.2f} euros")
    else:
        st.write("No se ha aplicado ningún complemento de disponibilidad especial.")

# Mostrar la referencia a la última publicación oficial
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.markdown("Última publicación oficial: BOPV del 27 de febrero del 2024")



# Formulario de envío
with st.form('addition'):
    submit = st.form_submit_button('Confirmar Valoración preliminar')

if submit:
    try:
        # Consulta para obtener el último ID de proyecto
        query_max_id = """
        SELECT MAX(Id_valoracion_preliminar) FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_preliminar_por_proyecto`
        """
        query_job_max_id = client.query(query_max_id)
        max_id_result = query_job_max_id.result()

        max_id = 0
        for row in max_id_result:
            max_id = row[0]

        # Incrementar el máximo ID en 1 para obtener el nuevo ID de proyecto
        new_id_valoracion_preliminar = max_id + 1 if max_id is not None else 1

        # Consulta para insertar datos básicos en BigQuery
        query_kai_insert = f"""
            INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.valoracion_preliminar_por_proyecto`
            (Id_valoracion_preliminar, id_proyecto, id_puesto, nombre_puesto, puntos_destino, puntos_especifico, sueldo_base_puesto, importe_destino,importe_especifico,bruto_anual_puesto) 
            VALUES 
            ({new_id_valoracion_preliminar},{id_proyecto_seleccionado}, {puesto_id}, '{puesto_nombre}', {puntos_destino_peso_total}, {puntos_especifico_peso_total}, {sueldo},{puntos_valoracion},{puntos_específico_sueldo},{sueldo_total_puesto})
        """
        query_job_kai_insert = client.query(query_kai_insert)
        query_job_kai_insert.result()  # Asegurarse de que la consulta se complete
        # Mensaje de éxito
        st.success("Registro insertado correctamente")

        
    except Exception as e:
        st.error(f"Error al insertar el registro: {e}")
