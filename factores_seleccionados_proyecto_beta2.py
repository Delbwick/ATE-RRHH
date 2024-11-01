import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino-Manual preliminar")

# HTML para mostrar el texto de desplazamiento
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
        1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.
    </h3>
    <p style="font-family: Arial, sans-serif; font-size: 14px; color: #555555; text-align: justify;">
       2.	El contenido del salario público.
Cada empleado público (funcionario o personal laboral) puede cobrar una cantidad diferente, como consecuencia de la suma de los diferentes conceptos retributivos: retribuciones básicas -sueldo base, trienios-, y retribuciones complementarias -complemento de destino, complemento específico-. Sin perjuicio de otros complementos -por resultados en la gestión o productividad- o percepción de gratificaciones extraordinarias, en caso de que los hubiera. (art. 122 LEPV).
La valoración sólo determina el complemento de destino y el complemento específico, aunque del estudio de los puestos de trabajo se pueden extraer otras propuestas.
El grupo o categoría en el que se clasifica un determinado puesto de trabajo está vinculado a los requisitos de titulación para el acceso al puesto. Es decir, la titulación de la persona no tiene importancia, sino la exigida para el acceso al puesto.
Atendiendo a la clasificación del puesto le corresponderán unas retribuciones básicas-sueldo y trienios*-. 
Los importes correspondientes a doce mensualidades (para el periodo enero a diciembre de 2024) en concepto de retribuciones básicas, son los que se recogen a continuación :
* Los trienios están regulados por Udalhitz (art. 69). 
Grupo/subgrupo	Sueldo (euros)	Trienios (euros)
A1	15.922,80	612,84
A2	13.768,20	499,80
B	12.035,28	438,48
C1	10.337,52	378,36
C2	8.603,76	257,52
E	7.874,76	193,92


Y para cada una de las pagas extraordinarias de los meses de junio y diciembre (2024), en concepto de sueldo y	trienios, las siguientes cuantías:

Grupo/subgrupo	Sueldo 
(euros)	Trienios 
(euros)
A1	818,82 	31,53
A2	836,78	30,37
B	866,84	31,60
C1	744,56	27,21
C2	710,44	21,24
E	656,23	16,16

La Ley 11/2022, de 1 de diciembre, del Empleo Público Vasco, establece en su artículo 122, en relación con el complemento del puesto de trabajo:
3.	El complemento de destino se fijará anualmente en los Presupuestos Generales de la Comunidad Autónoma del País Vasco y será el correspondiente al puesto de trabajo que se desempeñe, de acuerdo con la estructura de niveles jerárquicos de responsabilidad que cada Administración Pública determine en función de sus facultades organizativas.
Para la asignación del nivel de complemento de destino se tendrán en cuenta:
•	Nivel de titulación exigido
•	Nivel de coordinación requerido por la relación jerárquica o funcional del puesto
•	Responsabilidad, iniciativa y autonomía en la toma de decisiones y en la adopción de medidas
•	Grado de complejidad de la información a procesar para el correcto desarrollo de las tareas propias del	puesto	de trabajo



4.	El mismo artículo de la ley recoge que, el complemento específico, que salvo norma o pacto en contrario será único por cada puesto de trabajo que tenga asignado, retribuye las condiciones especiales de cada puesto de trabajo:
•	Dificultad técnica especial.
•	Responsabilidad.
•	Dedicación.
•	Penosidad o peligrosidad.
•	Y cualquier otra condición que se produzca en el puesto de trabajo.
Podrá fijarse una cuantía por el factor de incompatibilidad cuando para el desempeño de determinados puestos se requiera una dedicación absoluta al servicio público.
En ningún caso podrá percibirse el complemento específico como retribución consolidada, quedando condicionado el desempeño efectivo del puesto en las condiciones valoradas.
Las Administraciones Públicas Vascas podrán asignar, en su caso, un complemento específico a todos los puestos de trabajo de su organización. 
Las cuantías del complemento de destino se fijarán en la norma presupuestaria de cada Administración pública vasca, de acuerdo con los criterios que reglamentariamente establezca el órgano correspondiente para su determinación.

    </p>
