import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

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
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener datos de una tabla específica (complementos)
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"  # Solo los primeros 100 registros
    df = client.query(query).result().to_dataframe().fillna('No disponible')
    return df

# Función para obtener la descripción de una tabla
def obtener_descripcion_tabla(nombre_tabla):
    query = f"DESCRIBE `{nombre_tabla}`"  # Esto da el esquema de la tabla
    result = client.query(query).result()
    return result

# Función para mostrar la interfaz
def mostrar_interfaz():
    # Obtener los proyectos
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0]  # Selección por defecto del primer proyecto

    # Crear el sidebar con el selectbox
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

    # Obtener el ID del proyecto seleccionado
    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    # Mostrar mensaje de advertencia
    st.markdown("""
    **Importante**: Los porcentajes para los complementos de destino y específicos deben sumar **100%**.
    Asegúrate de que la suma de los porcentajes de cada grupo sea exactamente 100%.
    """)

    # Mostrar los complementos de destino y específicos
    if id_proyecto_seleccionado:
        # Obtener complementos
        complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
        complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")

        # Complementos de destino
        for complemento in complementos_destino:
            # Mostrar la descripción de la tabla
            nombre_tabla_destino = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            descripcion_destino = obtener_descripcion_tabla(nombre_tabla_destino)
            st.write(f"**Descripción de la tabla: {complemento} (Destino)**")
            st.write(descripcion_destino)

            # Mostrar los datos de la tabla
            df_destino = obtener_datos_tabla(nombre_tabla_destino)
            st.write(f"**Datos de la tabla {complemento} (Destino):**")
            st.dataframe(df_destino)

        # Complementos específicos
        for complemento in complementos_especificos:
            # Mostrar la descripción de la tabla
            nombre_tabla_especifico = f"ate-rrhh-2024.Ate_kaibot_2024.{complemento}"
            descripcion_especifico = obtener_descripcion_tabla(nombre_tabla_especifico)
            st.write(f"**Descripción de la tabla: {complemento} (Específico)**")
            st.write(descripcion_especifico)

            # Mostrar los datos de la tabla
            df_especifico = obtener_datos_tabla(nombre_tabla_especifico)
            st.write(f"**Datos de la tabla {complemento} (Específico):**")
            st.dataframe(df_especifico)

# Llamar a la función para mostrar la interfaz
mostrar_interfaz()
