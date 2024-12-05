import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="APP Escenarios por proyecto ", page_icon="🤯")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula los Salarios Por Proyecto!")

# HTML personalizado para el encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 10px;
        }
        h1, h2 {
            font-family: 'Arial', sans-serif;
            font-size: 17pt;
            text-align: left;
            color: #333333;
        }
        h3 {
            font-family: 'Arial', sans-serif;
            font-size: 14pt;
            text-align: center;
            color: #333333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #2596be;
            color: white;
        }
        td {
            background-color: #f9f9f9;
        }
    </style>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)

# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM ate-rrhh-2024.Ate_kaibot_2024.proyecto
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener complementos específicos de cada proyecto
def get_complementos_especificos(id_proyecto):
    query = f"""
        SELECT complemento_especifico, porcentaje_importancia
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_especifico_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'complemento_especifico': row.complemento_especifico, 'porcentaje_importancia': row.porcentaje_importancia} for row in results]

# Función para obtener complementos de destino
def get_complementos_destino(id_proyecto):
    query = f"""
        SELECT complemento_destino, porcentaje_importancia
        FROM `ate-rrhh-2024.Ate_kaibot_2024.complemento_destino_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'complemento_destino': row.complemento_destino, 'porcentaje_importancia': row.porcentaje_importancia} for row in results]
# Función para obtener y mostrar el contenido de una tabla
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}`"
    query_job = client.query(query)
    results = query_job.result()
    # Convertir a un DataFrame para mostrarlo en Streamlit
    return pd.DataFrame([dict(row) for row in results])


# Función para mostrar complementos con porcentaje_importancia editable

# Función para mostrar complementos con porcentaje_importancia editable

# Función para mostrar complementos con porcentaje_importancia editable

# Función para determinar el orden de letras basado en la categoría seleccionada
def ordenar_letras(categoria, df_tabla):
    # Filtramos las letras por las condiciones de la categoría
    if categoria == 'a1':
        # Ordenar de menor a mayor según la letra, y seleccionar la más alta (letra más grande)
        # Ordenar de mayor a menor según la letra, usando pd.Categorical para asegurar el orden alfabético
        letras_ordenadas = pd.Categorical(df_tabla['letra'], categories=[chr(i) for i in range(65, 91)], ordered=True)
        letras_ordenadas = sorted(df_tabla['letra'].unique(), key=lambda x: letras_ordenadas.categories.get_loc(x), reverse=True)
    
    elif categoria == 'a2':
        letras_ordenadas = ['E']  # Solo 'e' para esta categoría
    
    elif categoria == 'b':
        letras_ordenadas = ['E']  # Solo 'e' para esta categoría
    
    elif categoria == 'c1':
        letras_ordenadas = ['D']  # Solo 'd' para esta categoría
    
    elif categoria == 'c2':
        letras_ordenadas = ['C']  # Solo 'c' para esta categoría
    
    elif categoria == 'ap/e':
        # Ordenar por letra de menor a mayor
        letras_ordenadas = sorted(df_tabla['letra'].unique())  # Ordenamos de menor a mayor
    
    return letras_ordenadas


