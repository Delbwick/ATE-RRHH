import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid


# Configurar la página de Streamlit
st.set_page_config(page_title="ATE-Alta nuevos proyectos", page_icon="🆕")
st.title("¡Bienvenido a ATE! 👷")
st.header("¡Empieza tu Proyecto!")

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
st.write("# Alta nuevo Proyecto")

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
st.title('Nuevo Proyecto:')
st.markdown("<h2>Datos de Proyecto</h2>", unsafe_allow_html=True)
    # Línea horizontal ancha
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
  
col1, col2, col3, col4 = st.columns(4)

with col1:
    nombre = st.text_input('Nombre de Proyecto')
with col2:
    descripcion = st.text_input('Descripción')
with col3:
    fecha_inicio = st.date_input('Fecha de Inicio')
with col4:
    fecha_fin = st.date_input('Fecha de Fin')

# Filas para otros campos del proyecto
col1, col2, col3, col4 = st.columns(4)
with col1:
    proyecto_activo = st.checkbox('Proyecto Activo')
with col2:
    id_ads = st.text_input('Cliente')
with col3:
    id_tag = st.date_input('Creado en')
with col4:
    id_propiedad = st.date_input('Actualizado en')

# Filas para datos adicionales
col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox('Sector', ['Ayuntamiento', 'Gobierno','Administración local',
'Ayuntamiento de primera categoría',
'Ayuntamiento de segunda categoría',
'Ayuntamiento de tercera categoría',
'Consorcio',
'Mancomunidad',
'Cuadrilla',
'Entidad autónoma local',
'Empresa pública',
'Sociedad pública local',
'Sociedad pública autonómica',
'Sociedad pública estatal',
'Agencia',
'Departamento'])
with col2:
    tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])

# Filas para datos de alta
col1, col2 = st.columns(2)
with col1:
    fecha_alta = st.date_input('Fecha de Alta')
with col2:
    pago = st.text_input('Forma de Pago')


# Función para obtener puestos desde BigQuery
def get_puestos():
    query = """
        SELECT *
        FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
    """
    query_job = client.query(query)
    results = query_job.result()
    puestos = [row.descripcion for row in results]
    return puestos

# Mostrar el selectbox de puestos
st.markdown("<h2>Datos de Factores</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
selected_puesto = st.selectbox("Selecciona un puesto", get_puestos())
#mostrar los puestos como checkbox
# Obtener los puestos
puestos = get_puestos()

# Mostrar los puestos como checkboxes
st.write("Selecciona los puestos:")
selected_puestos = []
for descripcion in puestos:
    if st.checkbox(descripcion):
        selected_puestos.append((descripcion))

# Mostrar los puestos seleccionados
if selected_puestos:
    st.write("Puestos seleccionados:")
    for descripcion in selected_puestos:
        st.write(f"{descripcion}")
else:
    st.warning("Por favor, selecciona al menos un puesto para continuar.")



#Finde Primeros campos de proyectos
#para las selecciones de los factores que ya estan seleccionadops
def obtener_datos_bigquery(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"  # Ajusta el límite según sea necesario
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df



st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento de destino:")
# Diccionario de tablas de factores de compelemto destino
PAGES_TABLES = {
    "Formación": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Autonomía-Complejidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica destino": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    #"Complemento de Destino": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_de_destino", "id_complemento_destino"),
    #"Complemento Específico por Año": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_específico_xaño", "id_complemento_especifico"),
    #"Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    #"Conocimientos específicos al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_especificos", "id_conocimientos_especificos"),
    #"Definitivo?¿ ": ("ate-rrhh-2024.Ate_kaibot_2024.definitivo", "id_definitivo"),
    #"Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    #"Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    #"Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "Especialización destino /ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA/": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    #"Idioma del Proyecto": ("ate-rrhh-2024.Ate_kaibot_2024.idioma_proyecto", "id_idioma_proyecto"),
    #"Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    #"Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "id_idioma_euskera"),
    #"Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    #"Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    #"Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad_turno"),
    #"Porcentajes Variables": ("ate-rrhh-2024.Ate_kaibot_2024.porcentajes_variables", "id_porcentajes_variables"),
    #"Proyectos": ("ate-rrhh-2024.Ate_kaibot_2024.proyecto", "id_proyecto"),
    #"Puestos": ("ate-rrhh-2024.Ate_kaibot_2024.puestos", "id_puesto"),
    "Responsabilidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
    #"Salario Base por Categoría y Año": ("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño", "id_salario_base"),
    #"Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno")
    # Agregar el resto de las tablas aquí
}
# Mostrar checkboxes para seleccionar las tablas de factores de compleemnto de destino
selected_factores = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES.items():
    if st.checkbox(nombre_tabla):
        selected_factores.append((nombre_completo, id_tabla))
        
# Mostrar selectboxes para seleccionar una fila por tabla
selected_factores = {}
for nombre_tabla, filas in PAGES_TABLES.items():
    opciones = [fila[0] for fila in filas]
    selected_opcion = st.selectbox(f"Seleccione una opción de {nombre_tabla}", ["Ninguno"] + opciones)
    
    if selected_opcion != "Ninguno":
        # Encontrar la fila seleccionada
        selected_fila = next(fila for fila in filas if fila[0] == selected_opcion)
        selected_factores[nombre_tabla] = selected_fila



# Mostrar los datos seleccionados
if selected_factores:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.write("Selecciona los valores específicos de las tablas seleccionadas:")

    valores_seleccionados = {}
    for nombre_completo, id_tabla in selected_factores:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(nombre_completo)
        if not df.empty:
            valores_seleccionados[id_tabla] = []
            for index, row in df.iterrows():
                # Crear la etiqueta del checkbox usando descripcion y letra
                etiqueta_checkbox = f"{row['descripcion']} ({row['letra']})"
                if st.checkbox(etiqueta_checkbox, key=f"{id_tabla}_{index}"):
                    valores_seleccionados[id_tabla].append(row[id_tabla])

    st.write("Valores seleccionados:")
    st.write(valores_seleccionados)



        
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
    "Especialización": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
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
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno")
    # Agregar el resto de las tablas aquí
}


