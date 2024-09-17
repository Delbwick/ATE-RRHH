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

def obtener_valoracion_destino(puntos_valoracion_destino):
    query_valoracion_puntos = f"""
    SELECT complemento_destino_anual
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_destino_puntos_por_ano`
    WHERE puntos_valoracion_destino = {puntos_valoracion_destino}
    LIMIT 1
    """
    results = client.query(query_valoracion_puntos).result()
    for row in results:
        return row.complemento_destino_anual
    return None

def obtener_complemento_especifico(id_puesto):
    query_complemento = f"""
    SELECT valor_punto_especifico_proyecto
    FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico`
    WHERE id_puesto = {id_puesto}
    LIMIT 1
    """
    results = client.query(query_complemento).result()
    for row in results:
        return row.valor_punto_especifico_proyecto
    return None

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

# Variable para almacenar las selecciones
selecciones_especificos = []
selecciones_destino = []
selected_puestos_ids = puestos_df.query(f"descripcion in {selected_puestos}")['id_puesto'].tolist()

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
                        st.write("Tabla de Factores Específicos")
                        st.dataframe(df_especificos)
                        
                        opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")
                        if seleccion_especifico:
                            selected_letra, selected_descripcion = seleccion_especifico.split(" - ")
                            st.write(f"Seleccionaste la letra: {selected_letra} y la descripción: {selected_descripcion}")
                            puntos = df_especificos.query(f"letra == '{selected_letra}'")['puntos'].values[0]
                            selecciones_especificos.append({'Puesto': descripcion, 'Letra': selected_letra, 'Descripción': selected_descripcion, 'Puntos': puntos})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores específicos {tabla_especificos}.")
                
                if tabla_destino != 'No disponible':
                    st.subheader(f"Factores de Destino: {tabla_destino}")
                    df_destino = obtener_datos_tabla(tabla_destino)
                    if not df_destino.empty:
                        st.write("Tabla de Factores de Destino")
                        st.dataframe(df_destino)
                        
                        opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")
                        if seleccion_destino:
                            selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                            st.write(f"Seleccionaste la letra: {selected_letra_destino} y la descripción: {selected_descripcion_destino}")
                            puntos_destino = df_destino.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]
                            selecciones_destino.append({'Puesto': descripcion, 'Letra': selected_letra_destino, 'Descripción': selected_descripcion_destino, 'Puntos': puntos_destino})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores de destino {tabla_destino}.")
        else:
            st.write(f"No se encontraron factores para el Puesto {id_puesto} ({descripcion}).")

    # Mostrar la tabla de resumen final
    for descripcion in selected_puestos:
        st.subheader(f"Resumen de Selecciones para el Puesto: {descripcion}")
        
        # Mostrar complementos específicos
        df_especificos_resumen = pd.DataFrame([item for item in selecciones_especificos if item['Puesto'] == descripcion])
        if not df_especificos_resumen.empty:
            st.markdown("#### Complementos Específicos")
            st.table(df_especificos_resumen[['Letra', 'Descripción', 'Puntos']])
        
        # Mostrar complementos de destino
        df_destino_resumen = pd.DataFrame([item for item in selecciones_destino if item['Puesto'] == descripcion])
        if not df_destino_resumen.empty:
            st.markdown("#### Complementos de Destino")
            st.table(df_destino_resumen[['Letra', 'Descripción', 'Puntos']])

    # Calcular puntos de valoración de destino
    puntos_destino_peso_total = round(puntos_destino_peso_total)
    puntos_valoracion = obtener_valoracion_destino(puntos_destino_peso_total)
    if puntos_valoracion:
        st.markdown("### Consulta de Puntos de Valoración de Destino con el Peso Asignado")
        st.write(f"Puntos de Valoración de Destino con el peso asignado ({puntos_destino_peso_total} puntos): {puntos_valoracion:.2f} euros")
    else:
        st.write("No se encontraron puntos de valoración para el valor introducido.")

    # Calcular el complemento específico
    for puesto_id in selected_puestos_ids:
        valor_punto_especifico_proyecto = obtener_complemento_especifico(puesto_id)
        if valor_punto_especifico_proyecto:
            st.write(f"Valor específico del puesto para el complemento específico: {valor_punto_especifico_proyecto:.2f} euros")
        else:
            st.write("No se encontró valor específico para el puesto.")

    # Calcular el sueldo base y total
    for puesto_id in selected_puestos_ids:
        sueldo = sueldo_categoria_puesto[puesto_id]  # Supone que esta variable está definida en otro lugar
        valor_punto_especifico_proyecto = obtener_complemento_especifico(puesto_id)
        if valor_punto_especifico_proyecto:
            valor_punto_especifico_proyecto = valor_punto_especifico_proyecto
        puntos_valoracion = obtener_valoracion_destino(puntos_destino_peso_total)
        
        if puntos_valoracion is not None:
            sueldo_total = sueldo + valor_punto_especifico_proyecto + puntos_valoracion
            st.write(f"Sueldo total (base + complemento específico + valoración): {sueldo_total:.2f} euros")
        else:
            st.write("No se encontraron puntos de valoración para calcular el sueldo total.")
else:
    st.info("Selecciona un proyecto y puestos para ver los factores seleccionados.")
