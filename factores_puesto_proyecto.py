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

def get_proyectos():
    query = """
        SELECT id_projecto, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    proyectos = [{'id': row.id_projecto, 'nombre': row.nombre} for row in results]
    return proyectos

def get_puestos(id_proyecto):
    # Obtener los IDs de los puestos relacionados con el proyecto
    query_ids = f"""
    SELECT DISTINCT id_puesto
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto}
    """
    query_job_ids = client.query(query_ids)
    ids_result = query_job_ids.result()
    ids_puestos = [row.id_puesto for row in ids_result]

    # Obtener las descripciones de los puestos basados en los IDs obtenidos
    if ids_puestos:
        query_descripciones = f"""
        SELECT id_puesto, descripcion
        FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        WHERE id_puesto IN UNNEST({ids_puestos})
        """
        query_job_descripciones = client.query(query_descripciones)
        descripciones_result = query_job_descripciones.result()
        puestos = [{'id': row.id_puesto, 'descripcion': row.descripcion} for row in descripciones_result]
        return puestos
    else:
        return []

def get_factores_seleccionados(id_proyecto, id_puesto):
    # Consulta para obtener valores únicos de complementos_especificos
    query_especificos = f"""
    SELECT DISTINCT complementos_especificos
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    query_job_especificos = client.query(query_especificos)
    df_especificos = query_job_especificos.result().to_dataframe()

    # Consulta para obtener valores únicos de complementos_destino
    query_destino = f"""
    SELECT DISTINCT complementos_destino
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    query_job_destino = client.query(query_destino)
    df_destino = query_job_destino.result().to_dataframe()

    # Limpiar valores vacíos y renombrar columnas
    df_especificos = df_especificos.dropna(subset=['complementos_especificos'])
    df_destino = df_destino.dropna(subset=['complementos_destino'])
    
    df_especificos.rename(columns={'complementos_especificos': 'complemento'}, inplace=True)
    df_destino.rename(columns={'complementos_destino': 'complemento'}, inplace=True)

    # Combinar los resultados de ambas consultas
    df_combined = pd.merge(df_especificos, df_destino, how='outer', left_on='complemento', right_on='complemento')

    return {
        'especificos': df_especificos,
        'destino': df_destino
    }


def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

def insertar_datos(table_id, rows_to_insert):
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        st.error(f"Error al insertar datos en {table_id}: {errors}")
    else:
        st.success(f"Datos insertados exitosamente en {table_id}")

# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')

# Selección de Proyecto
st.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
index_seleccionado = st.selectbox("Selecciona un proyecto", proyectos_nombres)
id_proyecto_seleccionado = next(proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == index_seleccionado)

# Selección de Puestos
st.markdown("<h2>Selecciona los Puestos de Trabajo</h2>", unsafe_allow_html=True)
puestos = get_puestos(id_proyecto_seleccionado)
puestos_descripciones = [puesto['descripcion'] for puesto in puestos]
selected_puestos = st.multiselect("Selecciona los puestos", puestos_descripciones)

# Mostrar factores seleccionados para el proyecto
if id_proyecto_seleccionado and selected_puestos:
    for descripcion in selected_puestos:
        id_puesto = next(puesto['id'] for puesto in puestos if puesto['descripcion'] == descripcion)

        factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

        if not factores_df.empty:
            st.write(f"Factores Seleccionados para el Proyecto {id_proyecto_seleccionado} y Puesto {id_puesto}")
            st.dataframe(factores_df)
            
            for index, row in factores_df.iterrows():
                # Obtener los datos de las tablas basadas en los factores
                tabla_especificos = row['complementos_especificos']
                tabla_destino = row['complementos_destino']

                st.markdown(f"### Factores Específicos: {tabla_especificos}")
                df_especificos = obtener_datos_tabla(tabla_especificos)
                if not df_especificos.empty:
                    opciones_especificos = [f"{row['descripcion']} ({row['letra']})" for index, row in df_especificos.iterrows()]
                    seleccion_especifico = st.radio(f"Seleccione un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")
                    if seleccion_especifico:
                        selected_value_especifico = df_especificos.loc[opciones_especificos.index(seleccion_especifico), df_especificos.columns[0]]
                    
                st.markdown(f"### Factores de Destino: {tabla_destino}")
                df_destino = obtener_datos_tabla(tabla_destino)
                if not df_destino.empty:
                    opciones_destino = [f"{row['descripcion']} ({row['letra']})" for index, row in df_destino.iterrows()]
                    seleccion_destino = st.radio(f"Seleccione un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")
                    if seleccion_destino:
                        selected_value_destino = df_destino.loc[opciones_destino.index(seleccion_destino), df_destino.columns[0]]

            # Aquí podrías agregar lógica para almacenar los valores seleccionados si es necesario

# Botón para guardar en BigQuery
if st.button('Guardar Datos'):
    rows_to_insert = []
    for descripcion in selected_puestos:
        id_puesto = next(puesto['id'] for puesto in puestos if puesto['descripcion'] == descripcion)
        
        row = {
            'id_proyecto': id_proyecto_seleccionado,
            'id_puesto': id_puesto,
            # Añadir aquí otros campos necesarios como los valores seleccionados
        }
        rows_to_insert.append(row)
    
    if rows_to_insert:
        insertar_datos("ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto", rows_to_insert)
