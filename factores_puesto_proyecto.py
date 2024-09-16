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

def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

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

    # Eliminar filas con valores NaN y combinar los resultados
    df_especificos = df_especificos.dropna(subset=['complementos_especificos'])
    df_destino = df_destino.dropna(subset=['complementos_destino'])
    
    # Combinar los resultados en un DataFrame
    df_combined = pd.merge(df_especificos, df_destino, how='outer', 
                           left_on='complementos_especificos', 
                           right_on='complementos_destino')

    return df_combined

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
id_proyecto = st.number_input('ID de Proyecto', min_value=1, step=1)
id_puesto = st.number_input('ID de Puesto', min_value=1, step=1)

st.markdown("<h2>Selecciona los Puestos de Trabajo</h2>", unsafe_allow_html=True)
puestos = get_puestos(id_proyecto)  # Asegúrate de que get_puestos acepte id_proyecto
selected_puestos = st.multiselect("Selecciona los puestos", [puesto['descripcion'] for puesto in puestos])

# Mostrar factores seleccionados para el proyecto
if id_proyecto and id_puesto:
    factores_df = get_factores_seleccionados(id_proyecto, id_puesto)

    if not factores_df.empty:
        st.write("Factores Seleccionados para el Proyecto")
        st.dataframe(factores_df)
        
        for index, row in factores_df.iterrows():
            tabla_especificos = row['complementos_especificos']
            tabla_destino = row['complementos_destino']

            if pd.notna(tabla_especificos):
                st.markdown(f"### Factores Específicos: {tabla_especificos}")
                df_especificos = obtener_datos_tabla(tabla_especificos)
                if not df_especificos.empty:
                    opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df_especificos.iterrows()]
                    seleccion_especifico = st.radio(f"Seleccione un valor para {tabla_especificos.split('.')[-1]}:", opciones, key=f"especifico_{index}")
                    if seleccion_especifico:
                        selected_value_especifico = df_especificos.loc[opciones.index(seleccion_especifico), df_especificos.columns[0]]
            
            if pd.notna(tabla_destino):
                st.markdown(f"### Factores de Destino: {tabla_destino}")
                df_destino = obtener_datos_tabla(tabla_destino)
                if not df_destino.empty:
                    opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df_destino.iterrows()]
                    seleccion_destino = st.radio(f"Seleccione un valor para {tabla_destino.split('.')[-1]}:", opciones, key=f"destino_{index}")
                    if seleccion_destino:
                        selected_value_destino = df_destino.loc[opciones.index(seleccion_destino), df_destino.columns[0]]

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
