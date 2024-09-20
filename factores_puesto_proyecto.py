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

                # Factores Específicos
                if tabla_especificos != 'No disponible':
                    st.subheader(f"Factores Específicos: {tabla_especificos}")
                    df_especificos = obtener_datos_tabla(tabla_especificos)
                    if not df_especificos.empty:
                        #st.write("Tabla de Factores Específicos")
                        #st.dataframe(df_especificos)

                        # Selección de un valor específico en dos columnas (75% y 25%)
                        opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                        # Dividimos la UI en dos columnas
                        col1, col2 = st.columns([3, 1])  # 75% y 25%

                        with col1:
                            st.write("Tabla de Factores Específicos")
                            st.dataframe(df_especificos)
                            seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")

                        if seleccion_especifico:
                            selected_letra, selected_descripcion = seleccion_especifico.split(" - ")
                            puntos = df_especificos.query(f"letra == '{selected_letra}'")['puntos'].values[0]

                            # Input para porcentaje en la segunda columna
                            with col2:
                                #porcentaje_especifico = st.number_input(f"% {selected_descripcion}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{index}')
                                porcentaje_especifico = st.number_input(f"%Peso del complemento de destino para {tabla_especificos}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{index}')


                            # Calcular puntos ajustados
                            puntos_ajustados = puntos * (porcentaje_especifico / 100)

                            # Mostrar resultado
                            st.write(f"Seleccionaste la letra: {selected_letra} y la descripción: {selected_descripcion}")
                            st.write(f"Puntos originales: {puntos}")
                            st.write(f"Puntos ajustados (con {porcentaje_especifico}%): {puntos_ajustados:.2f}")
                            selecciones_especificos.append({'Puesto': descripcion, 'Letra': selected_letra, 'Descripción': selected_descripcion, 'Puntos': puntos_ajustados})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores específicos {tabla_especificos}.")

                # Factores de Destino
                if tabla_destino != 'No disponible':
                    st.subheader(f"Factores de Destino: {tabla_destino}")
                    df_destino = obtener_datos_tabla(tabla_destino)
                    if not df_destino.empty:
                        st.write("Tabla de Factores de Destino")
                        st.dataframe(df_destino)

                        # Selección de un valor destino en dos columnas (75% y 25%)
                        opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                        # Dividimos la UI en dos columnas
                        col1, col2 = st.columns([3, 1])  # 75% y 25%

                        with col1:
                            seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")

                        if seleccion_destino:
                            selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                            puntos_destino = df_destino.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]

                            # Input para porcentaje en la segunda columna
                            with col2:
                                porcentaje_destino = st.number_input(f"% {selected_descripcion_destino}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_destino_{index}')

                            # Calcular puntos ajustados
                            puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)

                            # Mostrar resultado
                            st.write(f"Seleccionaste la letra: {selected_letra_destino} y la descripción: {selected_descripcion_destino}")
                            st.write(f"Puntos originales: {puntos_destino}")
                            st.write(f"Puntos ajustados (con {porcentaje_destino}%): {puntos_ajustados_destino:.2f}")
                            selecciones_destino.append({'Puesto': descripcion, 'Letra': selected_letra_destino, 'Descripción': selected_descripcion_destino, 'Puntos': puntos_ajustados_destino})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores de destino {tabla_destino}.")


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

    # Calcular sueldo total
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.title("Cálculo de Sueldo Total")

    sueldo_categoria_puesto = {id_puesto: 2000 for id_puesto in selected_puestos_ids}  # Dummy values, replace with actual
    puntos_especifico_sueldo = sum(item['Puntos'] for item in selecciones_especificos)
    puntos_valoracion = sum(item['Puntos'] for item in selecciones_destino)

    for puesto_id in selected_puestos_ids:
        puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
        sueldo = sueldo_categoria_puesto[puesto_id]
        
        sueldo_total_puesto = sueldo + puntos_especifico_sueldo + puntos_valoracion
        
        # Mostrar el cálculo para cada puesto
        st.markdown(f"<h2>Cálculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
        st.write(f"Bruto Anual con Jornada Ordinaria: {sueldo} + {puntos_especifico_sueldo} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")

    # Selección de la modalidad de disponibilidad especial
    modalidad_disponibilidad = st.selectbox(
        'Selecciona la modalidad de disponibilidad especial:',
        options=[
            'Ninguna',
            'Jornada ampliada (hasta 10%)',
            'Disponibilidad absoluta (hasta 15%)',
            'Jornada ampliada con disponibilidad absoluta (hasta 20%)'
        ]
    )

    # Inicialización del porcentaje según la modalidad seleccionada
    porcentaje_disponibilidad = 0.0
    if modalidad_disponibilidad == 'Jornada ampliada (hasta 10%)':
        porcentaje_disponibilidad = 10.0
    elif modalidad_disponibilidad == 'Disponibilidad absoluta (hasta 15%)':
        porcentaje_disponibilidad = 15.0
    elif modalidad_disponibilidad == 'Jornada ampliada con disponibilidad absoluta (hasta 20%)':
        porcentaje_disponibilidad = 20.0

    # Calcular el sueldo con disponibilidad especial
    for puesto_id in selected_puestos_ids:
        puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
        sueldo = sueldo_categoria_puesto[puesto_id]
        
        sueldo_total_puesto = sueldo + puntos_especifico_sueldo + puntos_valoracion
        
        sueldo_bruto_con_complementos = sueldo + puntos_especifico_sueldo + puntos_valoracion
        if porcentaje_disponibilidad > 0:
            incremento_disponibilidad = sueldo_bruto_con_complementos * (porcentaje_disponibilidad / 100)
            sueldo_total_con_disponibilidad = sueldo_total_puesto + incremento_disponibilidad
            st.write(f"Con la modalidad '{modalidad_disponibilidad}' ({porcentaje_disponibilidad}%), el sueldo total ajustado es: {sueldo_total_con_disponibilidad:.2f} euros")
        else:
            st.write("No se ha aplicado ningún complemento de disponibilidad especial.")

    # Mostrar la referencia a la última publicación oficial
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.markdown("Última publicación oficial: BOPV del 27 de febrero del 2024")

else:
    st.info("Selecciona un proyecto y puestos para ver los factores seleccionados.")
