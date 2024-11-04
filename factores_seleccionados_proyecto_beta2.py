import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino-Manual preliminar")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
    <h3 style="font-family: Arial, sans-serif; font-size: 16px; color: #333333;">
        1. Qué es un libro de valoración, para qué se utiliza y cómo funciona.
    </h3>
    <p style="font-family: Arial, sans-serif; font-size: 14px; color: #555555; text-align: justify;">
        Un libro de valoración se utiliza para valorar puestos de trabajo de forma objetiva...
        (continúa con el resto de tu texto)
    </p>
</div>
"""
# Mostrar el HTML en Streamlit
st.markdown(scrollable_text_html, unsafe_allow_html=True)

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Funciones para obtener proyectos y complementos
def get_proyectos():
    query = "SELECT id_projecto AS id, nombre FROM ate-rrhh-2024.Ate_kaibot_2024.proyecto"
    query_job = client.query(query)
    results = query_job.result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

def get_complementos_especificos(id_proyecto):
    query = f"SELECT complemento_especifico FROM ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto WHERE id_proyecto = {id_proyecto}"
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_especifico for row in results]

def get_complementos_destino(id_proyecto):
    query = f"SELECT complemento_destino FROM ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto WHERE id_proyecto = {id_proyecto}"
    query_job = client.query(query)
    results = query_job.result()
    return [row.complemento_destino for row in results]

def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM {nombre_tabla} LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Crear el sidebar para selección de proyectos
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Crear el selectbox para proyectos en el sidebar
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Mostrar ID de proyecto seleccionado para verificación
st.write(f"**ID del Proyecto Seleccionado**: {id_proyecto_seleccionado}")

# Función para mostrar y gestionar complementos específicos
def mostrar_complementos_especificos(id_proyecto_seleccionado):
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_especifico)
            
            # Formulario para insertar, modificar o eliminar datos
            with st.form(key=f'form_{nombre_tabla}'):
                st.write("### Operaciones")
                # Campo para añadir nueva fila
                nuevo_valor = st.text_input("Añadir nuevo valor (ejemplo: 'valor1, valor2')", "")
                if st.form_submit_button("Insertar"):
                    # Lógica para insertar el nuevo valor en la base de datos
                    st.write(f"Valor insertado: {nuevo_valor} en la tabla {nombre_tabla}")
                    # Aquí va el código para insertar el valor en la base de datos

                # Campo para modificar datos
                modificar_valor = st.text_input("Modificar valor existente (especifica ID)", "")
                nuevo_valor_modificado = st.text_input("Nuevo valor (ejemplo: 'valor1, valor2')", "")
                if st.form_submit_button("Modificar"):
                    # Lógica para modificar el valor en la base de datos
                    st.write(f"Valor modificado: {nuevo_valor_modificado} en la tabla {nombre_tabla} con ID {modificar_valor}")
                    # Aquí va el código para modificar el valor en la base de datos

                # Campo para eliminar datos
                eliminar_valor = st.text_input("Eliminar valor (especifica ID)", "")
                if st.form_submit_button("Eliminar"):
                    # Lógica para eliminar el valor en la base de datos
                    st.write(f"Valor eliminado de la tabla {nombre_tabla} con ID {eliminar_valor}")
                    # Aquí va el código para eliminar el valor en la base de datos
    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")

# Función para mostrar y gestionar complementos de destino
def mostrar_complementos_destino(id_proyecto_seleccionado):
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            st.dataframe(df_complemento_destino)

            # Formulario para insertar, modificar o eliminar datos
            with st.form(key=f'destino_form_{nombre_tabla}'):
                st.write("### Operaciones")
                # Campo para añadir nueva fila
                nuevo_valor = st.text_input("Añadir nuevo valor (ejemplo: 'valor1, valor2')", "")
                if st.form_submit_button("Insertar"):
                    # Lógica para insertar el nuevo valor en la base de datos
                    st.write(f"Valor insertado: {nuevo_valor} en la tabla {nombre_tabla}")
                    # Aquí va el código para insertar el valor en la base de datos

                # Campo para modificar datos
                modificar_valor = st.text_input("Modificar valor existente (especifica ID)", "")
                nuevo_valor_modificado = st.text_input("Nuevo valor (ejemplo: 'valor1, valor2')", "")
                if st.form_submit_button("Modificar"):
                    # Lógica para modificar el valor en la base de datos
                    st.write(f"Valor modificado: {nuevo_valor_modificado} en la tabla {nombre_tabla} con ID {modificar_valor}")
                    # Aquí va el código para modificar el valor en la base de datos

                # Campo para eliminar datos
                eliminar_valor = st.text_input("Eliminar valor (especifica ID)", "")
                if st.form_submit_button("Eliminar"):
                    # Lógica para eliminar el valor en la base de datos
                    st.write(f"Valor eliminado de la tabla {nombre_tabla} con ID {eliminar_valor}")
                    # Aquí va el código para eliminar el valor en la base de datos
    else:
        st.write("No se encontraron complementos de destino para el proyecto seleccionado.")

# Obtener y mostrar datos de tablas específicas para el proyecto seleccionado
if id_proyecto_seleccionado:
    mostrar_complementos_especificos(id_proyecto_seleccionado)
    mostrar_complementos_destino(id_proyecto_seleccionado)
