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


import pandas as pd

def ordenar_letras(categoria, df_tabla):
    # Asegurarnos de que la columna 'letra' esté en mayúsculas
    df_tabla['letra'] = df_tabla['letra'].str.upper()
    
    # Filtramos y ordenamos las letras según la categoría
    if categoria == 'a1':
        # Ordenar de mayor a menor (A-Z) con la letra más alta primero
        letras_ordenadas = sorted(df_tabla['letra'].unique(), reverse=True)  # De Z a A
    
    elif categoria == 'a2':
        letras_ordenadas = ['E']  # Solo 'E' para esta categoría
    
    elif categoria == 'b':
        letras_ordenadas = ['E']  # Solo 'E' para esta categoría
    
    elif categoria == 'c1':
        letras_ordenadas = ['D']  # Solo 'D' para esta categoría
    
    elif categoria == 'c2':
        letras_ordenadas = ['C']  # Solo 'C' para esta categoría
    
    elif categoria == 'ap/e':
        # Ordenar de menor a mayor (A-Z) con la letra más baja primero
        letras_ordenadas = sorted(df_tabla['letra'].unique())  # De A a Z
    
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


# Consulta para obtener las categorías de sueldo
query_categorias_sueldo = """
    SELECT nombre_categoria, sueldo
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_categoria_sueldo_por_ano`
"""

# Ejecutar la consulta para obtener las categorías de sueldo
query_job_categorias_sueldo = client.query(query_categorias_sueldo)
results_categorias_sueldo = query_job_categorias_sueldo.result()
df_categorias_sueldo = pd.DataFrame(data=[row.values() for row in results_categorias_sueldo], columns=[field.name for field in results_categorias_sueldo.schema])

# Convertir el DataFrame de categorías de sueldo en un diccionario para fácil acceso
categorias_sueldo_dict = df_categorias_sueldo.set_index('nombre_categoria')['sueldo'].to_dict()

# Mostrar el dataframe de categorías de sueldo
st.dataframe(df_categorias_sueldo)

# Almacenar los sueldos seleccionados por categoría
sueldo_categoria_puesto = {}

# Generar los selectboxes para elegir la categoría de sueldo
st.markdown("<h2>Selecciona la Categoría de Sueldo</h2>", unsafe_allow_html=True)
categoria_seleccionada = st.selectbox(
    "Seleccione la categoría de sueldo",
    list(categorias_sueldo_dict.keys())
)

# Obtener el sueldo de la categoría seleccionada
sueldo = categorias_sueldo_dict[categoria_seleccionada]
st.write(f"Sueldo base: {sueldo} euros")

# Mensaje markdown para explicar la regla de tres
st.markdown("<h2>Valoración para regla de 3 para tabla de complemento específico por Año (Variable) son 100 puntos -> 34.388,95 euros</h2>", unsafe_allow_html=True)
valor_base = 34388.95  # euros

# Input para que el usuario introduzca el valor de puntos específicos
total_especifico = st.number_input('Introduce el número de puntos específicos del proyecto:',
                                   min_value=1.0,
                                   value=100.0,
                                   step=0.01)

# Calcular el valor de los puntos específicos del proyecto
valor_punto_especifico_proyecto = (total_especifico * valor_base) / 100
st.write(f"Valor de los puntos específicos del proyecto: {valor_punto_especifico_proyecto:.2f} euros")

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

# Calcular el complemento específico con el porcentaje de disponibilidad especial
sueldo_bruto_con_complementos = sueldo + valor_punto_especifico_proyecto
if porcentaje_disponibilidad > 0:
    incremento_disponibilidad = sueldo_bruto_con_complementos * (porcentaje_disponibilidad / 100)
    sueldo_total_con_disponibilidad = sueldo_bruto_con_complementos + incremento_disponibilidad
    st.write(f"Con la modalidad '{modalidad_disponibilidad}' ({porcentaje_disponibilidad}%), el sueldo total ajustado es: {sueldo_total_con_disponibilidad:.2f} euros")
else:
    st.write(f"Sueldo total sin disponibilidad especial: {sueldo_bruto_con_complementos:.2f} euros")

# Mostrar la referencia a la última publicación oficial
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.markdown("Última publicación oficial: BOPV del 27 de febrero del 2024")

# Formulario de envío
with st.form('addition'):
    submit = st.form_submit_button('Confirmar Valoración preliminar')

if submit:
    try:
        # Consulta para obtener el último ID de proyecto
        query_max_id = """
        SELECT MAX(Id_valoracion_preliminar) FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_preliminar_por_proyecto`
        """
        query_job_max_id = client.query(query_max_id)
        max_id_result = query_job_max_id.result()

        max_id = 0
        for row in max_id_result:
            max_id = row[0]

        # Incrementar el máximo ID en 1 para obtener el nuevo ID de proyecto
        new_id_valoracion_preliminar = max_id + 1 if max_id is not None else 1

        # Consulta para insertar datos básicos en BigQuery
        query_kai_insert = f"""
            INSERT INTO `ate-rrhh-2024.Ate_kaibot_2024.valoracion_preliminar_por_proyecto`
            (Id_valoracion_preliminar, id_proyecto, puntos_destino, puntos_especifico, sueldo_base_puesto, importe_destino,importe_especifico,bruto_anual_puesto) 
            VALUES 
            ({new_id_valoracion_preliminar},{id_proyecto_seleccionado}, {total_especifico}, {total_especifico}, {sueldo},{valor_punto_especifico_proyecto},{valor_punto_especifico_proyecto},{sueldo_total_con_disponibilidad})
        """
        query_job_kai_insert = client.query(query_kai_insert)
        query_job_kai_insert.result()  # Asegurarse de que la consulta se complete
        # Mensaje de éxito
        st.success("Registro insertado correctamente")

    except Exception as e:
        st.error(f"Error al insertar el registro: {e}")

