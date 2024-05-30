# streamlit_app.py
#hay que añadir el secreto toml en los ajustes avanzados de aplicacion dentro de streamlit
#creamos el primer formulario de registros de cliente sobre la tabla demo
#hay que insertar el secreto en la aplicacion dentro de stremalit
import webbrowser #para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
#Creamos la cabecera
st.set_page_config(page_title="ATE-Alta nuevos proyectos", page_icon="🆕")
st.title("🚀 ¡Bienvenido a ATE! 🎉")
st.header("🚀 ¡Empieza tu Proyecto! 🎉")
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
st.markdown('<div class="header-container"><img class="logo" src="https://kaibot.es/wp-content/uploads/2020/07/image1.png" alt="Logo"></div>', unsafe_allow_html=True)
st.write("# Alta nuevo cliente")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)


#otra manera de trabajar las tablas
# Configurar la conexión a BigQuery
#usamos la configuracion anterior

# Consulta para extraer datos de BigQuery de la tabla de clientes
query_clientes = """
   SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.proyectos`
"""

# Ejecutar la consulta
query_job_clientes = client.query(query_clientes)

# Obtener resultados de la consulta
results_clientes = query_job_clientes.result()

# Convertir los resultados en un DataFrame de pandas
df_clientes = pd.DataFrame(data=[row.values() for row in results_clientes], columns=[field.name for field in results_clientes.schema])

# Visualizar el DataFrame
st.dataframe(df_clientes)

#st.dataframe(results_clientes)

# Creamos formulario de alta de clientes
st.title('Alta Proyectos:')
col1, col2, col3,col4 = st.columns(4)  # Tres columnas al 33.33% cada una, si quisieramos otras medidas serian (1,1,2) 25%25%y50%

  
with col1:
    #id_cliente = st.number_input('id_cliente', step=1) step=1 siginifica que el booleano se queda sin decimales
    nombre = st.text_input('Nombre de Proyecto')
with col2:
    descripcion = st.text_input('Descripción')

with col3:
    fecha_inicio = st.date_input('Fecha de Inicio')
with col4:
    fecha_fin = st.date_input('Fecha de Fin')

# Filas de columnas para otros campos
col1, col2, col3,col4 = st.columns(4)
with col1:
    proyecto_activo = st.checkbox('Poryecto Activo')
   

with col2:
   id_ads = st.text_input('Identificador Google Ads XXX-XXX-XXXX, introducir sin guiones 1234567890')

with col3:
   id_tag = st.text_input('Identificador Tag Manager')
with col4:
   id_propiedad = st.text_input('Propiedad GA4')

#fila de datos de empresa
col1,col2=st.columns(2)
with col1:
   sector = st.selectbox('Sector', ['Ecommerce', 'B2B'])
with col2:
   tamano_empresa = st.radio('Selecciona el tamaño:', ['Pequeña', 'Mediana', 'Gran Empresa'])

#fila de datos de alta
col1,col2=st.columns(2)
with col1:
   fecha_alta = st.date_input('Fecha de Alta')
with col2:
   pago = st.text_input('Forma de Pago')

with st.form('addition'):
    submit = st.form_submit_button('Alta nuevo cliente')

if submit:
    # Consulta para obtener el último ID de cliente
      query_max_id = """
      SELECT MAX(id_proyecto) FROM `ate-rrhh-2024.Ate_kaibot_2024.proyectos`
      """
    # Ejecutar la consulta para obtener el último ID de cliente
      query_job_max_id = client.query(query_max_id)
    # Obtener el resultado de la consulta
      max_id_result = query_job_max_id.result()

    # Inicializar el máximo ID como 0 si no hay registros aún
      
      max_id = 0
    # Iterar sobre el resultado para obtener el máximo ID de cliente
      for row in max_id_result:
           max_id = row[0]


    # Incrementar el máximo ID en 1 para obtener el nuevo ID de cliente
      if max_id is not None:
            new_id_proyecto = max_id + 1
      else:
           new_id_proyecto = 1
    # Consulta para insertar datos de BigQuery
      query_kai_insert = f"""
      INSERT INTO ate-rrhh-2024.Ate_kaibot_2024.proyectos (id_proyecto, nombre, descripcion,fecha_inicio,fecha_fin,proyecto_activo) 
      VALUES ({new_id_proyecto}, '{nombre}', '{descripcion}','{fecha_inicio}','{fecha_fin}','{proyecto_activo}')
      """
    # Ejecutar la consulta
      query_job_kai_insert = client.query(query_kai_insert)
    # Comprobamos que va todo bien
      st.success('Record added Successfully')
 
  # if submit:
       
        ## Consulta para insertar datos de BigQuery
        #parece que la F es importante
       # query_kai_insert = f""" 
       # INSERT INTO kaibot-saas-2018.demo.clientes_kai_2024 (id_cliente, nombre_cliente) VALUES ({id_cliente}, '{nombre}','{mail}')
        #"""
        # Ejecutar la consulta
        #query_job_kai_insert = client.query(query_kai_insert)
        #comprobamos que va todo bien
        #st.success('Record added Successfully')
#vamos a poner un boton que vaya a lista de clientes:

def abrir_otra_app(): #necesitamos importa webrowser
    url_otra_app = "https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/"
    webbrowser.open_new_tab(url_otra_app)

st.title("Ver listado de clientes")

# Botón para abrir la otra aplicación
if st.button("Clientes"):
    abrir_otra_app()

#otro metodo
if st.button("Ir a Otra App"):
    st.markdown('[Otra App](https://test-analytics-g7zhphce2svtgaye6sgiso.streamlit.app/)')
