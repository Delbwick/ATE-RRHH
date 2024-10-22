# streamlit_app.py
import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Creamos la cabecera
st.set_page_config(page_title="ATE-Alta nuevos proyectos", page_icon="🆕")
st.title("¡Bienvenido a ATE! 👷")
st.header("¡Empieza tu Proyecto!")

# Definir el color de fondo del encabezado
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
    </style>
"""

# Agregar el HTML personalizado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
st.write("# Alta nuevo cliente")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Consulta para extraer datos de BigQuery de la tabla de clientes
query_clientes = """
   SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
"""

# Ejecutar la consulta y obtener resultados
try:
    query_job_clientes = client.query(query_clientes)
    results_clientes = query_job_clientes.result()
    df_clientes = pd.DataFrame(data=[row.values() for row in results_clientes], columns=[field.name for field in results_clientes.schema])
    #st.dataframe(df_clientes)
except Exception as e:
    st.error(f"Error al ejecutar la consulta: {e}")

# Creamos formulario de alta de clientes
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

# Filas de columnas para otros campos
col1, col2, col3, col4 = st.columns(4)
with col1:
    proyecto_activo = st.checkbox('Proyecto Activo')
with col2:
    id_ads = st.text_input('Identificador Google Ads XXX-XXX-XXXX, introducir sin guiones 1234567890')
with col3:
    id_tag = st.text_input('Identificador Tag Manager')
with col4:
    id_propiedad = st.text_input('Propiedad GA4')

# Fila de datos de empresa
col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox('Sector', ['Ecommerce', 'B2B'])
with col2:
    tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])

# Fila de datos de alta
col1, col2 = st.columns(2)
with col1:
    fecha_alta = st.date_input('Fecha de Alta')
with col2:
    pago = st.text_input('Forma de Pago')

with st.form('addition'):
    submit = st.form_submit_button('Alta nuevo cliente')

if submit:
    try:
        # Consulta para obtener el último ID de cliente
        query_max_id = """
        SELECT MAX(id_proyecto) FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
        """
        query_job_max_id = client.query(query_max_id)
        max_id_result = query_job_max_id.result()

        max_id = 0
        for row in max_id_result:
            max_id = row[0]

        # Incrementar el máximo ID en 1 para obtener el nuevo ID de cliente
        new_id_proyecto = max_id + 1 if max_id is not None else 1

        # Consulta para insertar datos en BigQuery
        query_kai_insert = f"""
        INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.proyecto` (id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin, proyecto_activo) 
        VALUES ({new_id_proyecto}, '{nombre}', '{descripcion}', '{fecha_inicio}', '{fecha_fin}', '{proyecto_activo}')
        """
        query_job_kai_insert = client.query(query_kai_insert)
        query_job_kai_insert.result()  # Asegurarse de que la consulta se complete
        st.success('Record added Successfully')
    except Exception as e:
        st.error(f"Error al insertar el registro: {e}")

def abrir_otra_app():
    url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    webbrowser.open_new_tab(url_otra_app)

#st.title("Ver listado de clientes")

# Botón para abrir la otra aplicación
if st.button("Clientes"):
    abrir_otra_app()

if st.button("Ir a Otra App"):
    st.markdown('[Otra App](https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/)')