# Mostrar checkboxes para seleccionar las tablas de factores de complemento de destino
selected_factores_2 = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES_2.items():
    if st.checkbox(nombre_tabla):
        selected_factores_2.append((nombre_completo, id_tabla))

# Mostrar los datos seleccionados
if selected_factores_2:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.write("Selecciona los valores específicos de las tablas seleccionadas:")

    valores_seleccionados_2 = {}
    for nombre_completo, id_tabla in selected_factores_2:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(nombre_completo)
        if not df.empty:
            valores_seleccionados_2[id_tabla] = []
            for index, row in df.iterrows():
                # Crear la etiqueta del checkbox usando descripcion y letra
                etiqueta_checkbox = f"{row['descripcion']} ({row['letra']})"
                if st.checkbox(etiqueta_checkbox, key=f"{id_tabla}_{index}"):
                    valores_seleccionados_2[id_tabla].append(row[id_tabla])

    st.write("Valores seleccionados:")
    st.write(valores_seleccionados_2)





#CONSULTA DE INSERCION de proyecto

# Formulario de envío
with st.form('addition'):
    submit = st.form_submit_button('Alta nuevo cliente')

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

        # Consulta para insertar datos básicos en BigQuery
        query_kai_insert = f"""
            INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.proyecto` 
            (id_projecto, nombre, descripcion, fecha_comienzo, fecha_fin, proyecto_activo_2) 
            VALUES 
            ({new_id_proyecto}, '{nombre}', '{descripcion}', '{fecha_inicio}', '{fecha_fin}', '{proyecto_activo}')
        """
        query_job_kai_insert = client.query(query_kai_insert)
        query_job_kai_insert.result()  # Asegurarse de que la consulta se complete

        # Insertar datos seleccionados de las tablas de factores
        for nombre_completo, id_tabla in selected_factores:
            query_factores_insert = f"""
                INSERT INTO `{nombre_completo}` 
                (id_tabla, letra, descripcion, porcentaje_de_total, puntos) 
                VALUES 
                ({new_id_proyecto}, '{letra}', '{descripcion}', {porcentaje_de_total}, {puntos})
            """
            query_job_factores_insert = client.query(query_factores_insert)
            query_job_factores_insert.result()  # Asegurarse de que la consulta se complete

        st.success('Registro añadido correctamente')
    except Exception as e:
        st.error(f"Error al insertar el registro: {e}")

# Insertar los valores seleccionados en BigQuery
# Generar un nuevo ID de proyecto
new_id_proyecto = st.number_input('Nuevo ID de Proyecto', min_value=1, step=1)


