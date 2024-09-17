import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def get_proyectos():
    query = """
        SELECT id_projecto, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    return client.query(query).result().to_dataframe()

def get_puestos(id_proyecto):
    query_ids = f"""
    SELECT DISTINCT id_puesto
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto}
    """
    ids_puestos = client.query(query_ids).result().to_dataframe()['id_puesto'].tolist()
    if ids_puestos:
        query_descripciones = f"""
        SELECT id_puesto, descripcion
        FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        WHERE id_puesto IN UNNEST({ids_puestos})
        """
        return client.query(query_descripciones).result().to_dataframe()
    return pd.DataFrame(columns=['id_puesto', 'descripcion'])

def get_factores_seleccionados(id_proyecto, id_puesto):
    query_especificos = f"""
    SELECT DISTINCT complementos_especificos
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    df_especificos = client.query(query_especificos).result().to_dataframe()

    query_destino = f"""
    SELECT DISTINCT complementos_destino
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    df_destino = client.query(query_destino).result().to_dataframe()

    df_combined = pd.merge(df_especificos, df_destino, how='outer', left_on='complementos_especificos', right_on='complementos_destino')
    return df_combined.fillna('No disponible')

def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

def insertar_datos(table_id, rows_to_insert):
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        st.error(f"Error al insertar datos en {table_id}: {errors}")
    else:
        st.success(f"Datos insertados exitosamente en {table_id}")

# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')

# Selección de Proyecto
st.sidebar.markdown("### Selecciona el proyecto")
proyectos_df = get_proyectos()
proyectos_nombres = proyectos_df['nombre'].tolist()
index_seleccionado = st.sidebar.selectbox("Selecciona un proyecto", proyectos_nombres)
id_proyecto_seleccionado = proyectos_df.query(f"nombre == '{index_seleccionado}'")['id_projecto'].values[0]

# Selección de Puestos
st.sidebar.markdown("### Selecciona los Puestos de Trabajo")
puestos_df = get_puestos(id_proyecto_seleccionado)
puestos_descripciones = puestos_df['descripcion'].tolist()
selected_puestos = st.sidebar.multiselect("Selecciona los puestos", puestos_descripciones)

if id_proyecto_seleccionado and selected_puestos:
    st.markdown(f"### Factores Seleccionados para el Proyecto {id_proyecto_seleccionado}")
    for descripcion in selected_puestos:
        id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
        factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

        if not factores_df.empty:
            st.write(f"Factores para el Puesto {id_puesto} ({descripcion})")

            for index, row in factores_df.iterrows():
                tabla_especificos = row['complementos_especificos']
                tabla_destino = row['complementos_destino']

                if tabla_especificos != 'No disponible':
                    st.subheader(f"Factores Específicos: {tabla_especificos}")
                    df_especificos = obtener_datos_tabla(tabla_especificos)
                    if not df_especificos.empty:
                        # Mostrar tabla completa del dataframe
                        st.write("Tabla de Factores Específicos")
                        st.dataframe(df_especificos)
                        
                        # Crear el selector para elegir `letra` y `descripcion` juntas
                        opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")
                        if seleccion_especifico:
                            # Dividimos la selección en letra y descripción
                            selected_letra, selected_descripcion = seleccion_especifico.split(" - ")
                            st.write(f"Seleccionaste la letra: {selected_letra} y la descripción: {selected_descripcion}")
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores específicos {tabla_especificos}.")
                
                if tabla_destino != 'No disponible':
                    st.subheader(f"Factores de Destino: {tabla_destino}")
                    df_destino = obtener_datos_tabla(tabla_destino)
                    if not df_destino.empty:
                        # Mostrar tabla completa del dataframe
                        st.write("Tabla de Factores de Destino")
                        st.dataframe(df_destino)
                        
                        # Crear el selector para elegir `letra` y `descripcion` juntas
                        opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")
                        if seleccion_destino:
                            # Dividimos la selección en letra y descripción
                            selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                            st.write(f"Seleccionaste la letra: {selected_letra_destino} y la descripción: {selected_descripcion_destino}")
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores de destino {tabla_destino}.")
        else:
            st.write(f"No se encontraron factores para el Puesto {id_puesto} ({descripcion}).")
                
    if st.sidebar.button('Guardar Datos'):
        rows_to_insert = []
        for descripcion in selected_puestos:
            id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
            row = {
                'id_proyecto': id_proyecto_seleccionado,
                'id_puesto': id_puesto,
                # Añadir aquí otros campos necesarios
            }
            rows_to_insert.append(row)
        
        if rows_to_insert:
            insertar_datos("ate-rrhh-2024.Ate_kaibot_2024.puestos_seleccionados_por_proyecto", rows_to_insert)
        else:
            st.warning("No hay datos para guardar.")
else:
    st.info("Selecciona un proyecto y puestos para ver los factores seleccionados.")