</div>
"""
st.markdown(scrollable_text_html, unsafe_allow_html=True)

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener tablas que contienen la columna 'tipo_factor'
# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Obtener todas las tablas y verificar si contienen tipo_factor
def get_tablas_con_tipo_factor():
    dataset_id = "YOUR_DATASET"  # Reemplaza con tu dataset en BigQuery
    project_id = "YOUR_PROJECT"  # Reemplaza con tu proyecto en BigQuery
    
    # Consulta para obtener todas las tablas del dataset
    tables_query = f"""
        SELECT table_name
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    """
    tables = client.query(tables_query).result()
    
    tablas_con_tipo_factor = []
    for table in tables:
        table_name = table.table_name
        # Consulta para verificar si `tipo_factor` está presente como clave en la tabla
        query = f"""
            SELECT COUNT(1) AS has_tipo_factor
            FROM `{project_id}.{dataset_id}.{table_name}`
            WHERE 'tipo_factor' IN UNNEST(REGEXP_EXTRACT_ALL(TO_JSON_STRING(t), r'"([a-zA-Z0-9_]+)"'))
        """
        result = client.query(query).result()
        if result and next(result).has_tipo_factor > 0:
            tablas_con_tipo_factor.append(table_name)
    
    return tablas_con_tipo_factor


# Función para obtener complementos específicos
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_especifico for row in results]

# Función para obtener complementos de destino
def get_complementos_destino(id_proyecto):
    query = f"""
        SELECT complemento_destino
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_destino for row in results]

# Función para obtener datos de la tabla específica
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Función para crear una nueva tabla en BigQuery desde Streamlit
def crear_tabla_nueva():
    st.sidebar.subheader("Crear una nueva tabla de factores")
    table_name = st.sidebar.text_input("Nombre de la nueva tabla")
    num_columns = st.sidebar.number_input("Número de columnas", min_value=1, max_value=10)
    columns = []

    for i in range(int(num_columns)):
        col_name = st.sidebar.text_input(f"Nombre de la columna {i + 1}", key=f"col_name_{i}")
        col_type = st.sidebar.selectbox(f"Tipo de dato de la columna {i + 1}", ["STRING", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP"], key=f"col_type_{i}")
        columns.append((col_name, col_type))

    if st.sidebar.button("Crear Tabla"):
        if table_name and columns:
            cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns])
            query = f"CREATE TABLE `YOUR_PROJECT.YOUR_DATASET.{table_name}` ({cols_str})"
            client.query(query)
            st.sidebar.success("Tabla creada exitosamente")
        else:
            st.sidebar.error("Por favor, proporciona un nombre de tabla y al menos una columna.")

# Sidebar para selección de proyecto y modificación de factores
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]

# Obtener id_proyecto desde la URL si está disponible
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Crear el selectbox para proyectos en el sidebar
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

# Obtener el ID del proyecto seleccionado
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Mostrar ID de proyecto seleccionado para verificación
st.write(f"**ID del Proyecto Seleccionado**: {id_proyecto_seleccionado}")

# Listar tablas que contienen 'tipo_factor' y permitir selección en el sidebar
st.sidebar.subheader("Gestión de Factores para el Proyecto")
tablas_con_tipo_factor = get_tablas_con_tipo_factor()
factores_seleccionados = st.sidebar.multiselect("Factores disponibles:", tablas_con_tipo_factor)

# Guardar factores seleccionados (puedes personalizar esta sección para almacenarlo en una base de datos)
if st.sidebar.button("Guardar selección de factores"):
    st.write(f"Factores guardados para el proyecto: {factores_seleccionados}")

# Crear nueva tabla desde el sidebar
crear_tabla_nueva()

# Mostrar datos de tablas específicas para el proyecto seleccionado
if id_proyecto_seleccionado:
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_especifico)
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")
    
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_destino)
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")
