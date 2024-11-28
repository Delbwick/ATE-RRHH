import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="App valoraciones Puestos de trabajo - Escenarios Posibles", page_icon="🥸")
st.title("¡Bienvenido a APP VALORACIONES DE PUESTOS DE TRABAJO 👷")
st.header("Posibles Escenarios para el proyecto - beta4")

# HTML personalizado para el encabezado
header_html = """
     <style>
          /* Colores principales */
        :root {
            --color-principal: #007d9a;
            --color-secundario: #dfa126;
            --color-texto: #333333;
        }

        /* Estilos generales */
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: var(--color-texto);
        }
        .header-container {
            background-color: #007d9a; /* Color de fondo principal */
            padding: 0;
            text-align: center;
        }
        .logo {
            width: 100%;  /* Hacer que el logo ocupe todo el ancho */
            max-height: 300px; /* Limitar la altura del banner */
            object-fit: cover;  /* Asegura que el logo se ajuste bien */
        }
        .wide-line {
            width: 100%;
            height: 2px;
            background-color: var(--color-secundario);
            margin-top: 20px;
            margin-bottom: 20px;
        }
    h1 {
        font-family: 'Arial', sans-serif;
        font-size: 17pt;
        text-align: left;
        color: #333333;
    }
    h2 {
        font-family: 'Arial', sans-serif;
        font-size: 17pt;
        text-align: left;
        color: #333333;
    }
    h4 {
            font-size: 20pt;
            color: var(--color-principal);
            font-weight: bold;
        }

        /* Estilo para el formulario */
        .stTextInput, .stDateInput, .stCheckbox, .stSelectbox, .stRadio {
            background-color: #ffffff;
            border: 1px solid var(--color-principal);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }

        .stTextInput input, .stDateInput input, .stCheckbox input, .stSelectbox select, .stRadio input {
            color: var(--color-texto);
        }

        .stButton>button {
            background-color: var(--color-secundario);
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            border: none;
            font-size: 14pt;
        }

        .stButton>button:hover {
            background-color: darkorange;
        }

        /* Estilo del botón de redirección */
        .stButton a {
            color: white;
            text-decoration: none;
        }
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://kaibot.es/wp-content/uploads/2024/11/banner-app-1.png" alt="Logo"></div>', unsafe_allow_html=True)




# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Funciones de consulta
def obtener_datos(query):
    return client.query(query).result().to_dataframe().fillna('No disponible')

def get_proyectos():
    return obtener_datos("SELECT id_projecto, nombre FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`")

def get_puestos(id_proyecto):
    query = f"""
    SELECT DISTINCT id_puesto, descripcion
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto}
    """
    return obtener_datos(query)

def get_factores_seleccionados(id_proyecto, id_puesto):
    query_especificos = f"""
    SELECT DISTINCT complementos_especificos FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    query_destino = f"""
    SELECT DISTINCT complementos_destino FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    df_especificos = obtener_datos(query_especificos)
    df_destino = obtener_datos(query_destino)
    return pd.merge(df_especificos, df_destino, how='outer', left_on='complementos_especificos', right_on='complementos_destino')

# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')

# Selección de Proyecto
proyectos_df = get_proyectos()
index_seleccionado = st.sidebar.selectbox("Selecciona un proyecto", proyectos_df['nombre'].tolist())
id_proyecto_seleccionado = proyectos_df.query(f"nombre == '{index_seleccionado}'")['id_projecto'].values[0]

# Selección de Puestos
puestos_df = get_puestos(id_proyecto_seleccionado)
selected_puestos = st.sidebar.multiselect("Selecciona los puestos", puestos_df['descripcion'].tolist())

# Selección de Categoría
opcion_proyecto = st.sidebar.selectbox("Seleccione una Categoría:", ("A!", "A2", "B1", "B2"))

# Variables de selección
selecciones_especificos = []
selecciones_destino = []
selected_puestos_ids = puestos_df.query(f"descripcion in {selected_puestos}")['id_puesto'].tolist()

# Procesar los puestos seleccionados
if id_proyecto_seleccionado and selected_puestos:
    for descripcion in selected_puestos:
        id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
        factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

        for index, row in factores_df.iterrows():
            tabla_especificos, tabla_destino = row['complementos_especificos'], row['complementos_destino']
            if tabla_especificos != 'No disponible':
                st.write(f"Factores Específicos: {tabla_especificos}")
                df_especificos = obtener_datos(f"SELECT * FROM `{tabla_especificos}` LIMIT 100")
                opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos)
                if seleccion_especifico:
                    selected_letra = seleccion_especifico.split(" - ")[0]
                    puntos = df_especificos.query(f"letra == '{selected_letra}'")['puntos'].values[0]
                    porcentaje_especifico = st.number_input(f"Peso del complemento específico para {tabla_especificos}", min_value=0.0, max_value=100.0, value=100.0)
                    puntos_ajustados = puntos * (porcentaje_especifico / 100)
                    selecciones_especificos.append({'Puesto': descripcion, 'Letra': selected_letra, 'Puntos': puntos_ajustados})

            if tabla_destino != 'No disponible':
                st.write(f"Factores de Destino: {tabla_destino}")
                df_destino = obtener_datos(f"SELECT * FROM `{tabla_destino}` LIMIT 100")
                opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino)
                if seleccion_destino:
                    selected_letra_destino = seleccion_destino.split(" - ")[0]
                    puntos_destino = df_destino.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]
                    porcentaje_destino = st.number_input(f"Peso del complemento de destino para {tabla_destino}", min_value=0.0, max_value=100.0, value=100.0)
                    puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)
                    selecciones_destino.append({'Puesto': descripcion, 'Letra': selected_letra_destino, 'Puntos': puntos_ajustados_destino})

# Calcular y mostrar sueldos
for puesto_id in selected_puestos_ids:
    puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
    sueldo_base = 2000  # Sueldo base
    puntos_especifico_sueldo = sum(item['Puntos'] for item in selecciones_especificos if item['Puesto'] == puesto_nombre)
    puntos_valoracion = sum(item['Puntos'] for item in selecciones_destino if item['Puesto'] == puesto_nombre)
    sueldo_total_puesto = sueldo_base + puntos_especifico_sueldo + puntos_valoracion
    st.write(f"Sueldo para el puesto {puesto_nombre}: {sueldo_total_puesto:.2f} euros")