# Función para mostrar complementos con porcentaje_importancia editable
def mostrar_complementos_editables(df, tabla_nombre, categoria_seleccionada):
    st.write(f"### Descripción de la tabla: {tabla_nombre}")
    st.write(f"Esta tabla contiene los datos de los complementos asociados a la tabla `{tabla_nombre}` con su respectivo porcentaje de importancia.")
    
    for index, row in df.iterrows():
        # Creamos dos columnas para la interfaz
        col1, col2 = st.columns([3, 1])  # 75% para el selectbox, 25% para el inputbox

        # Columna 1: Mostrar el nombre de complemento y porcentaje de importancia
        with col1:
            # Mostrar el nombre de complemento y porcentaje de importancia
            st.write(f"**{row['complemento_especifico' if 'complemento_especifico' in row else 'complemento_destino']}**")
            st.write(f"Porcentaje de importancia: {row['porcentaje_importancia']}%")
            
            # Mostrar el contenido de la tabla específica o de destino
            nombre_tabla = row['complemento_especifico' if 'complemento_especifico' in row else 'complemento_destino']
            try:
                df_tabla = obtener_datos_tabla(nombre_tabla)  # Obtenemos el contenido de la tabla
                st.write(f"Contenido de la tabla `{nombre_tabla}`:")

                if not df_tabla.empty:
                    # Filtramos las columnas para mostrar solo "letra" y "descripcion"
                    if 'letra' in df_tabla.columns and 'descripcion' in df_tabla.columns:
                        # Ordenamos las letras según la categoría seleccionada
                        letras_ordenadas = ordenar_letras(categoria_seleccionada, df_tabla)

                        # Filtramos las opciones de acuerdo con las letras ordenadas
                        opciones = df_tabla[df_tabla['letra'].isin(letras_ordenadas)][['letra', 'descripcion']].drop_duplicates()

                        # Mostrar el selectbox con las letras ordenadas
                        opcion_seleccionada = st.selectbox(
                            f"Selecciona un registro de la tabla `{nombre_tabla}`:",
                            opciones.apply(lambda x: f"{x['letra']} - {x['descripcion']}", axis=1).values  # Formato del selectbox
                        )

                        # Extraer los detalles del registro seleccionado
                        letra_seleccionada, descripcion_seleccionada = opcion_seleccionada.split(' - ')
                        registro_detalle = df_tabla[(df_tabla['letra'] == letra_seleccionada) & (df_tabla['descripcion'] == descripcion_seleccionada)]
                        st.write("Detalles del registro seleccionado:")
                        st.write(registro_detalle)
                    else:
                        st.write("La tabla no contiene las columnas 'letra' y 'descripcion'.")
                else:
                    st.write(f"No se encontraron registros en la tabla `{nombre_tabla}`.")
            except Exception as e:
                st.error(f"Error al cargar la tabla `{nombre_tabla}`: {e}")

        # Columna 2: InputBox para modificar el porcentaje
        with col2:
            nuevo_porcentaje = st.number_input(
                f"Modificar porcentaje para {row['complemento_especifico' if 'complemento_especifico' in row else 'complemento_destino']}",
                min_value=0.0, max_value=100.0, value=row['porcentaje_importancia'], step=0.1
            )
            # Aquí puedes agregar cualquier lógica que necesites para actualizar la base de datos
            st.button(f"Actualizar {row['complemento_especifico' if 'complemento_especifico' in row else 'complemento_destino']}")

# Mostrar la interfaz principal
def mostrar_interfaz():
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres)

    categorias = ['ap/e', 'a1', 'a2', 'b', 'c1', 'c2']
    categoria_seleccionada = st.sidebar.selectbox("Seleccione una Categoría:", categorias)

    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    st.markdown("""
    **Importante**: Los porcentajes para los complementos deben sumar **100%**.
    """)

    if id_proyecto_seleccionado:
        # Obtener complementos específicos con porcentaje de importancia
        complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
        if complementos_especificos:
            st.write("### Factores Específicos del Proyecto")
            df_complementos_especificos = pd.DataFrame(complementos_especificos)
            mostrar_complementos_editables(df_complementos_especificos, "complemento_especifico_x_proyecto", categoria_seleccionada)
        else:
            st.write("No se encontraron complementos específicos.")

        # Obtener complementos de destino con porcentaje de importancia
        complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
        if complementos_destino:
            st.write("### Factores de Destino del Proyecto")
            df_complementos_destino = pd.DataFrame(complementos_destino)
            mostrar_complementos_editables(df_complementos_destino, "complemento_destino_x_proyecto", categoria_seleccionada)
        else:
            st.write("No se encontraron complementos de destino.")

mostrar_interfaz()
