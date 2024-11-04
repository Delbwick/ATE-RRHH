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
        1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.
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
        if st.button(f"Agregar {tipo_complemento}", key=f"add_{nombre_tabla}_{tipo_complemento}"):
            agregar_fila(df, nombre_tabla)
            
    with col2:
        if st.button(f"Eliminar {tipo_complemento}", key=f"delete_{nombre_tabla}_{tipo_complemento}"):
            eliminar_fila(df, nombre_tabla)
            
    with col3:
        if st.button(f"Editar {tipo_complemento}", key=f"edit_{nombre_tabla}_{tipo_complemento}"):
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

# Mostrar complementos específicos y de destino
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
