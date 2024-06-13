import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

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
selected_puesto = st.selectbox("Selecciona un puesto", get_puestos())
#mostrar los puestos como checkbox
# Obtener los puestos
puestos = get_puestos()

# Mostrar los puestos como checkboxes
st.write("Selecciona los puestos:")
selected_puestos = []
for descripcion in puestos:
    if st.checkbox(descripcion):
        selected_puestos.append((id_puesto, descripcion))

# Mostrar los puestos seleccionados
if selected_puestos:
    st.write("Puestos seleccionados:")
    for id_puesto, descripcion in selected_puestos:
        st.write(f"{descripcion} (ID: {id_puesto})")
else:
    st.warning("Por favor, selecciona al menos un puesto para continuar.")

st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Diccionario de tablas de factores
PAGES_TABLES = {
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Complejidad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    "Complemento de Destino": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_de_destino", "id_complemento_destino"),
    "Complemento Específico por Año": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_específico_xaño", "id_complemento_especifico"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Conocimientos específicos al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_especificos", "id_conocimientos_especificos"),
    "Definitivo?¿ ": ("ate-rrhh-2024.Ate_kaibot_2024.definitivo", "id_definitivo"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "Especialización": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Idioma del Proyecto": ("ate-rrhh-2024.Ate_kaibot_2024.idioma_proyecto", "id_idioma_proyecto"),
    "Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    "Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_formacion", "id_nivel_formacion"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad_turno"),
    "Porcentajes Variables": ("ate-rrhh-2024.Ate_kaibot_2024.porcentajes_variables", "id_porcentajes_variables"),
    "Proyectos": ("ate-rrhh-2024.Ate_kaibot_2024.proyecto", "id_proyecto"),
    "Puestos": ("ate-rrhh-2024.Ate_kaibot_2024.puestos", "id_puesto"),
    "Responsabilidad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
    "Salario Base por Categoría y Año": ("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño", "id_salario_base"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno")
    # Agregar el resto de las tablas aquí
}

# Mostrar checkboxes para seleccionar las tablas de factores
selected_factores = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES.items():
    if st.checkbox(nombre_tabla):
        selected_factores.append((nombre_completo, id_tabla))

# Crear formulario para datos del proyecto
st.title('Alta Proyectos:')
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
    id_ads = st.text_input('Identificador Google Ads XXX-XXX-XXXX, introducir sin guiones 1234567890')
with col3:
    id_tag = st.text_input('Identificador Tag Manager')
with col4:
    id_propiedad = st.text_input('Propiedad GA4')

# Filas para datos adicionales
col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox('Sector', ['Ecommerce', 'B2B'])
with col2:
    tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])

# Filas para datos de alta
col1, col2 = st.columns(2)
with col1:
    fecha_alta = st.date_input('Fecha de Alta')
with col2:
    pago = st.text_input('Forma de Pago')

# Formulario de envío
with st.form('addition'):
    submit = st.form_submit_button('Alta nuevo cliente')

if submit:
    try:
        # Consulta para obtener el último ID de proyecto
        query_max_id = """
        SELECT MAX(id_proyecto) FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
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
            (id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin, proyecto_activo) 
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

# Función para abrir otra aplicación
def abrir_otra_app():
    url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    webbrowser.open_new_tab(url_otra_app)

st.title("Ver listado de clientes")

# Botón para abrir otra aplicación
if st.button("Clientes"):
    abrir_otra_app()

if st.button("Ir a Otra App"):
    st.markdown('[Otra App](https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/)')
