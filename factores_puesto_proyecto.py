import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Funciones para BigQuery
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

# Función para ejecutar consulta con las nuevas columnas y pesos
def execute_query_for_page(page_name, id_proyecto):
    table_name, id_field = page_name  # Ejemplo: obtener el nombre de la tabla y el campo ID
    
    query = f"""
        SELECT * FROM `{table_name}`
        WHERE {id_field} IN (
            SELECT {id_field} FROM `ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto`
            WHERE id_proyecto = {id_proyecto}
        )
    """
    
    df = client.query(query).result().to_dataframe()

    total_puntos_destino_1 = df['puntos'].iloc[0] if not df.empty else 0
    return df, total_puntos_destino_1

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

    # Diccionario de pesos específicos por puesto
    peso_especifico_por_proyecto = {}
    puntos_destino_peso_total = 0

    for descripcion in selected_puestos:
        id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
        factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

        if not factores_df.empty:
            st.write(f"Factores para el Puesto {id_puesto} ({descripcion})")

            for index, row in factores_df.iterrows():
                tabla_especificos = row['complementos_especificos']
                tabla_destino = row['complementos_destino']

                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                # Contenido de la primera columna (50%)
                with col1:
                    st.subheader(f"Factores Específicos: {tabla_especificos}")
                    df_especificos = obtener_datos_tabla(tabla_especificos)
                    if not df_especificos.empty:
                        st.dataframe(df_especificos)

                with col2:
                    st.subheader(f"Peso del Complemento de Destino ({tabla_destino})")
                    peso_especifico_por_proyecto[tabla_destino] = st.number_input(
                        f'Peso del complemento de destino para {descripcion}', 
                        min_value=0.0,
                        key=f'{tabla_destino}_peso'
                    )

                with col3:
                    puntos_destino_peso = df_especificos['puntos'].sum() * peso_especifico_por_proyecto[tabla_destino] / 100
                    puntos_destino_peso_total += puntos_destino_peso
                    st.write(f"Puntos de destino con peso específico: {puntos_destino_peso}")

                with col4:
                    st.text_input(f'Nota específica para {descripcion}', key=f'{descripcion}_nota')

    st.write(f"Suma de Puntos de Destino Total: {puntos_destino_peso_total}")
else:
    st.info("Selecciona un proyecto y puestos para ver los factores seleccionados.")
