import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np


# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Inicializa el cliente de BigQuery
#client = bigquery.Client()

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



# Función para obtener puestos
def get_puestos():
    query = "SELECT id_puesto, descripcion FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`"
    query_job = client.query(query)
    puestos_df = query_job.result().to_dataframe()  # Convertimos a DataFrame
    return puestos_df

# Función para obtener factores seleccionados
def get_factores_seleccionados(id_proyecto,selected_puestos_id):
    query = f"""
    SELECT DISTINCT complementos_especificos, complementos_destino
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto={selected_puestos_id}
    GROUP BY complementos_especificos, complementos_destino
    """
    query_job = client.query(query)
    df = query_job.result().to_dataframe()

     # Eliminar filas duplicadas, manteniendo solo combinaciones únicas
    #df = df.drop_duplicates(subset=['complementos_especificos', 'complementos_destino'])
    
    return df

# Función para obtener los datos de una tabla específica
def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

# Función para insertar datos en BigQuery
def insertar_datos(table_id, rows_to_insert):
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        st.error(f"Error al insertar datos en {table_id}: {errors}")
    else:
        st.success(f"Datos insertados exitosamente en {table_id}")

# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')

# Selección de Puestos
# Obtener los puestos disponibles
puestos_df = get_puestos()

# Crear un diccionario que mapee descripcion -> id_puesto
puestos_dict = dict(zip(puestos_df['descripcion'], puestos_df['id_puesto']))

# Mostrar el multiselect para seleccionar los puestos (basado en descripcion)
st.markdown("<h2>Selecciona los Puestos de Trabajo</h2>", unsafe_allow_html=True)
selected_puestos_desc = st.multiselect("Selecciona los puestos", puestos_df['descripcion'])

# Obtener los id_puesto correspondientes a las descripciones seleccionadas
selected_puestos_id = [puestos_dict[desc] for desc in selected_puestos_desc]

# Mostrar los id_puesto seleccionados
st.write(f"ID de Puestos seleccionados: {selected_puestos_id}")
# Selección de Proyecto
id_proyecto = st.number_input('ID de Proyecto', min_value=1,value=id_proyecto_seleccionado, step=1)

# Mostrar factores seleccionados para el proyecto
if id_proyecto:
    factores_df = get_factores_seleccionados(id_proyecto,selected_puestos_id)

    if not factores_df.empty:
        st.write("Factores Seleccionados para el Proyecto")
        st.dataframe(factores_df)
        
        for index, row in factores_df.iterrows():
            # Obtener los datos de las tablas basadas en los factores
            tabla_especificos = row['complementos_especificos']
            tabla_destino = row['complementos_destino']

            st.markdown(f"### Factores Específicos: {tabla_especificos}")
            df_especificos = obtener_datos_tabla(tabla_especificos)
            if not df_especificos.empty:
                opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df_especificos.iterrows()]
                seleccion_especifico = st.radio(f"Seleccione un valor para {tabla_especificos.split('.')[-1]}:", opciones, key=f"especifico_{index}")
                if seleccion_especifico:
                    selected_value_especifico = df_especificos.loc[opciones.index(seleccion_especifico), df_especificos.columns[0]]
                    
            st.markdown(f"### Factores de Destino: {tabla_destino}")
            df_destino = obtener_datos_tabla(tabla_destino)
            if not df_destino.empty:
                opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df_destino.iterrows()]
                seleccion_destino = st.radio(f"Seleccione un valor para {tabla_destino.split('.')[-1]}:", opciones, key=f"destino_{index}")
                if seleccion_destino:
                    selected_value_destino = df_destino.loc[opciones.index(seleccion_destino), df_destino.columns[0]]

            # Aquí podrías agregar lógica para almacenar los valores seleccionados si es necesario

# Botón para guardar en BigQuery
if st.button('Guardar Datos'):
    rows_to_insert = []
    for descripcion in selected_puestos:
        query = f"""
        SELECT id_puesto FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos` WHERE descripcion = '{descripcion}'
        """
        query_job = client.query(query)
        id_puesto = query_job.result().to_dataframe()['id_puesto'].iloc[0]
        
        row = {
            'id_proyecto': id_proyecto,
            'id_puesto': id_puesto,
            # Añadir aquí otros campos necesarios como los valores seleccionados
        }
        rows_to_insert.append(row)
    
    if rows_to_insert:
        insertar_datos("ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto", rows_to_insert)
