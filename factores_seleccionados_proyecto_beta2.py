import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino - Manual preliminar")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
       1.	Qué es un libro de valoración, para qué se utiliza y cómo funciona.

Un libro de valoración se utiliza para valorar puestos de trabajo de forma objetiva. No se tienen en cuenta las personas que ocupan los puestos, sino los requisitos necesarios de cada puesto.
Se presentan los factores elegidos para valorar la organización, la graduación de los factores y el peso porcentual específico de cada factor en función de la organización.
El objetivo de la valoración de puestos de trabajo es establecer el valor relativo de los puestos de una organización, asignando a cada puesto una clasificación profesional y estableciendo una retribución en función de la valoración de diversos factores.
Hay que elegir los factores que se van a utilizar para realizar la valoración. Tanto los que determinan los complementos de destino como los que determinan los complementos específicos. La elección de los factores es relativamente libre mientras nos adaptemos a  los criterios legales.
Además, a cada factor se le asignará un peso porcentual específico. De esta forma, escalonamos la importancia del propio factor dentro de la organización.
Los factores de cada complemento, de destino, por un lado, y los específicos, por otro, deben sumar cada uno por su lado un 100%.
Los pesos porcentuales se refieren y se suelen escoger según la importancia o repetición de determinadas funciones en los puestos de trabajo de la institución, aunque la negociación con los representantes sindicales puede dar porcentajes poco habituales.
Asimismo, los factores se dividen en niveles alfabéticos (se pueden añadir más graduaciones de la A a la G si se desea) y cada grado tiene una valoración entre 0 y 100.
La combinación del peso específico del factor y la valoración por puntos nos permite trasladarnos a un resultado económico numérico de cada puesto de trabajo.

    </h3>
    <!-- Contenido omitido para brevedad -->
</div>
"""

# Mostrar el HTML en Streamlit
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

# Función para obtener complementos específicos de cada proyecto
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_especifico for row in results]

# Función para obtener complementos de destino de cada proyecto
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

# Función para mostrar opciones de edición de un dataframe
def mostrar_opciones_complementos(nombre_tabla, df, tipo_complemento):
    st.write(f"**Tabla: {nombre_tabla} ({tipo_complemento})**")
    
    # Mostrar el DataFrame
    st.dataframe(df)

    # Botones para agregar, eliminar y editar filas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"Agregar NUEVO SOLAMENTE VINCULADO A ESE PROYECTO{tipo_complemento}", key=f"add_{nombre_tabla}_{tipo_complemento}"):
            agregar_fila(df, nombre_tabla)
            
    with col2:
        if st.button(f"Eliminar SOLO DEL PROYECTO{tipo_complemento}", key=f"delete_{nombre_tabla}_{tipo_complemento}"):
            eliminar_fila(df, nombre_tabla)
            
    with col3:
        if st.button(f"Editar (CLONAR FACTOR EXISTENTE POR PORYECTO){tipo_complemento}", key=f"edit_{nombre_tabla}_{tipo_complemento}"):
            editar_fila(df, nombre_tabla)

# Funciones para modificar el dataframe
def agregar_fila(df, nombre_tabla):
    # Formulario para agregar una nueva fila
    st.write("### Agregar una nueva fila")
    nueva_fila = {}
    for col in df.columns:
        nueva_fila[col] = st.text_input(f"{col}", key=f"input_{nombre_tabla}_add_{col}")

    if st.button("Guardar nueva fila", key=f"save_new_{nombre_tabla}"):
        new_df = df.append(nueva_fila, ignore_index=True)
        st.write("Fila agregada:")
        st.dataframe(new_df)
        return new_df  # Devuelve el dataframe actualizado

def eliminar_fila(df, nombre_tabla):
    # Permite seleccionar y eliminar una fila
    st.write("### Seleccionar una fila para eliminar")
    fila_index = st.selectbox("Seleccione el índice de la fila", df.index, key=f"delete_row_{nombre_tabla}")
    if st.button("Eliminar fila seleccionada", key=f"confirm_delete_{nombre_tabla}"):
        df = df.drop(fila_index).reset_index(drop=True)
        st.write("Fila eliminada:")
        st.dataframe(df)
        return df

def editar_fila(df, nombre_tabla):
    # Permite seleccionar y editar una fila
    st.write("### Editar una fila existente")
    fila_index = st.selectbox("Seleccione el índice de la fila para editar", df.index, key=f"edit_row_{nombre_tabla}")
    fila_seleccionada = df.loc[fila_index]

    valores_editados = {}
    for col in df.columns:
        valores_editados[col] = st.text_input(f"{col}", fila_seleccionada[col], key=f"edit_{nombre_tabla}_{col}_{fila_index}")

    if st.button("Guardar cambios", key=f"confirm_edit_{nombre_tabla}"):
        for col, val in valores_editados.items():
            df.at[fila_index, col] = val
        st.write("Fila actualizada:")
        st.dataframe(df)
        return df

# Configuración del Sidebar
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar el proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Selectbox para seleccionar el proyecto
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)


# Funcionalidad de selección de factores
st.sidebar.markdown("<h2>Selecciona los Factores</h2>", unsafe_allow_html=True)
opcion = st.sidebar.selectbox("Tipo de Factor", [
    "Factores de formación", 
    "Factores de jerarquización o mando", 
    "Factores de responsabilidad", 
    "Factores de iniciativa o autonomía", 
    "Factores de Complejidad"
])

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

# Obtener los datos de la tabla en función de la etiqueta
project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Consulta SQL para obtener las tablas y sus columnas principales
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
    ORDER BY column_name
"""

# Ejecutar la consulta y obtener los resultados
tables_query_job = client.query(query)
tables = tables_query_job.result()
tablas_seleccionadas = [row.table_name for row in tables]

# Inicializar la lista de selecciones
selecciones_destino = []

# Mostrar las tablas y permitir la selección
st.sidebar.markdown("<h2>Selecciona los Factores de complemento de destino:</h2>", unsafe_allow_html=True)
for tabla in tablas_seleccionadas:
    if st.sidebar.checkbox(tabla, key=f"checkbox_{tabla}"):
        selecciones_destino.append(tabla)

# Botón para guardar selecciones
if st.sidebar.button("Guardar selecciones"):
    tabla_seleccion = f"{project_id}.{dataset_id}.nombre_de_la_tabla_de_destino"  # Cambia este valor por el nombre correcto de la tabla de destino
    guardar_selecciones_en_bigquery(tabla_seleccion, id_proyecto_seleccionado, selecciones_destino)

#>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>


# Mostrar complementos específicos y de destino en pagna principal
if id_proyecto_seleccionado:
    # Complementos específicos
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            mostrar_opciones_complementos(nombre_tabla, df_complemento_especifico, "complemento específico")
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")
    
    # Complementos de destino
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            mostrar_opciones_complementos(nombre_tabla, df_complemento_destino, "complemento de destino")
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")