# Insertar los valores seleccionados en BigQuery
if st.button('Insertar en BigQuery'):
    rows_to_insert_1 = []
    rows_to_insert_2 = []
    rows_to_insert_puestos = []

    # Procesar valores seleccionados para la primera tabla
    for id_tabla, valores in valores_seleccionados.items():
        for valor in valores:
            row = {id_tabla: valor, 'id_proyecto': new_id_proyecto}
            rows_to_insert_1.append(row)

    # Procesar valores seleccionados para la segunda tabla
    for id_tabla, valores in valores_seleccionados_2.items():
        for valor in valores:
            row = {id_tabla: valor, 'id_proyecto': new_id_proyecto}
            rows_to_insert_2.append(row)

    # Procesar puestos seleccionados
    for descripcion in selected_puestos:
        # Obtener el id_puesto basado en la descripción del puesto
        query = f"""
            SELECT id_puesto
            FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
            WHERE descripcion = '{descripcion}'
        """
        query_job = client.query(query)
        results = query_job.result()
        id_puesto = None
        for row in results:
            id_puesto = row.id_puesto
            break

        if id_puesto is not None:
            row = {
                'id_proyecto': new_id_proyecto,
                'id_puesto': id_puesto
            }
            rows_to_insert_puestos.append(row)

    # Insertar en la primera tabla
    if rows_to_insert_1:
        table_id_1 = "ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto"
        errors_1 = client.insert_rows_json(table_id_1, rows_to_insert_1)
        if errors_1 == []:
            st.success('Datos insertados exitosamente en complementos_de_destino_por_proyecto')
        else:
            st.error(f'Error al insertar datos en complementos_de_destino_por_proyecto: {errors_1}')

    # Insertar en la segunda tabla
    if rows_to_insert_2:
        table_id_2 = "ate-rrhh-2024.Ate_kaibot_2024.complementos_especificos_por_proyecto"
        errors_2 = client.insert_rows_json(table_id_2, rows_to_insert_2)
        if errors_2 == []:
            st.success('Datos insertados exitosamente en complementos_especificos_por_proyecto')
        else:
            st.error(f'Error al insertar datos en complementos_especificos_por_proyecto: {errors_2}')

    # Insertar en la tabla de puestos seleccionados por proyectos
    if rows_to_insert_puestos:
        table_id_puestos = "ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto"
        errors_puestos = client.insert_rows_json(table_id_puestos, rows_to_insert_puestos)
        if errors_puestos == []:
            st.success('Datos insertados exitosamente en puestos_seleccionados_por_proyecto')
        else:
            st.error(f'Error al insertar datos en puestos_seleccionados_por_proyecto: {errors_puestos}')


# Función para abrir otra aplicación
#def abrir_otra_app():
    #url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    #webbrowser.open_new_tab(url_otra_app)

# Función para obtener datos de BigQuery
# Función para obtener datos de BigQuery
def obtener_datos_por_proyecto(id_proyecto):
    query = f"""
    SELECT 
        ps.id_puesto,
        cd.id_formacion_general,
        cd.id_capacidades_necesarias,
        cd.id_complejidad,
        cd.id_complejidad_tecnica,
        cd.id_complejidad_territorial,
        cd.id_conocimientos_basicos,
        cd.id_especializacion,
        cd.id_iniciativa,
        cd.id_mando,
        cd.id_formacion,
        cd.id_responsabilidad_actividad,
        cd.id_responsabilidad,
        
    FROM 
        `ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto` ps
    LEFT JOIN 
        `ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto` cd
    ON 
        ps.id_proyecto = cd.id_proyecto
    LEFT JOIN 
        `ate-rrhh-2024.Ate_kaibot_2024.complementos_especificos_por_proyecto` ce
    ON 
        ps.id_proyecto = ce.id_proyecto
    WHERE 
        ps.id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

# Formulario de entrada
st.title('Ver Datos del Proyecto')
id_proyecto = st.number_input('ID de Proyecto', min_value=1, step=1)
if st.button('Mostrar Datos'):
    df = obtener_datos_por_proyecto(id_proyecto)
    if not df.empty:
        st.write('IDs Relacionados del Proyecto:')
        st.dataframe(df)
    else:
        st.warning('No se encontraron datos para este ID de proyecto.')
